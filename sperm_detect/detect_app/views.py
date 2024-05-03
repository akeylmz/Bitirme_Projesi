from django.http import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import render, redirect
import cv2
import numpy as np
import os
from sperm_detect import settings
from ultralytics import YOLO
from django.contrib.auth import authenticate, login, logout
from .forms import UserVideoForm
from tempfile import NamedTemporaryFile
from.models import UserVideo, VideoFrames
from django.core.files.base import ContentFile

from django.core.files.base import File

def split_video_frames(user_video):
    video_path = user_video.video_file.path
    video = cv2.VideoCapture(video_path)
    count = 1

    while True:
        success, frame = video.read()

        if not success:
            break

        # Dosya yolunu düzeltme
        frame_path = os.path.join(user_video.user.username, 'frames', f'{count}.jpg')
        
        # Çerçeve dosyasını oluşturma
        _, temp_frame = cv2.imencode('.jpg', frame)
        frame_content = ContentFile(temp_frame.tobytes())

        # VideoFrames modeline kaydetme
        new_frame = VideoFrames(
            video=user_video,
        )
        
        # Dosya adı ve içeriğini ayarlama
        new_frame.frame.save(frame_path, File(frame_content))

        new_frame.save()

        count += 1

    video.release()
    return count


def home(request):
    if request.method == 'POST':
        form = UserVideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            user_video=form.save()
            # Video dosyasını işleyerek frameleri ayır
            split_video_frames(user_video)

            return redirect('home')
    else:
        form = UserVideoForm()
    return render(request, 'home.html', {'form': form})

def labeling_sperm(request):
     # Kullanıcı adı
    username = request.user.username
    user= request.user
    user_video=UserVideo.objects.filter(user=user).first()
    video_frames=VideoFrames.objects.filter(video=user_video)
    return render(request, 'sperm_label.html', {"frames":video_frames})


def upload_video(request):
    if request.method == 'POST':
        if request.FILES.get('video'):
            print("video yüklendi")
            video = request.FILES['video']
            # YOLO modelini yükle
            model = YOLO('best.pt')
            sonuc = model.predict(source=video, show=True) 
            return JsonResponse({'sonuc': sonuc})



# Create your views here.
def login_request(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "account/login.html", {
                "error":"Kullanıcı adı veya parola yanlış"
            })
    else:
        return render(request, "account/login.html")

def logout_request(request):
    logout(request)
    return redirect("login")