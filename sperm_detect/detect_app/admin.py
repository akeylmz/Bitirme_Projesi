from django.contrib import admin

# Register your models here.
from.models import UserVideo, VideoFrames,FrameLabels
admin.site.register(UserVideo)
admin.site.register(VideoFrames)
admin.site.register(FrameLabels)