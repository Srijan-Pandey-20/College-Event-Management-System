import json

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .decorators import anonymous_only, role_required
from .models import Event, Student, User


def homePage(request):
    """Render the public homepage from the same Event rows used by the
    dashboards, so creating/deleting an event is immediately reflected here."""
    events = Event.objects.order_by("date", "id")
    return render(request, "accounts/home.html", {"events": events})


@never_cache
def event_detail(request, event_id):
    """Render the information page only while the event exists in the database.

    Because this lookup is by the Event primary key, deleting the event from
    the admin dashboard makes this URL return a normal 404 immediately on
    refresh instead of rendering stale event information.
    """
    event = get_object_or_404(Event, id=event_id)
    context = {
        "event": event,
        "highlights": [line.strip() for line in event.highlights.splitlines() if line.strip()],
        "schedule_items": [line.strip() for line in event.schedule.splitlines() if line.strip()],
    }
    return render(request, "accounts/event_detail.html", context)


@anonymous_only
def signup(request):
    return render(request, "accounts/signup.html")


@anonymous_only
def login(request):
    return render(request, "accounts/login.html")


@require_POST
@never_cache
def logout_view(request):
    request.session.flush()
    return redirect("/")          # real home page (home.html)


def send_registration_confirmation_email(user, event):
    """Sends (or, without real credentials configured, prints to the
    console) a confirmation email for a single event registration.
    Returns True if the send call completed without raising."""
    subject = f"Registration Confirmed: {event.name}"
    message = (
        f"Hi {user.username},\n\n"
        f"Your registration for \"{event.name}\" has been confirmed.\n\n"
        f"Date: {event.date}\n"
        f"Venue: {event.venue}\n\n"
        f"See you there!\n"
        f"SRMCEM Event Team"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception:
        # Registration should still succeed even if the email fails to send
        # (e.g. bad/missing SMTP credentials) — we just won't mark it as sent.
        return False


# -----------------------------------------------------------------------------
# JSON API views used by signup.html / login.html (fetch calls)
# -----------------------------------------------------------------------------


@csrf_exempt
def register(request):
    """Creates a new account. Every account created here is a STUDENT
    account. There is no self-service way to become an admin — admin
    accounts are promoted manually through the Django admin site."""
    if request.method != "POST":
        return JsonResponse({"error": "Wrong method"})

    data = json.loads(request.body)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    try:
        if not username or not email or not password:
            return JsonResponse({"error": "All Fields are Required"})
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User Already Exist"})
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "User Already Exist"})

        user = User(
            username=username,
            email=email,
            password=make_password(password),
            role=User.ROLE_STUDENT,
        )
        user.save()
        return JsonResponse({
            "message": "User has been created successfully",
            "status": True,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)})


@csrf_exempt
def login_user(request):
    """Verifies credentials and starts a Django session. The session
    (not a token) is what the dashboard views check to decide whether
    someone is logged in and which role they have."""
    if request.method != "POST":
        return JsonResponse({"error": "Wrong method"})

    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"})

    if not check_password(password, user.password):
        return JsonResponse({"error": "Invalid password"})

    request.session.cycle_key()   # fresh session ID on login (prevents session fixation)
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role

    redirect_url = (
        "/accounts/dashboard/admin/"
        if user.role == User.ROLE_ADMIN
        else "/accounts/dashboard/student/"
    )

    return JsonResponse({"status": True, "role": user.role, "redirect_url": redirect_url})


# -----------------------------------------------------------------------------
# Dashboards
# -----------------------------------------------------------------------------

