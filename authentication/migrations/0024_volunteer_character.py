# Generated by Django 4.2.4 on 2023-10-17 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0023_volunteer_guardian_faculty"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="character",
            field=models.CharField(default="null", max_length=10),
        ),
    ]
