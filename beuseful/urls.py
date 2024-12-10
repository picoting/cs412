# quotes/urls.py
from django.urls import path, include
from django.conf import settings
from . import views
from .views import *
from django.contrib.auth import views as auth_views

from django.contrib.auth.views import LoginView, LogoutView



# all of the URLs that are part of this app
urlpatterns = [
    path('', DefaultView.as_view(), name='default'),
    path('profiles/', ProfileListView.as_view(), name='profile_list'),
    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile_form'), 
    path('login/', LoginView.as_view(template_name='beuseful/log_in.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='beuseful/log_out.html'), name='logout'),
    path('create_service/', CreateServiceView.as_view(), name='create_service'),
    path('order/<int:service_id>/place/', place_order, name='place_order'),
    path('orders/manage/', manage_orders, name='manage_orders'),
    path('order/<int:order_id>/update/', update_order_status, name='update_order_status'),
    path('my_orders/', my_orders, name='my_orders'),
]
