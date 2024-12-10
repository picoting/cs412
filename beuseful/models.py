"""
Ting Liu
tinglliu@bu.edu
data models for buseful
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator

"""
# Custom Profile model
class Profile(models.Model):
    username = models.CharField(max_length=30, default="johndoeuser")
    email = models.EmailField(unique=True)  # Ensure unique emails
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username
"""

class Profile(models.Model):
    """
    profile model, one-to-one with django user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        null=True,
        validators=[MinLengthValidator(10)], 
        help_text="Write a short bio about yourself (minimum 10 characters)."
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

# Service model
class Service(models.Model):
    """
    service model, has a preset list of possible service categories
    """
    CATEGORY_CHOICES = [
        ('Arts', 'Arts'),
        ('Technology', 'Technology'),
        ('Educational', 'Educational'),
        ('Lifestyle', 'Lifestyle'),
        ('Household', 'Household'),
        ('Business', 'Business'),
        ('Misc', 'Misc.'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Misc')
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"{self.title} by {self.seller.username}"

class Order(models.Model):
    """
    order, contains fields for both the seller/buyer
    preset list of order statuses for the seller to update
    """
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='buyer_orders')
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='seller_orders')
    quantity = models.PositiveIntegerField(default=1)  # Add quantity
    notes = models.TextField(blank=True, null=True)  # Add notes
    date_ordered = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        #calculates the total cost of the order based on quantity
        self.total_price = self.service.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.buyer.username} for {self.service.title}"

class Review(models.Model):
    """
    review model, has 2 way reltionship between reviewer and reviewee
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # ensure rating is 1-5
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"
