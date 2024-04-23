from django.urls import path
from . import views

urlpatterns = [
    path('', views.detect_sperm, name='detect_sperm'),
]
