from django.db import models
from django.contrib.auth.models import AbstractUser
import os

def avatar_upload_path(instance, filename):
    return os.path.join('avatars', instance.username, filename)

class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True, help_text="User avatar")

    def __str__(self):
        return self.username