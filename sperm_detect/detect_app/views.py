from django.http import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserVideoForm, ClassForm, ModelForm
from.models import UserVideo, VideoFrames, FrameLabels, Class, DetectModels
from django.core.files.base import ContentFile, File
import json
import cv2
import os
import zipfile
from io import BytesIO
from django.db.models import Count
from ultralytics import YOLO
from django.core.files.storage import FileSystemStorage

#Views.

def split_video_frames(user_video):
    video_path = user_video.video_file.path
    video = cv2.VideoCapture(video_path)
    count = 1
    
    model = YOLO(user_video.model.model_file.path)
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
        
        frame_path = new_frame.frame.path

        # Run batched inference on a list of images
        results = model.predict(frame_path)

        for r in results:
            if r.boxes.xywhn.tolist() is not None:
                for c in r.boxes.xywhn.tolist(): # To get the coordinates.
                    x, y, w, h = c[0], c[1], c[2], c[3] # x, y are the center coordinates.
                    class_id = int(r.boxes.cls[results.index(r)])  # Get the class ID
            
                    # Get the current video model
                    current_video_model = user_video.model
                    
                    # Check if the class with the given class_id exists for the current model
                    class_obj, created = Class.objects.get_or_create(
                        class_model=current_video_model,
                        class_id=class_id,
                        defaults={'class_name': model.names[class_id] if class_id < len(model.names) else ""}
                    )
                    #label_file.write(f'{x} {y} {w} {h}\n')  # Etiket bilgilerini dosyaya yaz
                    label_new= FrameLabels.objects.create(
                        labels_frame=new_frame,
                        x=x,
                        y=y,
                        w=w,
                        h=h,
                        labels_class=class_obj  # Link to the class object

                    )  

        count += 1

    video.release()
    return count

def split_video_frames_track_mode(user_video):
    
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
        
        frame_path = new_frame.frame.path

        # Run batched inference on a list of images

        count += 1

    video.release()
    track_mode_create_labels(user_video)
    return count

def track_mode_create_labels(user_video):
    model = YOLO(user_video.model.model_file.path)
    first_frame=VideoFrames.objects.filter(video=user_video).first()
    frame_id=first_frame.id
    detections = []
    results = model.track(user_video.video_file.path)
# Iterate over each result in the results
    for r in results:
        # Check if the result has a 'boxes' attribute
        if hasattr(r, 'boxes') and r.boxes is not None:
            # Iterate over each box, tracking id, and its corresponding class id
            for box, track_id in zip(r.boxes.xywhn, r.boxes.id):
                # Unpack the bounding box coordinates
                new_frame=get_object_or_404(VideoFrames, id=frame_id)
                x, y, w, h = box[0], box[1], box[2], box[3]
                if results.index(r) < len(r.boxes.cls):
                    class_id = int(r.boxes.cls[results.index(r)])
                else:
                    class_id = int(r.boxes.cls[(len(r.boxes.cls)-1)])  # Get the class ID
                current_video_model = user_video.model

                class_obj, created = Class.objects.get_or_create(
                        class_model=current_video_model,
                        class_id=class_id,
                        defaults={'class_name': model.names[class_id] if class_id < len(model.names) else ""}
                    )
                label_new= FrameLabels.objects.create(
                        labels_frame=new_frame,
                        x=x,
                        y=y,
                        w=w,
                        h=h,
                        labels_class=class_obj,  # Link to the class object
                        track_id=track_id
                    ) 
            frame_id+=1
    return frame_id

    

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

# Downloads.

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
            first_label = labels.first()
            if first_label:
                class_name =  first_label.labels_class.class_name
            else:
                class_name = "none"
            labels_dir = os.path.join('media', frame.video.user.username, str(frame.video.id), 'labels', class_name)
            os.makedirs(labels_dir, exist_ok=True)  # Klasörü oluştur (varsa hata vermez)
            label_file_path = os.path.join(labels_dir, frame_name + '.txt')
            with open(label_file_path, 'w') as label_file:
                for label in labels:
                    label_file.write(f'{label.labels_class.class_id} {label.x} {label.y} {label.w} {label.h}\n')  # Etiket bilgilerini dosyaya yaz
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
        frames_count=len(frames)
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
            "images_number": frames_count,
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

# Template.

def home(request):
    if request.method == 'POST':
        form = UserVideoForm(request.POST, request.FILES)
        model_form = ModelForm(request.POST, request.FILES)

        if form.is_valid():
            form.instance.user = request.user
            user_video=form.save()
            # Video dosyasını işleyerek frameleri ayır
            if user_video.track_mode:
                print("track mode run")
                split_video_frames_track_mode(user_video)
                

            else:
                split_video_frames(user_video)

            frame=VideoFrames.objects.filter(video=user_video).first()
            frame_id=frame.id
            return redirect('labeling', frame_id=frame_id)
        elif model_form.is_valid():
            model_form.save()
            return redirect('home')
    else:
        form = UserVideoForm()
        model_form = ModelForm()

    user_video=UserVideo.objects.filter(user=request.user).last()
    user_videos=UserVideo.objects.filter(user=request.user)
    models=DetectModels.objects.all()
    frame=VideoFrames.objects.filter(video=user_video).first()
    return render(request, 'home.html', {'form': form, 'frame':frame, 'user_video':user_video, 'user_videos':user_videos, 'model_form':model_form, 'models':models})

def video(request, user_video_id):
    
    user_video=UserVideo.objects.filter(id=user_video_id).first()

    frame=VideoFrames.objects.filter(video=user_video).first()
    if frame:
        frames=VideoFrames.objects.filter(video=user_video)
        frame_count=len(frames)
        total_labels = user_video.video_frames.aggregate(count=Count('frame_labels'))['count'] or 0
        rate0=total_labels/frame_count
        rate = f"{rate0:.2f}"
    else:
        frames=None
        frame_count=None
        total_labels = None
        rate0=None
        rate = None

    return render(request, 'video.html', {'frame':frame,'frame_count':frame_count, 'total_labels':total_labels, 'user_video':user_video, 'rate':rate})

