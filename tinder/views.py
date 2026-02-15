from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile, Like, Match
from datetime import date
import random
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

def likes(request):
    if not request.session.get("user_id"):
        return redirect("auth")

    me = Profile.objects.get(id=request.session["user_id"])

    profiles = Profile.objects.filter(
        sent_likes__to_user=me
    ).exclude(
        received_likes__from_user=me
    )

    return render(request, "likes.html", {
    "profiles": profiles,
    "current_user": me
})

def sympathy(request):
    user = get_current_user(request)

    matches = Match.objects.filter(user1=user) | Match.objects.filter(user2=user)

    profiles = []
    for m in matches:
        if m.user1 == user:
            profiles.append(m.user2)
        else:
            profiles.append(m.user1)

    return render(request, "sympathy.html", {
        "profiles": profiles,
        "current_user": user   # ← ВАЖЛИВО
    })



def like_user(request, user_id):
    me = Profile.objects.get(id=request.session["user_id"])
    target = Profile.objects.get(id=user_id)

    Like.objects.get_or_create(from_user=me, to_user=target)

    return redirect("dating")


def dislike_user(request, user_id):
    return redirect("dating")


def accept_like(request, user_id):
    me = Profile.objects.get(id=request.session["user_id"])
    sender = Profile.objects.get(id=user_id)

    # створюємо матч
    Match.objects.get_or_create(user1=me, user2=sender)

    # ❗ ВИДАЛЯЄМО ВСІ ЛАЙКИ МІЖ НИМИ
    Like.objects.filter(from_user=sender, to_user=me).delete()
    Like.objects.filter(from_user=me, to_user=sender).delete()

    return redirect("likes")

def reject_like(request, user_id):
    me = Profile.objects.get(id=request.session["user_id"])
    sender = Profile.objects.get(id=user_id)

    Like.objects.filter(from_user=sender, to_user=me).delete()

    return redirect("likes")


def get_current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return Profile.objects.filter(id=user_id).first()


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('auth')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dating(request):
    if not request.session.get("user_id"):
        return redirect("auth")

    me = Profile.objects.get(id=request.session["user_id"])

    viewed = Like.objects.filter(from_user=me).values_list("to_user", flat=True)

    profiles = Profile.objects.exclude(id=me.id).exclude(id__in=viewed)

    profile = random.choice(list(profiles)) if profiles else None

    return render(request, "dating.html", {
    "profile": profile,
    "current_user": me
})


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

        # ДАТА НАРОДЖЕННЯ
        day = request.POST.get('birth_day')
        month = request.POST.get('birth_month')
        year = request.POST.get('birth_year')
        if day and month and year:
            user.birth_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')

        user.save()
        return redirect('/profile/')

    current_year = date.today().year

    return render(request, 'profile.html', {
        'user': user,
        'days': range(1, 32),
        'years': range(current_year - 18, current_year - 70, -1),
        'months': [
            (1,"Січень"),(2,"Лютий"),(3,"Березень"),(4,"Квітень"),
            (5,"Травень"),(6,"Червень"),(7,"Липень"),(8,"Серпень"),
            (9,"Вересень"),(10,"Жовтень"),(11,"Листопад"),(12,"Грудень")
        ]
    })

def logout(request):
    request.session.pop('user_id', None)
    return redirect('home')