@role_required(User.ROLE_STUDENT)
def student_dashboard(request):
    user_id = request.session["user_id"]
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        selected_event_ids = request.POST.getlist("event_ids")
        newly_registered_events = []

        for event in Event.objects.filter(id__in=selected_event_ids):
            registration, created = Student.objects.get_or_create(
                user_id=user_id,
                event_choice=event.name,
                defaults={"name": user.username, "email": user.email},
            )
            if created:
                email_sent = send_registration_confirmation_email(user, event)
                registration.confirmation_email_sent = email_sent
                registration.save(update_fields=["confirmation_email_sent"])
                newly_registered_events.append(event.name)

        # One-time flash message, shown once after the redirect then cleared.
        request.session["newly_registered_events"] = newly_registered_events
        return redirect("/accounts/dashboard/student/")

    my_registrations = Student.objects.filter(user_id=user_id)
    registered_event_names = set(my_registrations.values_list("event_choice", flat=True))
    events = Event.objects.all()
    newly_registered_events = request.session.pop("newly_registered_events", [])

    context = {
        "username": request.session.get("username"),
        "my_registrations": my_registrations,
        "registered_event_names": registered_event_names,
        "events": events,
        "newly_registered_events": newly_registered_events,
    }
    return render(request, "accounts/student_dashboard.html", context)

@require_POST
@role_required(User.ROLE_STUDENT)
def unregister_student_event(request, registration_id):
    """Unregister the currently logged-in student from one event.

    The registration row is removed, which also means the event becomes
    selectable again on the student's dashboard after the redirect.
    """
    registration = get_object_or_404(
        Student,
        id=registration_id,
        user_id=request.session["user_id"],
    )
    registration.delete()
    return redirect("/accounts/dashboard/student/")


@require_POST
@role_required(User.ROLE_ADMIN)
def delete_event(request, event_id):
    """Delete an event and all registrations for that event.

    Student registrations currently store the event name as text rather than
    a ForeignKey, so the related registration rows must be deleted explicitly
    before deleting the Event row. Student accounts themselves are preserved.
    """
    event = get_object_or_404(Event, id=event_id)
    Student.objects.filter(event_choice=event.name).delete()
    event.delete()
    return redirect("/accounts/dashboard/admin/")


@require_POST
@role_required(User.ROLE_ADMIN)
def manage_student_registration(request, registration_id):
    """Handle an admin's removal choice for a specific registration.

    action=unregister removes only that student's registration for this event.
    action=delete_account removes the registration and the student's account;
    User.on_delete=CASCADE then removes any other registrations for that user.
    """
    registration = get_object_or_404(
        Student.objects.select_related("user"),
        id=registration_id,
    )
    action = request.POST.get("action")

    if action == "unregister":
        registration.delete()
    elif action == "delete_account":
        if registration.user_id:
            registration.user.delete()
        else:
            # Legacy registration without a linked account: there is no
            # account to remove, so remove only this registration row.
            registration.delete()

    return redirect("/accounts/dashboard/admin/")


@role_required(User.ROLE_ADMIN)
def admin_dashboard(request):
    if request.method == "POST":
        name = request.POST.get("event_name", "").strip()
        date = request.POST.get("event_date")
        venue = request.POST.get("event_venue", "").strip()
        description = request.POST.get("event_description", "").strip()
        highlights = request.POST.get("event_highlights", "").strip()
        schedule = request.POST.get("event_schedule", "").strip()
        theme = request.POST.get("event_theme", "").strip()
        participation = request.POST.get("event_participation", "").strip()
        contact_name = request.POST.get("event_contact_name", "").strip()
        contact_email = request.POST.get("event_contact_email", "").strip()
        contact_phone = request.POST.get("event_contact_phone", "").strip()

        # The original event fields stay required, while the detail-page
        # fields give the admin a single place to publish the public event
        # information.  We redirect back without creating a partial event
        # when required public content is missing.
        required_details = (description, highlights, schedule, theme, participation)
        if name and date and venue and all(required_details):
            Event.objects.create(
                name=name,
                date=date,
                venue=venue,
                description=description,
                highlights=highlights,
                schedule=schedule,
                theme=theme,
                participation=participation,
                contact_name=contact_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
            )
        return redirect("/accounts/dashboard/admin/")

    context = {
        "username": request.session.get("username"),
        "students": Student.objects.select_related("user").all(),
        "events": Event.objects.order_by("date", "id"),
    }
    return render(request, "accounts/admin_dashboard.html", context)
