from django.shortcuts import render
from .models import SiteSettings

def home(request):
    site_settings = SiteSettings.objects.first()
    return render(request, 'home.html', {'site_settings': site_settings})

