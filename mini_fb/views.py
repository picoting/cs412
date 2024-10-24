from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from .models import *
from .forms import *

from django.shortcuts import get_object_or_404

from .forms import CreateProfileForm
from django.urls import reverse

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'



class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'



class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    # redirect after submission
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        #profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        #form.instance.profile = profile

        profile = Profile.objects.get(pk=self.kwargs['pk'])
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
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    

class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    # dedirect to profile page after updating
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})


class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    #redirect to profile after deleting status
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    fields = ['message']  # you can only update the text
    template_name = 'mini_fb/update_status_form.html'

     #redirect to profile after updating status
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})