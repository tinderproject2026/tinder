from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import Profile, Like, Match, ChatMessage
from datetime import date
import random
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_zodiac_sign(birth_date):
    if not birth_date:
        return None

    month = birth_date.month
    day = birth_date.day

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Овен"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Телець"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Близнюки"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Рак"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Діва"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Терези"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Скорпіон"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Стрілець"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Козоріг"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Водолій"
    return "Риби"

def get_opposite_gender_filter(gender_value):
    if not gender_value:
        return None

    g = str(gender_value).strip().lower()

    male_values = {"чоловік", "чоловiк", "male", "man", "m"}
    female_values = {"жінка", "жiнка", "female", "woman", "f"}

    if g in male_values:
        return Q(gender__iexact="Жінка") | Q(gender__iexact="Жiнка") | Q(gender__iexact="female") | Q(gender__iexact="woman") | Q(gender__iexact="f")

    if g in female_values:
        return Q(gender__iexact="Чоловік") | Q(gender__iexact="Чоловiк") | Q(gender__iexact="male") | Q(gender__iexact="man") | Q(gender__iexact="m")

    return None

def get_match_partners(user):
    matches = (
        Match.objects
        .filter(Q(user1=user) | Q(user2=user))
        .select_related("user1", "user2")
        .order_by("-created")
    )

    partners = []
    seen_partner_ids = set()
    for match in matches:
        partner = match.user2 if match.user1_id == user.id else match.user1
        if partner.id in seen_partner_ids:
            continue
        seen_partner_ids.add(partner.id)
        partners.append(partner)
    return partners


def get_message_preview_text(message):
    if not message:
        return ""
    if message.text:
        return message.text
    if message.image:
        return "Фото"
    if message.video:
        return "Відео"
    return ""


def get_latest_chat(user, preview_limit=4):
    partners = get_match_partners(user)
    if not partners:
        return None

    partner_ids = [partner.id for partner in partners]
    latest_message = (
        ChatMessage.objects
        .filter(
            Q(sender=user, receiver_id__in=partner_ids)
            | Q(sender_id__in=partner_ids, receiver=user)
        )
        .select_related("sender", "receiver")
        .order_by("-created")
        .first()
    )

    latest_partner = partners[0]
    if latest_message:
        latest_partner = latest_message.receiver if latest_message.sender_id == user.id else latest_message.sender

    thread = (
        ChatMessage.objects
        .filter(
            Q(sender=user, receiver=latest_partner)
            | Q(sender=latest_partner, receiver=user)
        )
        .select_related("sender", "receiver")
        .order_by("-created")[:preview_limit]
    )

    preview_messages = []
    for message in reversed(list(thread)):
        preview_messages.append({
            "text": get_message_preview_text(message),
            "time": timezone.localtime(message.created).strftime("%H:%M"),
            "created_at": message.created.isoformat(),
            "is_mine": message.sender_id == user.id,
        })

    return {
        "partner": latest_partner,
        "messages": preview_messages,
        "chat_url": f"/messages/{latest_partner.id}/",
    }


def serialize_chat_message(message, me):
    return {
        "id": message.id,
        "text": message.text or "",
        "time": timezone.localtime(message.created).strftime("%H:%M"),
        "created_at": message.created.isoformat(),
        "is_mine": message.sender_id == me.id,
        "image_url": message.image.url if message.image else "",
        "video_url": message.video.url if message.video else "",
    }


def build_latest_chat_payload(user, message_limit=80):
    partners = get_match_partners(user)
    if not partners:
        return {"exists": False}

    partner_ids = [partner.id for partner in partners]
    latest_message = (
        ChatMessage.objects
        .filter(
            Q(sender=user, receiver_id__in=partner_ids)
            | Q(sender_id__in=partner_ids, receiver=user)
        )
        .select_related("sender", "receiver")
        .order_by("-created")
        .first()
    )

    partner = partners[0]
    if latest_message:
        partner = latest_message.receiver if latest_message.sender_id == user.id else latest_message.sender

    messages_qs = (
        ChatMessage.objects
        .filter(
            Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
        )
        .select_related("sender", "receiver")
        .order_by("-created")[:message_limit]
    )
    messages = [serialize_chat_message(msg, user) for msg in reversed(list(messages_qs))]

    return {
        "exists": True,
        "chat_url": f"/messages/{partner.id}/",
        "profile_url": f"/messages/profile/{partner.id}/",
        "partner": {
            "id": partner.id,
            "name": partner.name,
            "photo_url": partner.photo_url or "",
        },
        "messages": messages,
    }


def likes(request):
    if not request.session.get("user_id"):
        return redirect("auth")

    me = Profile.objects.get(id=request.session["user_id"])

    profiles = Profile.objects.filter(
        sent_likes__to_user=me
    ).exclude(
        received_likes__from_user=me
    )

    like_cards = [
        {"profile": p, "age": calculate_age(p.birth_date)}
        for p in profiles
    ]

    return render(request, "likes.html", {
        "profiles": profiles,
        "like_cards": like_cards,
        "current_user": me,
        "latest_chat": get_latest_chat(me),
    })

