import os
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
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated.

@receiver(post_save, sender=VideoFrames)
def labeling(sender, instance, created, **kwargs):
    if created:
        # Load a model
        model = YOLO(BEST_PT_PATH)  # pretrained YOLOv8n model
        frame_path = instance.frame.path
        frame_name = os.path.splitext(os.path.basename(frame_path))[0]

        # Run batched inference on a list of images
        results=model.predict(frame_path)

        #labels_dir = os.path.join('media', instance.video.user.username, str(instance.video.id), 'labels')
        #os.makedirs(labels_dir, exist_ok=True)  # Klasörü oluştur (varsa hata vermez)
        #label_file_path = os.path.join(labels_dir, frame_name + '.txt')
        #with open(label_file_path, 'w') as label_file:
        for r in results:
            if r.boxes.xywh.tolist() is not None:
                 for c in r.boxes.xywhn.tolist(): # To get the coordinates.

                    x, y, w, h = c[0], c[1], c[2], c[3] # x, y are the center coordinates.
                    #label_file.write(f'{x} {y} {w} {h}\n')  # Etiket bilgilerini dosyaya yaz

                    label_f= FrameLabels.objects.create(
                        labels_frame=instance,
                        x=x,
                        y=y,
                        w=w,
                        h=h
                    )
        


    