from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Profile(models.Model):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    bio = models.TextField(null=True, blank=True)

    interests = models.TextField(null=True, blank=True)
    lifestyle = models.TextField(null=True, blank=True)
    looking_for = models.TextField(null=True, blank=True)
    values = models.TextField(null=True, blank=True)

    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
