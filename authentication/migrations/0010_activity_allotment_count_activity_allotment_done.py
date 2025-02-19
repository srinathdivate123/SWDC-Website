# Generated by Django 4.2.4 on 2023-09-21 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0009_alter_activity_t_and_c"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="allotment_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="activity",
            name="allotment_done",
            field=models.BooleanField(default=True),
        ),
    ]
