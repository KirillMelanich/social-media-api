import os
import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify


def profile_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}.{extension}"
    return os.path.join("uploads/profile_picture/", filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to=profile_picture_file_path, blank=True, null=True)
    username = models.CharField(max_length=63, unique=True)
    bio = models.TextField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_followers", blank=True)
    followings = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_followings", blank=True)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post")
    content = models.TextField()
    hashtags = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
