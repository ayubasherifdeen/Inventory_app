"""Defines URL patterns for learning_logs"""
from django.urls import path
from . import views

app_name = 'keep_inventory'

urlpatterns = [
    #Home page
    path('', views.index, name='index'),
    #Sell page
    path('sell/', views.search_products, name='sell'),
    #add to cart
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    #remove from cart
    path('remove_from_cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    #checkout the cart
    path('confirm_sale', views.confirm_sale, name='confirm_sale'),
    path('search_transaction_per_date/', views.search_transaction_per_date, name='search_transaction_per_date'),
]