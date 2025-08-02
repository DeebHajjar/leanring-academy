// Stripe Checkout Handler
document.addEventListener('DOMContentLoaded', function() {
    const checkoutButton = document.getElementById('checkout-button');
    const stripePublicKey = document.querySelector('meta[name="stripe-public-key"]');
    
    if (checkoutButton && stripePublicKey) {
        const stripe = Stripe(stripePublicKey.getAttribute('content'));
        
        checkoutButton.addEventListener('click', function() {
            // Disable button to prevent double clicks
            checkoutButton.disabled = true;
            checkoutButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            // Get course ID from data attribute
            const courseId = checkoutButton.getAttribute('data-course-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/payments/create-checkout-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    course_id: parseInt(courseId)
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    // Re-enable button
                    checkoutButton.disabled = false;
                    checkoutButton.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Buy Now';
                } else if (data.checkout_url) {
                    // Redirect to Stripe Checkout
                    window.location.href = data.checkout_url;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
                // Re-enable button
                checkoutButton.disabled = false;
                checkoutButton.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Buy Now';
            });
        });
    }
});
