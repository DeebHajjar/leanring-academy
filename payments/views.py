import stripe
import json
import uuid
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

from .models import Order, Payment
from courses.models import Course, Enrollment

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
@require_POST
def create_checkout_session(request):
    try:
        data = json.loads(request.body)
        course_id = data.get('course_id')
        
        if not course_id:
            return JsonResponse({'error': 'Course ID is required'}, status=400)
        
        course = get_object_or_404(Course, id=course_id)
        
        # Verify that the user has not already purchased the course
        existing_order = Order.objects.filter(
            user=request.user,
            course=course,
            status='completed'
        ).first()
        
        if existing_order:
            return JsonResponse({'error': _('You already own this course')}, status=400)
        
        # Create or retrieve a pending order
        order, created = Order.objects.get_or_create(
            user=request.user,
            course=course,
            status='pending',
            defaults={
                'order_id': str(uuid.uuid4()),
                'amount': course.price,
                'currency': 'USD',
            }
        )
        
        # Create a Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                        'description': course.description[:500] if course.description else '',
                    },
                    'unit_amount': int(course.price * 100),  # Stripe uses cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payments:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payments:payment_cancel')),
            metadata={
                'order_id': order.order_id,
                'course_id': str(course.id),
                'user_id': str(request.user.id),
            }
        )
        
        # Save the payment intent ID
        order.stripe_payment_intent_id = checkout_session.id
        order.save()
        
        return JsonResponse({'checkout_url': checkout_session.url})
        
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request):
    """Payment success page"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            # Verify the payment session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                order_id = session.metadata.get('order_id')
                order = get_object_or_404(Order, order_id=order_id)
                
                # Update order status
                if order.status == 'pending':
                    order.status = 'completed'
                    order.completed_at = timezone.now()
                    order.save()
                    
                    # Create a payment record
                    Payment.objects.get_or_create(
                        order=order,
                        defaults={
                            'stripe_charge_id': session.payment_intent,
                            'amount': order.amount,
                            'currency': order.currency,
                            'status': 'succeeded',
                        }
                    )
                    
                    # Create Enrollment for the student in the course
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=order.user,
                        course=order.course,
                        defaults={
                            'enrolled_at': timezone.now(),
                            'progress': 0,
                            'is_completed': False,
                        }
                    )
                    
                    if created:
                        print(f"Enrollment created for user {order.user.username} in course {order.course.title}")
                    else:
                        print(f"Enrollment already exists for user {order.user.username} in course {order.course.title}")
                
                messages.success(request, _('Payment completed successfully! You now have access to the course.'))
                return render(request, 'payments/success.html', {
                    'order': order,
                    'course': order.course
                })
        
        except Exception as e:
            messages.error(request, _('Error processing payment verification.'))
    
    return render(request, 'payments/success.html')


def payment_cancel(request):
    """Payment cancel page"""
    messages.info(request, _('Payment was cancelled.'))
    return render(request, 'payments/cancel.html')


@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook handler"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    # If webhook secret is empty, skip verification in development
    if not endpoint_secret and settings.DEBUG:
        try:
            import json
            event = json.loads(payload.decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Webhook payload error: {e}")
            return HttpResponse(status=400)
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            print(f"Webhook ValueError: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(f"Webhook SignatureVerificationError: {e}")
            return HttpResponse(status=400)
    
    try:
        # Handle different events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_session_completed(session)
        
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_payment_intent_succeeded(payment_intent)
        
        print(f"Webhook processed successfully: {event['type']}")
        return HttpResponse(status=200)
        
    except Exception as e:
        print(f"Webhook processing error: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(status=500)


def handle_checkout_session_completed(session):
    """Processing completed checkout session"""
    try:
        logger.info(f"Processing checkout session: {session.get('id', 'unknown')}")
        
        # Verify the presence of metadata
        if 'metadata' not in session or not session['metadata']:
            logger.warning("No metadata found in session")
            return
            
        order_id = session['metadata'].get('order_id')
        if not order_id:
            logger.warning("No order_id found in session metadata")
            return
            
        logger.info(f"Looking for order: {order_id}")
        
        try:
            order = Order.objects.get(order_id=order_id)
            logger.info(f"Found order: {order}")
        except Order.DoesNotExist:
            logger.warning(f"Order not found: {order_id}")
            return
        
        if order.status == 'pending':
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            logger.info(f"Order status updated to completed: {order_id}")
            
            # Create a payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'stripe_charge_id': session.get('payment_intent', ''),
                    'amount': order.amount,
                    'currency': order.currency,
                    'status': 'succeeded',
                }
            )
            
            if created:
                logger.info(f"Payment record created: {payment.id}")
            else:
                logger.info(f"Payment record already exists: {payment.id}")
            
            # Create Enrollment for the student in the course
            enrollment, enrollment_created = Enrollment.objects.get_or_create(
                student=order.user,
                course=order.course,
                defaults={
                    'enrolled_at': timezone.now(),
                    'progress': 0,
                    'is_completed': False,
                }
            )
            
            if enrollment_created:
                logger.info(f"Enrollment created for user {order.user.username} in course {order.course.title}")
            else:
                logger.info(f"Enrollment already exists for user {order.user.username} in course {order.course.title}")
        else:
            logger.info(f"Order already processed: {order_id} (status: {order.status})")
            
    except Exception as e:
        logger.error(f"Error in handle_checkout_session_completed: {e}")
        import traceback
        traceback.print_exc()


def handle_payment_intent_succeeded(payment_intent):
    """Processing successful payment intent"""
    # Add additional logic here
    pass


@method_decorator(login_required, name='dispatch')
class OrderHistoryView(ListView):
    """Display order history for the user"""
    model = Order
    template_name = 'payments/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).select_related('course').order_by('-created_at')
