# Generated by Django 5.0.4 on 2024-05-25 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect_app', '0011_framelabels_track_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideo',
            name='track_mode',
            field=models.BooleanField(default=False),
        ),
    ]