def sympathy(request):
    user = get_current_user(request)
    if not user:
        return redirect("auth")

    profiles = get_match_partners(user)

    sympathy_cards = [
        {"profile": p, "age": calculate_age(p.birth_date)}
        for p in profiles
    ]

    return render(request, "sympathy.html", {
        "profiles": profiles,
        "sympathy_cards": sympathy_cards,
        "current_user": user,
        "latest_chat": get_latest_chat(user),
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


def latest_chat_data(request):
    if not request.session.get("user_id"):
        return JsonResponse({"error": "unauthorized"}, status=401)

    me = Profile.objects.get(id=request.session["user_id"])
    return JsonResponse(build_latest_chat_payload(me))


def latest_chat_send(request):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    if not request.session.get("user_id"):
        return JsonResponse({"error": "unauthorized"}, status=401)

    me = Profile.objects.get(id=request.session["user_id"])
    payload = build_latest_chat_payload(me, message_limit=1)
    if not payload.get("exists"):
        return JsonResponse({"error": "no_chat"}, status=404)

    partner_id = payload["partner"]["id"]
    partner = Profile.objects.filter(id=partner_id).first()
    if not partner:
        return JsonResponse({"error": "partner_not_found"}, status=404)

    text = request.POST.get("text", "").strip()
    image = request.FILES.get("image")
    video = request.FILES.get("video")

    if not text and not image and not video:
        return JsonResponse({"error": "empty_message"}, status=400)

    ChatMessage.objects.create(
        sender=me,
        receiver=partner,
        text=text,
        image=image,
        video=video,
    )
    return JsonResponse(build_latest_chat_payload(me))


def chat(request, partner_id=None):
    if not request.session.get("user_id"):
        return redirect("auth")

    me = Profile.objects.get(id=request.session["user_id"])

    partners = get_match_partners(me)

    partner_map = {p.id: p for p in partners}

    conversations = []
    today = timezone.localdate()
    weekday_map = {
        0: "пн",
        1: "вт",
        2: "ср",
        3: "чт",
        4: "пт",
        5: "сб",
        6: "нд",
    }

    for partner in partners:
        last_message = ChatMessage.objects.filter(
            Q(sender=me, receiver=partner) | Q(sender=partner, receiver=me)
        ).order_by("-created").first()

        time_label = ""
        if last_message:
            local_created = timezone.localtime(last_message.created)
            if local_created.date() == today:
                time_label = local_created.strftime("%H:%M")
            else:
                time_label = weekday_map.get(local_created.weekday(), local_created.strftime("%d.%m"))

        conversations.append({
            "partner": partner,
            "last_message": last_message,
            "last_time": last_message.created if last_message else None,
            "time_label": time_label,
            "is_mine": last_message.sender_id == me.id if last_message else False,
        })

    conversations.sort(
        key=lambda c: c["last_time"].timestamp() if c["last_time"] else 0,
        reverse=True
    )

    active_partner = None
    if partner_id:
        active_partner = partner_map.get(partner_id)
        if not active_partner:
            return redirect("chat")
    elif partner_id is None:
        active_partner = None

    if request.method == "POST" and active_partner:
        text = request.POST.get("text", "").strip()
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        
        if text or image or video:
            ChatMessage.objects.create(
                sender=me, 
                receiver=active_partner, 
                text=text,
                image=image,
                video=video
            )
        return redirect(f"/messages/{active_partner.id}/")

    thread_messages = []
    if active_partner:
        thread_messages = ChatMessage.objects.filter(
            Q(sender=me, receiver=active_partner) | Q(sender=active_partner, receiver=me)
        ).order_by("created")

    return render(request, "messages.html", {
        "current_user": me,
        "conversations": conversations,
        "active_partner": active_partner,
        "thread_messages": thread_messages,
    })


def chat_partner_profile(request, partner_id):
    if not request.session.get("user_id"):
        return redirect("auth")

    me = Profile.objects.get(id=request.session["user_id"])
    partners = get_match_partners(me)
    partner_map = {p.id: p for p in partners}
    partner = partner_map.get(partner_id)
    if not partner:
        return redirect("chat")

    interests = []
    if partner.interests:
        interests = [item.strip() for item in partner.interests.split(",") if item.strip()]

    return render(request, "chat_partner_profile.html", {
        "current_user": me,
        "partner": partner,
        "partner_age": calculate_age(partner.birth_date),
        "partner_zodiac_sign": calculate_zodiac_sign(partner.birth_date),
        "partner_interests": interests,
    })


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

    opposite_gender_filter = get_opposite_gender_filter(me.gender)
    if opposite_gender_filter is not None:
        profiles = profiles.filter(opposite_gender_filter)

    profile = random.choice(list(profiles)) if profiles else None

    return render(request, "dating.html", {
        "profile": profile,
        "profile_age": calculate_age(profile.birth_date) if profile else None,
        "current_user": me,
        "latest_chat": get_latest_chat(me),
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
                profile.set_photo_file(photo)
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
            user.set_photo_file(request.FILES.get('photo'))

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


def delete_message(request, message_id):
    if not request.session.get('user_id'):
        return redirect('auth')
    
    me = Profile.objects.get(id=request.session['user_id'])
    
    try:
        message = ChatMessage.objects.get(id=message_id, sender=me)
        
        if message.image:
            if message.image.path:
                import os
                if os.path.exists(message.image.path):
                    os.remove(message.image.path)
        
        if message.video:
            if message.video.path:
                import os
                if os.path.exists(message.video.path):
                    os.remove(message.video.path)
        
        partner_id = message.receiver_id if message.sender_id == me.id else message.sender_id
        message.delete()
        
        return redirect(f'/messages/{partner_id}/')
    except ChatMessage.DoesNotExist:
        return redirect('chat')

