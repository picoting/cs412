from django import forms
from .models import Profile
from .models import StatusMessage

class CreateProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    city = forms.CharField(label="City", required=True)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email', 'profile_image_url']

class CreateStatusMessageForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, label="Status Message", required=True)

    class Meta:
        model = StatusMessage
        fields = ['message']


class UpdateProfileForm(forms.ModelForm):
    #new form to update an existing profile
    class Meta:
        #do not include updating name
        model = Profile
        fields = ['city', 'email', 'profile_image_url']
        

    # update meta info
    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields['city'].label = "City"
        self.fields['email'].label = "Email Address"
        self.fields['profile_image'].label = "Profile Image URL"