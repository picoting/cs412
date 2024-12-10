from django import forms
from .models import Profile, Service, Order, Review


class CreateProfileForm(forms.ModelForm):
    """
    Form for creating a new User profile.
    """
    #username = forms.CharField(label="Username", required=True)
    email = forms.EmailField(label="Email Address", required=True)
    #password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    is_seller = forms.BooleanField(label="Are you a seller?", required=False)

    class Meta:
        model = Profile
        fields = ['email', 'is_seller']


class CreateServiceForm(forms.ModelForm):
    """
    Form for creating a new Service.
    """
    title = forms.CharField(label="Service Title", required=True)
    description = forms.CharField(widget=forms.Textarea, label="Service Description", required=True)
    price = forms.DecimalField(label="Price", required=True)
    category = forms.CharField(label="Category", required=True)

    class Meta:
        model = Service
        fields = ['title', 'description', 'price', 'category']


class UpdateUserProfileForm(forms.ModelForm):
    """
    Form for updating an existing User's profile.
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
    Form for creating a new Order.
    """
    class Meta:
        model = Order
        fields = ['quantity', 'notes']  # Allow buyers to set only these fields
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
    Form for creating a new Review.
    """
    rating = forms.IntegerField(label="Rating (1-5)", required=True, min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea, label="Comment", required=False)

    class Meta:
        model = Review
        fields = ['rating', 'comment', 'reviewer', 'reviewee', 'order']