from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('galery', views.galery, name='galery'),
    path('labeling/<frame_id>', views.labeling, name='labeling'),


    path("", views.login_request, name='login'),
    path("account/login/", views.login_request, name='login'),
    path("logout", views.logout_request, name='logout'),
]
