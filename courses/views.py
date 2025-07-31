from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from .models import Course, Lesson, Enrollment, Review, Comment, LessonProgress, Instructor
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from django.db.models import Q
from .forms import ReviewForm, CommentForm, CourseSearchForm
from django.shortcuts import redirect


def course_list(request):
    courses = Course.objects.filter(status='published')
    search_form = CourseSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data['query']
        difficulty = search_form.cleaned_data['difficulty']
        min_price = search_form.cleaned_data['min_price']
        max_price = search_form.cleaned_data['max_price']
        
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__user__username__icontains=query)
        )
        
        if difficulty:
            courses = courses.filter(difficulty=difficulty)
        
        if min_price:
            courses = courses.filter(price__gte=min_price)
        
        if max_price:
            courses = courses.filter(price__lte=max_price)
            
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    elif sort_by == 'rating':
        courses = courses.order_by('-rating')
    elif sort_by == 'students':
        courses = courses.order_by('-enrolled_students')
    else:
        courses = courses.order_by('-created_at')
    
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'search_form': search_form,
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(
        request,
        'courses/course_list.html', 
        context
    )


def course_detail(request, slug):
    course = Course.objects.get(slug=slug)
    lessons = course.lessons.all()
    reviews = course.reviews.select_related('student').order_by('-created_at')[:10]
    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews
    }
    return render(
        request,
        'courses/course_detail.html',
        context
    )

def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, status='published')
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Get previous and next lessons
    lessons = list(course.lessons.order_by('order', 'id'))  # تأكد من الترتيب
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), None)
    previous_lesson = lessons[current_index - 1] if current_index is not None and current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index is not None and current_index < len(lessons) - 1 else None
    
    is_enrolled = False
    
    reviews = course.reviews.select_related('student').order_by('-created_at')[:10]
    
    comment_form = CommentForm()
    comments = lesson.comments.filter(parent__isnull=True, is_active=True).order_by('created_at')
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    if not lesson.is_free and not is_enrolled:
        messages.error(request, _('You must enroll in the course to access this lesson.'))
        return redirect('courses:course_detail', slug=course.slug)
    
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            if not lesson.is_free:
                messages.error(request, _('You are not enrolled in this course.'))
    
    review_form = ReviewForm()
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(course=course, student=request.user)
        except Review.DoesNotExist:
            messages.error(request, _('You are not enrolled in this course.'))
    
    context = {
        'lesson': lesson,
        'course': course,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'review_form': review_form,
        'user_review': user_review,
        'comment_form': comment_form,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'comments': comments,
    }
    return render(
        request,
        'courses/lesson_detail.html',
        context
    )

def add_review(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, _('You must enroll in the course to add a review.'))
        return redirect('courses:course_detail', slug=course.slug)
    
    if Review.objects.filter(course=course, student=request.user).exists():
        messages.warning(request, _('You have already reviewed this course.'))
        return redirect('courses:course_detail', slug=course.slug)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.course = course
        review.student = request.user
        review.save()
        
        # Update course rating and total reviews
        avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg']
        course.rating = round(avg_rating, 2) if avg_rating else 0
        course.total_reviews = course.reviews.count()
        course.save()
        
        messages.success(request, _('Review added successfully!'))
    else:
        messages.error(request, _('Please correct the errors in your review.'))
    
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course__instructor').order_by('-enrolled_at')
    
    paginator = Paginator(enrollments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'courses/my_courses.html', context)


@login_required
def my_lessons(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    # Check if the user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, _('You must enroll in this course to access its lessons.'))
        return redirect('courses:course_detail', slug=course.slug)
    
    lessons = course.lessons.all()
    # Get the user's enrollments
    enrollment = Enrollment.objects.get(student=request.user, course=course)
    
    # Get the user's lesson progress
    lesson_progress_map = {
        lp.lesson_id: lp for lp in LessonProgress.objects.filter(enrollment=enrollment, lesson__in=lessons)
    }
    for lesson in lessons:
        lesson.lesson_progress = lesson_progress_map.get(lesson.id)
    
    paginator = Paginator(lessons, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'course': course,
        'lessons': lessons,
    }
    
    return render(request, 'courses/my_lessons.html', context)


@login_required
@require_POST
def add_comment(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    comment = Comment()
    
    # Check if the user is enrolled in the course or if the lesson is free
    if not lesson.is_free:
        if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
            messages.error(request, _('You must be enrolled to comment on this lesson.'))
            return redirect('courses:lesson_detail', 
                          course_slug=lesson.course.slug, lesson_id=lesson.id)
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment.content = form.cleaned_data['content']
        comment.lesson = lesson
        comment.user = request.user
        
        # Check if it's a reply comment
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, id=parent_id)
        
        comment.save()
        messages.success(request, _('Comment added successfully!'))
    else:
        messages.error(request, _('Please correct the errors in your comment.'))
    
    return redirect('courses:lesson_detail', 
                   course_slug=lesson.course.slug, lesson_id=lesson.id)


@login_required
@require_POST
def update_lesson_progress(request, lesson_id):
    """Update lesson progress via AJAX"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.course)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    watched_duration = int(request.POST.get('watched_duration', 0))
    lesson_progress.watched_duration = watched_duration
    
    # If watched 90% of the lesson, consider it completed
    if watched_duration >= (lesson.duration_minutes * 60 * 0.9):
        lesson_progress.is_completed = True
        if not lesson_progress.completed_at:
            from django.utils import timezone
            lesson_progress.completed_at = timezone.now()
    
    lesson_progress.save()
    
    # Update course progress
    total_lessons = enrollment.course.lessons.count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        is_completed=True
    ).count()
    
    enrollment.progress = int((completed_lessons / total_lessons) * 100)
    if enrollment.progress == 100 and not enrollment.is_completed:
        enrollment.is_completed = True
        from django.utils import timezone
        enrollment.completed_at = timezone.now()
    
    enrollment.save()
    
    return JsonResponse({
        'success': True,
        'progress': enrollment.progress,
        'lesson_completed': lesson_progress.is_completed
    })

def instructor_detail(request, instructor_username):
    instructor = get_object_or_404(Instructor, user__username=instructor_username)
    courses = Course.objects.filter(
        instructor=instructor,
        status='published'
    ).order_by('-created_at')
    
    # update total courses
    total_courses = courses.values('instructor').count()
    
    # save total courses    
    instructor.total_courses = total_courses
    instructor.save()
    
    context = {


        'instructor': instructor,
        'courses': courses,
    }
    
    return render(request, 'courses/instructor_detail.html', context)

