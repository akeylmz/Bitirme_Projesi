from django.db.models.signals import pre_save 
from django.db.models.signals import post_save
from django.dispatch import receiver
import numpy as np
from sperm_detect.settings import BEST_PT_PATH
from .models import UserVideo, VideoFrames, FrameLabels
from django.db import models
from django.contrib.auth.models import User
from ultralytics import YOLO
from PIL import Image
import io
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated

@receiver(post_save, sender=VideoFrames)
def labeling(sender, instance, created, **kwargs):
    if created:
        # Load a model
        model = YOLO(BEST_PT_PATH)  # pretrained YOLOv8n model
        frame_path = instance.frame.path

        # Open the image file
        with open(frame_path, 'rb') as f:
            frame_data = f.read()
        
        # Convert to PIL image
        frame_image = Image.open(io.BytesIO(frame_data))

        # Run batched inference on a list of images
        results=model.predict(frame_image)
        
        for r in results:
            if r.boxes.xywh.tolist() is not None:
                for c in r.boxes.xywh.tolist(): # To get the coordinates.
                    print(c)
                    x, y, w, h = c[0], c[1], c[2], c[3] # x, y are the center coordinates.
                    label_f= FrameLabels.objects.create(
                        labels_frame=instance,
                        x=x,
                        y=y,
                        w=w,
                        h=h
                    )
    


    