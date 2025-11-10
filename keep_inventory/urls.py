"""Defines URL patterns for learning_logs"""
from django.urls import path
from . import views

app_name = 'keep_inventory'

urlpatterns = [
    #Home page
    path('', views.index, name='index'),
    #Sell page
    path('sell/', views.search_products, name='sell'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
   
    
    
]