from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to="profile_images", default="blank-profile-pic.jpeg")
    location = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    is_blind = models.BooleanField(default=False)
    is_mute = models.BooleanField(default=False)
    is_deaf = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user
    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class ChatLog(models.Model):
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_chats')
    chat_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_chats')
    chat_text = models.TextField(blank=True, null=True)
    chat_audio = models.FileField(upload_to='chat_audios/', blank=True, null=True)
    transcript = models.TextField(blank=True, null=True)
    emotion_class = models.TextField(max_length=100, blank=True, null=True)
    emotional_audio = models.FileField(upload_to='emotional_audios/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat_from.username} to {self.chat_to.username} - {self.created_at}"
