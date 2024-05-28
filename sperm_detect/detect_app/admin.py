from django.contrib import admin

# Register your models here.
from.models import UserVideo, VideoFrames,FrameLabels, Class, DetectModels
admin.site.register(UserVideo)
admin.site.register(VideoFrames)
admin.site.register(FrameLabels)
admin.site.register(Class)
admin.site.register(DetectModels)