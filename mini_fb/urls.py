# quotes/urls.py
from django.urls import path, include
from django.conf import settings
from . import views
from .views import *
from django.contrib.auth import views as auth_views



# all of the URLs that are part of this app
urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>/', views.ShowProfilePageView.as_view(), name='show_profile'),
    path('profile/', views.ShowProfilePageView.as_view(), name='show_profile_logged_in'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('status/create_status/', CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('status/<int:pk>/delete/', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('status/<int:pk>/update/', UpdateStatusMessageView.as_view(), name='update_status'),
    path('profile/add_friend/<int:other_pk>/', views.CreateFriendView.as_view(), name='add_friend'),
    path('profile/friend_suggestions/', views.ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/news_feed/', views.ShowNewsFeedView.as_view(), name='news_feed'),
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout'),

]