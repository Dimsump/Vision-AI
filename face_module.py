# face_recognition.py
import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

class recognize_face:
    def __init__(self, db_path="./db"):
        self.db_path = db_path
        self.known_encodings = {}
        self.load_known_faces()

    def load_known_faces(self):
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        for file in os.listdir(self.db_path):
            if file.endswith(".npy"):
                name = file[:-4]
                encoding = np.load(os.path.join(self.db_path, file))
                self.known_encodings[name] = encoding
        print(f"✅ Loaded users: {list(self.known_encodings.keys())}")

    def save_new_face(self, name, face_crop):
        rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if encodings:
            np.save(os.path.join(self.db_path, f"{name}.npy"), encodings[0])
            self.known_encodings[name] = encodings[0]
            print(f"✅ New face saved: {name}")

    def match_face(self, face_crop):
        rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            return "Unknown"
        for name, known_encoding in self.known_encodings.items():
            match = face_recognition.compare_faces([known_encoding], encodings[0], tolerance=0.5)[0]
            if match:
                return name
        return "Unknown"


    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        for top, right, bottom, left in face_locations:
            face_crop = frame[top:bottom, left:right]
            name = self.match_face(face_crop)
            if not name:
                name = "Unknown"  # Hoặc dùng input hoặc pop-up tùy bạn
                self.save_new_face(name, face_crop)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        return frame
