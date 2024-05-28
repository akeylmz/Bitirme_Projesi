# forms.py

from django import forms
from .models import UserVideo, Class, DetectModels

class UserVideoForm(forms.ModelForm):
    class Meta:
        model = UserVideo
        fields = ['video_file', 'video_name', 'track_mode', 'model']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'class_id']

class ModelForm(forms.ModelForm):
    class Meta:
        model = DetectModels
        fields = ['model_name', 'model_file']
