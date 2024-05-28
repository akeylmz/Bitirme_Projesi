import os
from django.db.models.signals import pre_save 
from django.db.models.signals import post_save
from django.dispatch import receiver
import numpy as np
from .models import UserVideo, VideoFrames, FrameLabels
from django.db import models
from django.contrib.auth.models import User
from ultralytics import YOLO
from PIL import Image
import io
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated.


        
        


    