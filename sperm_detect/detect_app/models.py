from django.db import models
from django.contrib.auth.models import User

class DetectModels(models.Model):
    model_file = models.FileField(upload_to='models/')
    model_name = models.CharField(max_length=128)

class Class(models.Model):
    class_model = models.ForeignKey(DetectModels, on_delete=models.CASCADE, related_name='model_clases')
    class_name = models.CharField(max_length=128,blank=True,null=True)
    class_id = models.IntegerField()

class UserVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_videos')
    model = models.ForeignKey(DetectModels, on_delete=models.CASCADE, related_name='model_videos',blank=True,null=True)
    video_file = models.FileField(upload_to='videos/')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    video_name = models.CharField(max_length=128,blank=True,null=True)
    track_mode = models.BooleanField(default=False)

class VideoFrames(models.Model):
    video = models.ForeignKey(UserVideo, on_delete=models.CASCADE, related_name='video_frames')
    frame = models.FileField()

class FrameLabels(models.Model):
    labels_frame = models.ForeignKey(VideoFrames, on_delete=models.CASCADE, related_name='frame_labels')
    x = models.FloatField()
    y = models.FloatField()
    w = models.FloatField()
    h = models.FloatField()
    labels_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_labels', blank=True, null=True)
    track_id = models.IntegerField(blank=True, null=True)



