from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Like

def like_user(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    Like.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )
    return redirect('/')
