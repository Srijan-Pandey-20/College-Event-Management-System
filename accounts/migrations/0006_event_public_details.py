from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_student_confirmation_email_sent_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="event",
            name="highlights",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="event",
            name="schedule",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="event",
            name="theme",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="event",
            name="participation",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contact_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="event",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="event",
            name="contact_phone",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
