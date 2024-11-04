from django.db import models
from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles", default=1)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    profile_image_url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_status_messages(self):
        #returns ordered status messages
        return self.status_messages.order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    

    def get_friends(self):
        # get friend relationship
        friends_as_profile1 = Friend.objects.filter(profile1=self)
        friends_as_profile2 = Friend.objects.filter(profile2=self)
        
        # get the profiles in the relationship
        friends = [friend.profile2 for friend in friends_as_profile1] + \
                  [friend.profile1 for friend in friends_as_profile2]

        return friends
        
    
    def add_friend(self, other):
        #create new friend

        if other == self:
            return

        if Friend.objects.filter(profile1=self, profile2=other).exists() or \
           Friend.objects.filter(profile1=other, profile2=self).exists():
            return

        Friend.objects.create(profile1=self, profile2=other)

    def get_friend_suggestions(self):
        # Get all profiles except current profile and existing friends
        friends = self.get_friends()
        all_profiles = Profile.objects.exclude(id=self.id).exclude(id__in=[friend.id for friend in friends])
        return all_profiles

    def get_news_feed(self):
        friends = self.get_friends()
        profiles_to_include = [self] + friends
        # Get all status messages by this profile and its friends
        return StatusMessage.objects.filter(profile__in=profiles_to_include).order_by('-timestamp')


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


class Friend(models.Model):
    #new friend model to hold the relationship between two profiles
    profile1 = models.ForeignKey(Profile, related_name="friendships_as_profile1", on_delete=models.CASCADE)
    profile2 = models.ForeignKey(Profile, related_name="friendships_as_profile2", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"