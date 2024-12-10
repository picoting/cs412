"""
Ting Liu
tinglliu@bu.edu
django forms
"""

from django import forms
from .models import Profile, Service, Order, Review


class CreateProfileForm(forms.ModelForm):
    """
    form for creating a new profile (1-to-1 with user)
    gets email, is_seller, bio, and profile pic for the profile
    """
    #username = forms.CharField(label="Username", required=True)
    email = forms.EmailField(label="Email Address", required=True)
    is_seller = forms.BooleanField(label="Are you a seller?", required=False)

    class Meta:
        model = Profile
        fields = ['email', 'is_seller', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Tell us a little about yourself...'
            }),
        }


class CreateServiceForm(forms.ModelForm):
    """
    form for creating a new service
    for seller to input title, description, price (per unit), and category from a list`
    """
    title = forms.CharField(label="Service Title", required=True)
    description = forms.CharField(widget=forms.Textarea, label="Service Description", required=True)
    price = forms.DecimalField(label="Price", required=True)

    class Meta:
        model = Service
        fields = ['title', 'description', 'price', 'category']


class UpdateUserProfileForm(forms.ModelForm):
    """
    update profile form, can modify email/seller status
    """
    class Meta:
        model = Profile
        fields = ['email', 'is_seller']

    def __init__(self, *args, **kwargs):
        super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = "Email Address"
        self.fields['is_seller'].label = "Are you a seller?"
        if 'email' in self.fields:
            self.fields['email'].required = True


class CreateOrderForm(forms.ModelForm):
    """
    form for buyer to place order (quantity/order notes)
    """
    class Meta:
        model = Order
        fields = ['quantity', 'notes']  # buyers can only set these fields
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class OrderUpdateForm(forms.ModelForm):
    """
    form to update an order status (for seller)
    """
    class Meta:
        model = Order
        fields = ['status']


class CreateReviewForm(forms.ModelForm):
    """
    form to create a review (either from seller to buyer or buyer to seller)
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Leave a comment...'}),
        }
        labels = {
            'rating': 'Rating (out of 5)',
            'comment': 'Comment (optional)',
        }