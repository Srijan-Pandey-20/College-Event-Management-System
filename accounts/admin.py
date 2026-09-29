from django.contrib import admin

from .models import Event, Student, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role")
    list_filter = ("role",)
    search_fields = ("username", "email")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "venue", "theme")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "event_choice", "user", "confirmation_email_sent", "registered_at")
    list_filter = ("event_choice", "confirmation_email_sent")
    search_fields = ("name", "email")
