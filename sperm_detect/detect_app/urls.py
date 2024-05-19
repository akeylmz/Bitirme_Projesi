from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('labeling/<frame_id>', views.labeling, name='labeling'),
    path('delete_label/<label_id>', views.delete_label, name='delete_label'),
    path('add_label/<frame_id>', views.add_label, name='add_label'),
    path('user_video_frames_labels/<user_video_id>', views.user_video_frames_labels, name='user_video_frames_labels'),
    path('txt_frames/<user_video_id>', views.txt_frames, name='txt_frames'),

    path("", views.login_request, name='login'),
    path("account/login/", views.login_request, name='login'),
    path("logout", views.logout_request, name='logout'),
]
