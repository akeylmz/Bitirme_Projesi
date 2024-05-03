# forms.py

from django import forms
from .models import UserVideo

class UserVideoForm(forms.ModelForm):
    class Meta:
        model = UserVideo
        fields = ['video_file']
