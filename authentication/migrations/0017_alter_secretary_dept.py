# Generated by Django 4.2.4 on 2023-10-08 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0016_remove_coordinator_flagship_event_head_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="secretary",
            name="dept",
            field=models.CharField(max_length=60),
        ),
    ]
