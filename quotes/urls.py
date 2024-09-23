# quotes/urls.py
from django.urls import path, include
from django.conf import settings
from . import views

# all of the URLs that are part of this app
urlpatterns = [
    path(r'', views.home, name="home"),
    path(r'about', views.about, name="about"),
    path('quotes/', include('quotes.urls')),
    
]