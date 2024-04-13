from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('register/', views.register_page, name="register"),
    path('logout/', views.logout_page, name="logout"),
    path('activate/<email_token>/', views.activate_email, name="activate"),
    path('cart/', views.cart_page, name="cart"),
    path('add-to-cart/<uid>/', views.add_to_cart, name="add_to_cart"),
    path('remove-cart/<cart_item_uid>', views.remove_cart, name="remove_cart"),
    path('remove-coupon/<cart_id>/', views.remove_coupon, name="remove_coupon"),
    path('success/', views.success, name="success"),
    path('checkout/', views.checkout, name="checkout"),
]