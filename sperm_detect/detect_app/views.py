from django.http import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
import cv2
import numpy as np
import os
from sperm_detect import settings
from ultralytics import YOLO
from django.contrib.auth import authenticate, login, logout
from .forms import UserVideoForm
from tempfile import NamedTemporaryFile
from.models import UserVideo, VideoFrames, FrameLabels
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
            frame=VideoFrames.objects.filter(video=user_video).first()
            frame_id=frame.id
            return redirect('labeling', frame_id=frame_id)
    else:
        form = UserVideoForm()
    user_video=UserVideo.objects.filter(user=request.user).last()
    frame=VideoFrames.objects.filter(video=user_video).first()
    return render(request, 'home.html', {'form': form, 'frame':frame})

def labeling(request, frame_id):
    frame= VideoFrames.objects.filter(id=frame_id).first()
    user_video = get_object_or_404(UserVideo,id=frame.video.id)
    frame_last = user_video.video_frames.last()
    frame_first = user_video.video_frames.first()

    frame_next_id=int(frame_id)+1
    frame_next=VideoFrames.objects.filter(id=frame_next_id).first()
    if frame_next is None:
        frame_next_id = 0

    frame_previous_id=int(frame_id)-1

    if frame_previous_id <frame_first.id:
        frame_previous_id = 0
    labels= FrameLabels.objects.filter(labels_frame=frame_id)
    return render(request, 'labeling.html', {'frame': frame,'frame_next_id': frame_next_id, 'labels':labels,'frame_last':frame_last, 'frame_previous_id':frame_previous_id})

def galery(request):
     # Kullanıcı adı
    username = request.user.username
    user= request.user
    user_video=UserVideo.objects.filter(user=user).first()
    video_frames=VideoFrames.objects.filter(video=user_video)

    frames_with_labels = []
    for frame in video_frames:
        labels = FrameLabels.objects.filter(labels_frame=frame)
        frames_with_labels.append({"frame": frame, "labels": labels})
    labels =FrameLabels.objects.all()

    return render(request, 'sperm_label.html', {"frames":video_frames, "labels":labels})

def delete_label(request, label_id):
    label=get_object_or_404(FrameLabels, id=label_id)
    label.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def add_label(request, frame_id):
    if request.method == 'POST':
        x=request.POST.get('x')
        y=request.POST.get('y')
        w=request.POST.get('w')
        h=request.POST.get('h')
        frame=get_object_or_404(VideoFrames, id=frame_id)
        label=FrameLabels.objects.create(
            labels_frame=frame,
            x=x,
            y=y,
            w=w,
            h=h
        )
    return redirect(request.META.get('HTTP_REFERER'))


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