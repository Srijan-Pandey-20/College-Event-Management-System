from functools import wraps

from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from .models import User

VALID_ROLES = (User.ROLE_STUDENT, User.ROLE_ADMIN)


def dashboard_url_for(role):
    return "/accounts/dashboard/admin/" if role == User.ROLE_ADMIN else "/accounts/dashboard/student/"


def get_session_user(request):
    """Return the User for this session, or None.
    The role always comes from the DATABASE, never from the cookie session.
    A broken session (deleted user, unknown role) is wiped, so it can
    never cause a redirect loop."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = User.objects.filter(id=user_id).first()
    if user is None or user.role not in VALID_ROLES:
        request.session.flush()
        return None
    request.session["role"] = user.role      # keep session in sync with DB
    request.session["username"] = user.username
    return user


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_session_user(request)
            if user is None:
                return redirect("/accounts/login/")
            if user.role != required_role:
                # logged in, but wrong area -> send to THEIR OWN dashboard
                return redirect(dashboard_url_for(user.role))
            return view_func(request, *args, **kwargs)
        return never_cache(wrapper)
    return decorator


def anonymous_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_session_user(request)
        if user is not None:
            return redirect(dashboard_url_for(user.role))
        return view_func(request, *args, **kwargs)
    return never_cache(wrapper)