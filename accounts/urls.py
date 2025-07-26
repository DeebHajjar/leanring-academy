from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.my_profile_redirect, name='my_profile_redirect'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/edit/<str:username>/', views.profile_edit_view, name='profile_edit'),
    path('set-language/', views.set_language_and_save, name='set_language_and_save'),
]

