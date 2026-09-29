from django.db import models


class User(models.Model):
    ROLE_STUDENT = "student"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_ADMIN, "Admin"),
    ]

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    # Every account is a "student" account unless an admin manually promotes it
    # (via the Django admin site at /admin/). There is no self-service way to
    # become an admin.
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    venue = models.CharField(max_length=200)

    # Public information shown on the event detail page and homepage.
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    schedule = models.TextField(blank=True)
    theme = models.CharField(max_length=255, blank=True)
    participation = models.TextField(blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    # Links a registration to the logged-in account that created it.
    # Nullable so existing rows created before this field existed remain valid.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="registrations"
    )
    name = models.CharField(max_length=200)
    # No longer unique: a student now has ONE Student row PER event they
    # register for, so the same email legitimately appears on multiple rows.
    email = models.EmailField()
    # storing event name as plain text (no foreign key needed for your use-case)
    event_choice = models.CharField(max_length=200)
    registered_at = models.DateTimeField(auto_now_add=True, null=True)
    confirmation_email_sent = models.BooleanField(default=False)

    class Meta:
        # Prevents the same account from registering for the same event twice,
        # while still allowing multiple different events per student.
        unique_together = ("user", "event_choice")

    def __str__(self):
        return f"{self.name} - {self.event_choice}"
