# Generated by Django 5.0.4 on 2024-05-03 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect_app', '0003_videoframes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoframes',
            name='frame',
            field=models.FileField(upload_to=''),
        ),
    ]