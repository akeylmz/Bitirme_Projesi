cap = cv2.VideoCapture(video_path)
            
    
cap.set(cv2.CAP_PROP_POS_FRAMES, frame-1)

                
ret, img = cap.read()

if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    break

                
cv2.imwrite(os.path.join(output_path, f'frame{frame}.jpg'), img)

              
    filename = f'frame{frame}.txt'

                
    with open(os.path.join(output_path, filename), 'a') as f:
                    
    x = sequence['x'] / 100
    y = sequence['y'] / 100
    width = sequence['width'] / 100
    height = sequence['height'] / 100
    x_center = x + width / 2
    y_center = y + height / 2
    f.write(f"{cell_type} {x_center} {y_center} {width} {height}\n")


cap.release()
cv2.destroyAllWindows()
