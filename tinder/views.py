from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile


def home(request):
    user = None
    user_id = request.session.get('user_id')
    if user_id:
        user = Profile.objects.get(id=user_id)

    return render(request, 'home.html', {
        'user': user
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            messages.error(request, 'Користувача не існує')
            return redirect('auth')

        if not user.check_password(password):
            messages.error(request, 'Невірний пароль')
            return redirect('auth')

        request.session['user_id'] = user.id

        
        return redirect('home')

    return render(request, 'auth.html')


def register(request):
    step = int(request.GET.get('step', 1))

    if request.method == 'POST':
        step = int(request.POST.get('step'))

        data = request.session.get('reg_data', {})
        profile_id = request.session.get('reg_profile_id')
        profile = Profile.objects.filter(id=profile_id).first() if profile_id else None

        if step == 1:
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            # Перевірка чи існує користувач
            if Profile.objects.filter(username=username).exists():
                messages.error(request, 'Користувач з таким логіном вже існує')
                return redirect('register')

            day = request.POST.get('birth_day')
            month = request.POST.get('birth_month')
            year = request.POST.get('birth_year')

            birth_date = None
            if day and month and year:
                birth_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Створюємо профіль
            profile = Profile.objects.create(
                username=username,
                name=name,
                birth_date=birth_date,
                gender=request.POST.get('gender'),
                city=request.POST.get('city')
            )
            profile.set_password(password)
            profile.save()

            request.session['reg_profile_id'] = profile.id

        # КРОК 2 (фото)
        elif step == 2:
            if not profile:
                messages.error(request, 'Сесія реєстрації втрачена. Заповніть форму ще раз.')
                return redirect('register')

            photo = request.FILES.get('photo')
            if photo:
                profile.photo = photo
                profile.save()

        # КРОК 3 (про себе)
        elif step == 3:
            if not profile:
                messages.error(request, 'Сесія реєстрації втрачена. Заповніть форму ще раз.')
                return redirect('register')

            profile.bio = request.POST.get('bio')
            profile.interests = request.POST.get('interests')
            profile.lifestyle = request.POST.get('lifestyle')
            profile.save()

        # КРОК 4 (що шукає)
        elif step == 4:
            if not profile:
                messages.error(request, 'Сесія реєстрації втрачена. Заповніть форму ще раз.')
                return redirect('register')

            profile.looking_for = request.POST.get('looking_for')
            profile.values = request.POST.get('values')
            profile.save()

            # Очищаємо сесію
            request.session.pop('reg_data', None)
            request.session.pop('reg_profile_id', None)
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

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('auth')

    user = Profile.objects.get(id=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.gender = request.POST.get('gender')
        user.city = request.POST.get('city')
        user.bio = request.POST.get('bio')
        user.interests = request.POST.get('interests')
        user.lifestyle = request.POST.get('lifestyle')
        user.looking_for = request.POST.get('looking_for')
        user.values = request.POST.get('values')

        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')

        user.save()
        return redirect('/profile/')

    return render(request, 'profile.html', {
        'user': user
    })

def logout(request):
    request.session.pop('user_id', None)
    return redirect('home')