import dlib
import cv2
import numpy as np

def detect_faces(frame):
    return dlib.face_utils_detector(frame)

def detect_and Recognize_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = dlib.face_utils_detector(gray)
    
    results = []
    for face in faces:
        (left, top, right, bottom) = face.left(), face.top(), face.right(), face.bottom()
        
        # Ensure coordinates are within image bounds
        x1 = max(0, left)
        y1 = max(0, top)
        x2 = min(W, right)
        y2 = min(H, bottom)
        
        face_crop = frame[y1:y2, x1:x2]
        
        results.append((x1, y1, x2, y2))
    
    return results
