# Generated by Django 5.0 on 2024-01-11 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0036_delete_failedregistration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="guardianfaculty",
            name="email",
        ),
        migrations.RemoveField(
            model_name="secretary",
            name="module",
        ),
    ]