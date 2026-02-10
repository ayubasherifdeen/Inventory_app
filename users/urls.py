"""Defines urls for users"""
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name='users'
urlpatterns=[
    #Include default auth urls
    path('', include('django.contrib.auth.urls')),
        #Registration page
    path('register/', views.register, name='register'),
    
]