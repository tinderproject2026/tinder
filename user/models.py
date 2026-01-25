from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)

    def __str__(self):
        return self.username