from django.http import HttpResponseRedirect
from django.shortcuts import render
import cv2
import numpy as np
import os

from sperm_detect import settings

def detect_sperm(request):
    if request.method == 'POST':
        # YOLO modelini yükle
        net = cv2.dnn.readNet(os.path.join('detect_app', 'best.pt'))
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        # Etiketleri yükle
        with open(os.path.join('detect_app', 'coco.names'), 'r') as f:
            classes = [line.strip() for line in f.readlines()]

        # Videodan kareleri al
        video_file = request.FILES['video']
        cap = cv2.VideoCapture(video_file)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Kareyi YOLO modeli ile işle
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # Çıktıları işle
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        # Nesne konumunu bul
                        center_x = int(detection[0] * frame.shape[1])
                        center_y = int(detection[1] * frame.shape[0])
                        w = int(detection[2] * frame.shape[1])
                        h = int(detection[3] * frame.shape[0])
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Non-max suppression uygula
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # İşlenen kareleri göster
            cv2.imshow('Sperm Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    return render(request, 'home.html')

def upload_video(request):
    if request.method == "POST":
        video_file = request.FILES["video"]
        file_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
        with open(file_path, "wb") as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        return HttpResponseRedirect("/")