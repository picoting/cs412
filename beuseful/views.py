from django.shortcuts import render, redirect

from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import *
from .forms import *

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.contrib.auth.views import LoginView, LogoutView

class ProfileListView(ListView):
    model = Profile
    template_name = 'beuseful/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        # Exclude profiles with empty or null usernames
        return Profile.objects.exclude(username='')


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "beuseful/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the logged-in user is viewing their own profile
        context['is_own_profile'] = self.request.user.is_authenticated and self.get_object().username == self.request.user.username
        return context



class CreateServiceView(CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'beuseful/create_service.html'

    def form_valid(self, form):
        service = form.save(commit=False)
        service.seller = self.request.user  # Assuming logged-in user is the seller
        service.save()
        return super().form_valid(form)

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'beuseful/create_profile_form.html'

    def get_success_url(self):
        # Redirect to the default beuseful page (profile list)
        return reverse('profile_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()  # Add UserCreationForm to the context
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        user_form = UserCreationForm(self.request.POST)
        profile_form = self.get_form()

        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            return self.form_invalid(user_form, profile_form)

    def form_valid(self, user_form, profile_form):
        user = user_form.save()
        profile_form.instance.user = user
        profile_form.save()
        login(self.request, user)  # Log the user in after profile creation
        return super().form_valid(profile_form)

    def form_invalid(self, user_form, profile_form):
        context = self.get_context_data()
        context['user_form'] = user_form
        context['form'] = profile_form
        return self.render_to_response(context)

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post'] 


class DefaultView(TemplateView):
    template_name = 'beuseful/default.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile_list')  # Redirect logged-in users to the profile list
        return super().get(request, *args, **kwargs)