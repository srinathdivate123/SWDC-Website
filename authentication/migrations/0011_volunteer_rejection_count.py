# Generated by Django 4.0.6 on 2025-02-16 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_alter_attendance_options_alter_event_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='rejection_count',
            field=models.IntegerField(default=0),
        ),
    ]