def labeling(request, frame_id, mode, option_count, option_class):
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
    clases=Class.objects.filter(class_model=user_video.model)
    draw_counts=[1,5,10,20,50]
    return render(request, 'labeling.html', 
                  {'video':user_video,
                   'frame': frame,
                   'frame_next_id': frame_next_id,
                    'labels':labels,'frame_last':frame_last, 
                    'frame_previous_id':frame_previous_id, 
                    'clases':clases, 
                    'mode':mode, 
                    'option_count':option_count, 
                    'option_class':option_class,
                    'draw_counts':draw_counts
                    })

def deneme(request, frame_id):
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
    return render(request, 'deneme.html', {'video':user_video,'frame': frame,'frame_next_id': frame_next_id, 'labels':labels,'frame_last':frame_last, 'frame_previous_id':frame_previous_id})

def upload_frames(request):
    if request.method == 'POST':
        user = request.user
        video_name = request.POST.get('video_name')
        images = request.FILES.getlist('imageInput')
        model_id = request.POST.get('model')
        model = get_object_or_404(DetectModels, id=model_id)

        new_video = UserVideo.objects.create(
            user=user,
            model=model,
            video_name=video_name
        )
        
        yolo_model = YOLO(new_video.model.model_file.path)

        for count, image in enumerate(images, start=1):
            # Dosya yolu oluştur
            frame_path = os.path.join('media', new_video.user.username, str(new_video.id), 'frames', f'{count}.jpg')
            frame_up_path = os.path.join( new_video.user.username, str(new_video.id), 'frames', f'{count}.jpg')

            # FileSystemStorage kullanarak dosyayı belirli bir yola kaydet
            fs = FileSystemStorage(location=os.path.join('media', new_video.user.username, str(new_video.id), 'frames'))
            filename = fs.save(f'{count}.jpg', image)
            
            # Kaydedilen dosyanın tam yolu
            file_path = fs.path(filename)
            print(frame_up_path)
            # VideoFrames objesi oluştur ve kaydet
            new_frame = VideoFrames.objects.create(video=new_video, frame=frame_up_path)

            results = yolo_model.predict(frame_path)

            for r in results:
                if r.boxes.xywhn.tolist() is not None:
                    for c in r.boxes.xywhn.tolist(): # To get the coordinates.
                        x, y, w, h = c[0], c[1], c[2], c[3] # x, y are the center coordinates.
                        class_id = int(r.boxes.cls[results.index(r)])  # Get the class ID
                
                        # Get the current video model
                        current_video_model = new_video.model
                        
                        # Check if the class with the given class_id exists for the current model
                        class_obj, created = Class.objects.get_or_create(
                            class_model=current_video_model,
                            class_id=class_id,
                            defaults={'class_name': yolo_model.names[class_id] if class_id < len(yolo_model.names) else ""}
                        )
                        #label_file.write(f'{x} {y} {w} {h}\n')  # Etiket bilgilerini dosyaya yaz
                        label_new = FrameLabels.objects.create(
                            labels_frame=new_frame,
                            x=x,
                            y=y,
                            w=w,
                            h=h,
                            labels_class=class_obj  # Link to the class object
                        )

        return redirect('upload_frames')

    user_video = UserVideo.objects.filter(user=request.user).last()
    user_videos = UserVideo.objects.filter(user=request.user)
    models = DetectModels.objects.all()
    frame = VideoFrames.objects.filter(video=user_video).first()
    return render(request, 'upload_frames.html', { 'frame': frame, 'user_video': user_video, 'user_videos': user_videos, 'models': models })
#  add- Delete.

def delete_label(request, label_id):
    label=get_object_or_404(FrameLabels, id=label_id)
    label.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def delete_video(request, video_id):
    video=get_object_or_404(UserVideo, id=video_id)
    video.delete()
    return redirect('home')

def add_label(request, frame_id):
    if request.method == 'POST':
        x = float(request.POST.get('x'))
        y = float(request.POST.get('y'))
        w = float(request.POST.get('w'))
        h = float(request.POST.get('h'))
        labels_class = request.POST.get('labels_class')
        labels_count = int(request.POST.get('labels_count'))  # Ensure labels_count is an integer

        frame=get_object_or_404(VideoFrames, id=frame_id)
        class_object=get_object_or_404(Class, id=labels_class)
        video = frame.video

        x=x/1920
        w=w/1920
        y=y/1080
        h=h/1080
        y=y+h/2
        x=x+w/2

        all_frames = VideoFrames.objects.filter(video=video).order_by('id')
        start_index = list(all_frames).index(frame)
        frames_to_label = all_frames[start_index:start_index + labels_count]

        for f in frames_to_label:
            FrameLabels.objects.create(
                labels_frame=f,
                x=x,
                y=y,
                w=w,
                h=h,
                labels_class=class_object
            )
    return redirect(request.META.get('HTTP_REFERER'))

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_label(request, label_id):
    label=FrameLabels.objects.filter(id=label_id)
    frame=label.labels_frame
    if request.method == 'POST':
        x = float(request.POST.get('x'))
        y = float(request.POST.get('y'))
        w = float(request.POST.get('w'))
        h = float(request.POST.get('h'))
        x=x/1920
        w=w/1920
        y=y/1080
        h=h/1080
        y=y+h/2
        x=x+w/2
        label.x=x
        label.y=y
        label.w=w
        label.h=h
        label.save()
    return redirect(request.META.get('HTTP_REFERER'))

# Account.
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