from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Course, Lesson, Instructor, Review, Comment, Enrollment, LessonProgress

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Instructor)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
# Register your models here.
