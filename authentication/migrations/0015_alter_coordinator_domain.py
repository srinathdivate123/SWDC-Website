# Generated by Django 4.2.4 on 2023-09-26 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0014_secretary_activity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coordinator",
            name="domain",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
