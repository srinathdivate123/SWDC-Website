# Generated by Django 5.0 on 2024-01-11 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0037_remove_guardianfaculty_email_remove_secretary_module"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coordinator",
            name="contact_num",
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name="coordinator",
            name="parent_num",
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name="secretary",
            name="contact_num",
            field=models.CharField(max_length=10),
        ),
    ]
