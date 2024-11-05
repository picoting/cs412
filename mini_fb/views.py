from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic.edit import FormView

from .models import *
from .forms import *

from django.shortcuts import get_object_or_404

from .forms import CreateProfileForm
from django.urls import reverse

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.forms import UserCreationForm

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'



class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Profile, pk=self.kwargs['pk'])
        else:
            return get_object_or_404(Profile, user=self.request.user)



class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    # redirect after submission
    def get_success_url(self):
        return reverse('show_profile_logged_in')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()  # Add UserCreationForm to the context
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        user_form = UserCreationForm(self.request.POST)
        profile_form = self.get_form()

        #check if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            return self.form_invalid(user_form, profile_form)
        
    def form_valid(self, user_form, profile_form):
        user = user_form.save()
        #attach user to profile
        profile_form.instance.user = user
        profile_form.save()

        #log in after registration
        login(self.request, user)
        return super().form_valid(profile_form)

    #handle erros
    def form_invalid(self, user_form, profile_form):
        context = self.get_context_data()
        context['user_form'] = user_form
        context['form'] = profile_form
        return self.render_to_response(context)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

    def form_valid(self, form):
        #profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        #form.instance.profile = profile

        profile = Profile.objects.get(user=self.request.user)
        status_message = form.save(commit=False)
        status_message.profile = profile
        status_message.save() 

        # get all uploaded files
        files = self.request.FILES.getlist('files')

        print(files)

        # create an image object for each file
        for file in files:
            image = Image(status_message=sm, image=file)
            image.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_profile_logged_in')
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    # dedirect to profile page after updating
    def get_success_url(self):
        return reverse('show_profile_logged_in')
    
    def get_queryset(self):
        # only allow the user associated with this profile to update it
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)


class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    #redirect to profile after deleting status
    def get_success_url(self):
        return reverse('show_profile_logged_in')

    def get_object(self):
        return get_object_or_404(StatusMessage, pk=self.kwargs['pk'], profile__user=self.request.user)
    

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    fields = ['message']  # you can only update the text
    template_name = 'mini_fb/update_status_form.html'

     #redirect to profile after updating status
    def get_success_url(self):
        return reverse('show_profile_logged_in')
    
    def get_object(self):
        return get_object_or_404(StatusMessage, pk=self.kwargs['pk'])
    

class CreateFriendView(View):
    #view to create the friend relationship
    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        other = get_object_or_404(Profile, pk=self.kwargs['other_pk'])
        profile.add_friend(other)
        return redirect('show_profile', pk=profile.pk)

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
class ShowFriendSuggestionsView(DetailView):
    #view to show friend suggestions for a profile
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friend_suggestions'] = self.object.get_friend_suggestions()
        return context

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class ShowNewsFeedView(DetailView):
    #view to show news feed
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()
        return context

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)