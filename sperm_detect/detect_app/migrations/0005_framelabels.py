# Generated by Django 5.0.4 on 2024-05-03 14:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect_app', '0004_alter_videoframes_frame'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrameLabels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('labels_txt', models.FileField(upload_to='')),
                ('x', models.DecimalField(decimal_places=7, max_digits=10)),
                ('y', models.DecimalField(decimal_places=7, max_digits=10)),
                ('w', models.DecimalField(decimal_places=7, max_digits=10)),
                ('h', models.DecimalField(decimal_places=7, max_digits=10)),
                ('labels_frame', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frame_labels', to='detect_app.videoframes')),
            ],
        ),
    ]
