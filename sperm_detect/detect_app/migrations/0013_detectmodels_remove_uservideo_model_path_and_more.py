# Generated by Django 5.0.4 on 2024-05-27 17:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect_app', '0012_uservideo_track_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetectModels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_file', models.FileField(upload_to='models/')),
                ('model_name', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveField(
            model_name='uservideo',
            name='model_path',
        ),
        migrations.AddField(
            model_name='uservideo',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='model_videos', to='detect_app.detectmodels'),
        ),
    ]
