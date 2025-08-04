from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Learning Academy')
    logo = models.ImageField(upload_to='site/', storage=S3Boto3Storage(), blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', storage=S3Boto3Storage(), blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
