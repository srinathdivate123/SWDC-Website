# Generated by Django 4.2.4 on 2023-09-11 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "authentication",
            "0008_coordinator_marked_in_fe_coordinator_marked_in_gp2_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="t_and_c",
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
