from django.http import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserVideoForm
from.models import UserVideo, VideoFrames, FrameLabels
from django.core.files.base import ContentFile, File
import json
import cv2
import os
import zipfile
from io import BytesIO
def split_video_frames(user_video):
    video_path = user_video.video_file.path
    video = cv2.VideoCapture(video_path)
    count = 1

    while True:
        success, frame = video.read()

        if not success:
            break

        # Dosya yolunu düzeltme
        frame_path = os.path.join(user_video.user.username, str(user_video.id), 'frames', f'{count}.jpg')
        
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
    return render(request, 'home.html', {'form': form, 'frame':frame, 'user_video':user_video})

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

def zip_directory(directory_path):
    # Geçici bellek nesnesi oluştur
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Belirtilen klasördeki tüm dosyaları ve alt klasörleri zip dosyasına ekle
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, directory_path))
    return zip_buffer

def txt_frames(request, user_video_id):
    try:
        user_video = UserVideo.objects.get(pk=user_video_id)
        frames = user_video.video_frames.all()

        video_id = str(user_video.id)
        username = user_video.user.username
        directory_path = os.path.join('media', username, video_id)

        for frame in frames:
            
            frame_path = frame.frame.path
            frame_name = os.path.splitext(os.path.basename(frame_path))[0]
            
            labels = frame.frame_labels.all()
            labels_dir = os.path.join('media', frame.video.user.username, str(frame.video.id), 'labels')
            os.makedirs(labels_dir, exist_ok=True)  # Klasörü oluştur (varsa hata vermez)
            label_file_path = os.path.join(labels_dir, frame_name + '.txt')
            with open(label_file_path, 'w') as label_file:
                for label in labels:
                    label_file.write(f'{label.x} {label.y} {label.w} {label.h}\n')  # Etiket bilgilerini dosyaya yaz
        if not os.path.exists(directory_path):
            return JsonResponse({'error': 'Directory does not exist'}, status=404)
        
        # Klasörü zip dosyasına ekle
        zip_buffer = zip_directory(directory_path)
        
        # Zip dosyasını bellekte sona erdir
        zip_buffer.seek(0)
        
        # HTTP yanıtı oluştur
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={username}_{video_id}_labels.zip'
        return response
    
    except UserVideo.DoesNotExist:
        return JsonResponse({'error': 'User video does not exist'}, status=404)

def user_video_frames_labels(request, user_video_id):
    try:
        user_video = UserVideo.objects.get(pk=user_video_id)
        # Frames'i al
        frames = user_video.video_frames.all()
        date_create = user_video.date_uploaded.strftime('%d-%m-%Y')
        date_year = user_video.date_uploaded.strftime('%Y')

        user_name=user_video.user
        desc = f"{user_name}'s Video Frames Labels"
        print(date_create)
        # COCO veri yapısını oluştur
        coco_data = {
            "info": {
                "description": desc,
                "version": "1.0",
                "year": date_year,
                "contributor": "Your Company",
                "date_created": date_create
            },
            "licenses": [
                {
                    "id": 1,
                    "name": "Attribution-NonCommercial-ShareAlike License",
                    "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
                }
            ],
            "images": [],
            "annotations": [],
            "categories": [
                {
                    "id": 1,
                    "name": "sperm",
                    "supercategory": "sperm"
                }
            ]
        }
        
        annotation_id = 1  # Benzersiz annotation id'si için sayaç

        # Frames ve etiketleri COCO formatına dönüştür
        for frame in frames:
            frame_path = frame.frame.path
            frame_name = os.path.splitext(os.path.basename(frame_path))[0]
            
            # Frame (image) bilgileri
            image_info = {
                "id": frame.id,
                "file_name": os.path.basename(frame_path),
                "width": 1920,  # Frame genişliğini ekle
                "height": 1080,  # Frame yüksekliğini ekle
                "date_captured": date_create,
                "license": 1,
                "coco_url": "",  # Opsiyonel, boş bırakılabilir
                "flickr_url": ""  # Opsiyonel, boş bırakılabilir
            }
            coco_data["images"].append(image_info)
            
            labels = frame.frame_labels.all()
            for label in labels:
                # Annotation bilgileri
                annotation_info = {
                    "id": annotation_id,
                    "image_id": frame.id,
                    "category_id": 1,  # 'sperm' kategorisi için id
                    "bbox": [label.x, label.y, label.w, label.h],
                    "area": label.w * label.h,
                    "segmentation": [],
                    "iscrowd": 0
                }
                coco_data["annotations"].append(annotation_info)
                annotation_id += 1

        video_path = user_video.video_file.path
        json_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # JSON dönüştürme ve HttpResponse oluşturma
        json_data = json.dumps(coco_data, indent=4)
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{json_name}.json"'
        return response

    except UserVideo.DoesNotExist:
        return JsonResponse({'error': 'User video does not exist'}, status=404)

def delete_label(request, label_id):
    label=get_object_or_404(FrameLabels, id=label_id)
    label.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def add_label(request, frame_id):
    if request.method == 'POST':
        x = float(request.POST.get('x'))
        y = float(request.POST.get('y'))
        w = float(request.POST.get('w'))
        h = float(request.POST.get('h'))
        frame=get_object_or_404(VideoFrames, id=frame_id)
        x=x/1920
        w=w/1920
        y=y/1080
        h=h/1080
        y=y+h/2
        x=x+w/2
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