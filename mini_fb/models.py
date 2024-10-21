from django.db import models
from django.utils import timezone
from django.urls import reverse

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
    #new StatusMessage model that stores the message, timestamp, and relates it to a user profile.
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.profile.first_name} at {self.timestamp}: {self.message}"

    def get_images(self):
        # return all the images related to the status message
        return Image.objects.filter(status_message=self)


class Image(models.Model):
    #new image model that stores each image, relates it to a StatusMessage, and timestamp
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='status_images/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.status_message.message} uploaded on {self.timestamp}"