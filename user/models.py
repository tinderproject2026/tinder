from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True)

    def __str__(self):
        return self.user.username