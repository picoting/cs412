from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# Service model
class Service(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"{self.title} by {self.seller.username}"

# Order model
class Order(models.Model):
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
        # Automatically calculate total price
        self.total_price = self.service.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.buyer.username} for {self.service.title}"

# Review model
class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # ensure rating is 1-5
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"
