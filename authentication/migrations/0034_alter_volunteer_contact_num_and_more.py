# Generated by Django 4.2.4 on 2023-12-08 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0033_volunteer_profile_edited"),
    ]

    operations = [
        migrations.AlterField(
            model_name="volunteer",
            name="contact_num",
            field=models.CharField(max_length=12),
        ),
        migrations.AlterField(
            model_name="volunteer",
            name="parent_num",
            field=models.CharField(max_length=12),
        ),
    ]
