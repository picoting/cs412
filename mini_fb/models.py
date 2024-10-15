from django.db import models
from django.utils import timezone

class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    profile_image_url = models.URLField(max_length=200)

    def get_status_messages(self):
        #returns ordered status messages
        return self.status_messages.order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})


class StatusMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.profile.first_name} at {self.timestamp}: {self.message}"