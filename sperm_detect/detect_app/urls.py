from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('labeling_sperm', views.labeling_sperm, name='labeling_sperm'),
    path('upload_video', views.upload_video, name='upload_video'),
    path("", views.login_request, name='login'),
    path("account/login/", views.login_request, name='login'),
    path("logout", views.logout_request, name='logout'),
]
