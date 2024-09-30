# quotes/urls.py
from django.urls import path, include
from django.conf import settings
from . import views

# all of the URLs that are part of this app
urlpatterns = [
    path(r'main/', views.main, name="main"),
    path(r'restaurant/', views.main, name="restaurant"),
    path(r'order/', views.order, name="order"),
    path(r'confirmation/', views.confirmation, name="confirmation"),   
]