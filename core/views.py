from django.shortcuts import render
from .models import SiteSettings
from courses.models import Course

def home(request):
    site_settings = SiteSettings.objects.first()
    courses = Course.objects.all()
    return render(request, 'home.html', {'site_settings': site_settings, 'courses': courses})

