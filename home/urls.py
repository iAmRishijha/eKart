from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.search_product, name="search_product"),
    path('category/<slug>', views.search_category, name="search_category"),
    
]