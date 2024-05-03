from django.db import models
from django.contrib.auth.models import User

class UserVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_videos')
    video_file = models.FileField(upload_to='videos/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

def frame_upload_path(instance, filename):
    return f"{instance.video.user.username}/frames/{filename}"

class VideoFrames(models.Model):
    video = models.ForeignKey(UserVideo, on_delete=models.CASCADE, related_name='video_frames')
    frame = models.FileField()

class FrameLabels(models.Model):
    labels_frame = models.ForeignKey(VideoFrames, on_delete=models.CASCADE, related_name='frame_labels')
    labels_txt = models.FileField()
    x = models.DecimalField(max_digits=10, decimal_places=7)
    y = models.DecimalField(max_digits=10, decimal_places=7)
    w = models.DecimalField(max_digits=10, decimal_places=7)
    h = models.DecimalField(max_digits=10, decimal_places=7)

