from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import SiteSettings
from . import translation


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin):
    list_display = ('site_name', 'logo', 'favicon', 'contact_email', 'contact_phone', 'address', 'facebook', 'twitter', 'instagram', 'youtube')
