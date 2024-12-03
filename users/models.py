from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.URLField(max_length=500, blank=True, null=True, help_text="S3 image URl")

    def __str__(self):
        return self.username