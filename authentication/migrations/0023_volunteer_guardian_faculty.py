# Generated by Django 4.2.4 on 2023-10-17 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0022_remove_volunteer_guardian_faculty"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="guardian_faculty",
            field=models.CharField(default="not_assigned", max_length=50),
        ),
    ]
