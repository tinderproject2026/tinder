import base64
import mimetypes
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
    photo_data = models.TextField(null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_photo_file(self, uploaded_file):
        if not uploaded_file:
            return

        self.photo = uploaded_file
        raw = uploaded_file.read()
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        mime_type = (
            getattr(uploaded_file, "content_type", None)
            or mimetypes.guess_type(getattr(uploaded_file, "name", ""))[0]
            or "application/octet-stream"
        )
        encoded = base64.b64encode(raw).decode("ascii")
        self.photo_data = f"data:{mime_type};base64,{encoded}"

    @property
    def photo_url(self):
        if self.photo_data:
            return self.photo_data
        try:
            if self.photo:
                return self.photo.url
        except Exception:
            return None
        return None

    def __str__(self):
        return self.username
    

# ===== LIKE SYSTEM =====
class Like(models.Model):
    from_user = models.ForeignKey(Profile, related_name="sent_likes", on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name="received_likes", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)   # <--- КЛЮЧ

class Match(models.Model):
    user1 = models.ForeignKey(Profile, related_name="match_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(Profile, related_name="match_user2", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey(Profile, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name="received_messages", on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]
