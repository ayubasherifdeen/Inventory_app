"""Defines urls for users"""
from django.urls import path, include
from . import views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

app_name='users'
urlpatterns=[
    #Include default auth urls
    path('', include('django.contrib.auth.urls')),
        #Registration page
    path('register/', views.register, name='register'),
        #Reset form
    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
        #Reset link
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
        #New password form
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
        #Reset completion confirmation
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]