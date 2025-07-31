from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('lesson/<slug:course_slug>/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('review/<slug:course_slug>/', views.add_review, name='add_review'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-courses/<slug:course_slug>/', views.my_lessons, name='my_lessons'),
    path('comment/<int:lesson_id>/', views.add_comment, name='add_comment'),
    path('update-lesson-progress/<int:lesson_id>/', views.update_lesson_progress, name='update_lesson_progress'),
    path('instructor/<str:instructor_username>/', views.instructor_detail, name='instructor_detail'),
]
