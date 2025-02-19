# Generated by Django 4.2.4 on 2023-10-16 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0018_activity_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="FalcultyAdvisor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="", max_length=50)),
                ("email", models.CharField(default="", max_length=30)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name_plural": "Faculty Advisors",
                "ordering": ["name"],
            },
        ),
    ]
