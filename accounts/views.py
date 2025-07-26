from django.views.decorators.csrf import csrf_exempt
from django.utils import translation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import User, Profile
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        'user': user,
        'profile': profile,
        'is_owner': request.user == user,
    }
    return render(request, 'account/profile.html', context)


def login_view(request):
    return render(request, 'account/login.html')

def signup_view(request):
    return render(request, 'account/signup.html')

@login_required
def my_profile_redirect(request):
    if request.user.username:
        return redirect('profile', username=request.user.username)
    else:
        return redirect('profile_edit', username=request.user.username or '')


@login_required
def profile_edit_view(request, username):
    user = get_object_or_404(User, username=username)
    # Only the account owner can edit.
    if request.user != user:
        return redirect('profile', username=user.username)
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save()
            if profile.preferred_language:
                translation.activate(profile.preferred_language)
                request.session['django_language'] = profile.preferred_language
            return redirect('profile', username=user.username)
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'account/profile_edit.html', context)


@csrf_exempt
def set_language_and_save(request):
    next_url = request.POST.get('next', '/')
    lang_code = request.POST.get('language')
    if lang_code:
        if request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.preferred_language = lang_code
            profile.save()
        translation.activate(lang_code)
        request.session['django_language'] = lang_code

        import re
        if lang_code == 'ar':
            if not next_url.startswith('/ar/'):
                if next_url == '/':
                    next_url = '/ar/'
                else:
                    next_url = '/ar' + next_url
        else:
            next_url = re.sub(r'^/ar', '', next_url)
            if next_url == '':
                next_url = '/'
    return redirect(next_url)
