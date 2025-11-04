"""Defines URL patterns for learning_logs"""
from django.urls import path
from . import views

app_name = 'keep_inventory'

urlpatterns = [
    #Home page
    path('', views.index, name='index'),
    path('products/', views.search_products, name='sell'),
    #Registration page
    path('register/', views.regsiter, name='register'),
]