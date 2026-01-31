from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile

from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile

def home(request):
    if request.method == 'POST' and request.POST.get('form_type') == 'register':
        username = request.POST.get('username')

        # 🔍 перевірка на існування логіну
        if Profile.objects.filter(username=username).exists():
            messages.error(request, 'Користувач з таким логіном вже існує 😕')
            return redirect('home')

        Profile.objects.create(
            username=username,
            name=request.POST.get('name'),
            password=request.POST.get('password'),
            birth_date=request.POST.get('birth_date') or None,
            gender=request.POST.get('gender'),
            city=request.POST.get('city'),
            bio=request.POST.get('bio'),
            photo=request.FILES.get('photo')
        )

        messages.success(request, 'Реєстрація успішна 💖')
        return redirect('home')

    return render(request, 'home.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            messages.error(request, 'Користувача з таким логіном не існує')
            return redirect('home')

        if user.password != password:
            messages.error(request, 'Невірний пароль')
            return redirect('home')

        messages.success(request, f'Вітаю, {user.name} 💖')
        return redirect('home')
