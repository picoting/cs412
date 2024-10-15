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