from django.db.models.signals import pre_save 
from django.db.models.signals import post_save
from django.dispatch import receiver
from sperm_detect.settings import BEST_PT_PATH
from .models import UserVideo, VideoFrames
from django.db import models
from django.contrib.auth.models import User
from ultralytics import YOLO
from PIL import Image
import io

@receiver(post_save, sender=VideoFrames)
def labeling(sender, instance, **kwargs):
    
    # Load a model
    model = YOLO(BEST_PT_PATH)  # pretrained YOLOv8n model
    frame_path = instance.frame.path
    frame_a = instance.frame

    # Open the image file
    with open(frame_path, 'rb') as f:
        frame_data = f.read()
    
    # Convert to PIL image
    frame_image = Image.open(io.BytesIO(frame_data))

    # Run batched inference on a list of images
    model.predict(frame_image, save_txt=True, project=f"/Users/ahmetkemalyilmaz/Documents/VsCode/GITHUB/Bitirme_Projesi/sperm_detect/media/{instance.video.user.username}/labels")

    
    


    