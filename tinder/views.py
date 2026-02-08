from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile


def home(request):
    return render(request, 'home.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            messages.error(request, 'Користувача не існує')
            return redirect('auth')

        if user.password != password:
            messages.error(request, 'Невірний пароль')
            return redirect('auth')

        messages.success(request, f'Вітаю, {user.name} 💖')
        return redirect('home')

    return render(request, 'auth.html')


def register(request):
    step = int(request.GET.get('step', 1))

    if request.method == 'POST':
        step = int(request.POST.get('step'))

        data = request.session.get('reg_data', {})

        # КРОК 1
        if step == 1:
            data['name'] = request.POST.get('name')
            data['username'] = request.POST.get('username')
            data['password'] = request.POST.get('password')

            day = request.POST.get('birth_day')
            month = request.POST.get('birth_month')
            year = request.POST.get('birth_year')

            if day and month and year:
                data['birth_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            data['gender'] = request.POST.get('gender')
            data['city'] = request.POST.get('city')

        # КРОК 2 (фото)
        elif step == 2:
            pass

        # КРОК 3 (про себе)
        elif step == 3:
            data['bio'] = request.POST.get('bio')
            data['interests'] = request.POST.get('interests')
            data['lifestyle'] = request.POST.get('lifestyle')

        # КРОК 4 (що шукає)
        elif step == 4:
            data['looking_for'] = request.POST.get('looking_for')
            data['values'] = request.POST.get('values')

            # фінальне створення
            Profile.objects.create(
                username=data['username'],
                name=data['name'],
                password=data['password'],
                birth_date=data.get('birth_date') or None,
                gender=data.get('gender'),
                city=data.get('city'),
                bio=data.get('bio'),
                interests=data.get('interests'),
                lifestyle=data.get('lifestyle'),
                looking_for=data.get('looking_for'),
                values=data.get('values'),
                photo=request.FILES.get('photo')  # додано
            )

            request.session.pop('reg_data', None)
            messages.success(request, 'Реєстрація успішна 💖')
            return redirect('auth')

        request.session['reg_data'] = data
        return redirect(f'/register/?step={step+1}')

    from datetime import date

    current_year = date.today().year
    years = list(range(current_year - 18, current_year - 70, -1))
    days = list(range(1, 32))

    return render(request, 'register.html', {
        'step': step,
        'years': years,
        'days': days
    })
