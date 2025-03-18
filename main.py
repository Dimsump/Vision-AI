import os
import argparse
import cv2
import time
import mediapipe as mp
import numpy as np

face_database = {}

session_faces = {}

def load_existing_users(output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for person_name in os.listdir(output_dir):
        person_path = os.path.join(output_dir, person_name)
        if os.path.isdir(person_path):
            face_database[person_name] = [os.path.join(person_path, img) for img in os.listdir(person_path) if img.endswith(".jpg")]
    print(f" Loaded Users: {list(face_database.keys())}")
    
def match_face(face_crop):

    if face_crop is None or face_crop.size == 0:
        return None 

    gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) 

    for person_name, face_images in face_database.items():
        for stored_face_path in face_images:
            stored_face = cv2.imread(stored_face_path, cv2.IMREAD_GRAYSCALE)
            if stored_face is None:
                continue

            stored_face = cv2.resize(stored_face, (gray_face.shape[1], gray_face.shape[0]))

            result = cv2.matchTemplate(gray_face, stored_face, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(result)

            if similarity > 0.75: 
                return person_name 

    return None    

def get_person_name(face_id, face_crop):
    
    if face_id in session_faces:
        return session_faces[face_id]
    
    matched_name = match_face(face_crop)
    if matched_name:
        session_faces[face_id] = matched_name  # ✅ Store name in session
        return matched_name

    name = input(f" New face detected! Enter name for person {face_id} (Press Enter for 'Unknown'): ").strip()
    if name == "":
        name = "Unknown"

    session_faces[face_id] = name  
    return name  
def process_img(img, face_detection, output_dir):
    
    H, W, _ = img.shape
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    out = face_detection.process(img_rgb)

    
    if out.detections is not None:
        for i, detection in enumerate(out.detections):  
            location_data = detection.location_data
            bbox = location_data.relative_bounding_box
            
            x1 = int(bbox.xmin * W)  
            y1 = int(bbox.ymin * H)  
            w = int(bbox.width * W)  
            h = int(bbox.height * H) 
            
            face_crop = img[y1:y1 + h, x1:x1 + w] if y1 + h <= H and x1 + w <= W else None
            
            if face_crop is not None and face_crop.size != 0:
                person_name = get_person_name(i, face_crop)
            
            person_output_dir = os.path.join(output_dir, person_name)
            if not os.path.exists(person_output_dir):
                os.makedirs(person_output_dir)
            
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
            text_y = y1 - 10 if y1 - 10 > 20 else y1 + 20
            
            cv2.putText(img, person_name, (x1, y1 -10), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0), 2)
            
            face_filename = os.path.join(person_output_dir, f"{person_name}_face_{i}.jpg")
            cv2.imwrite(face_filename, face_crop)
            print(f" Saved detected face: {face_filename}")

    return img

args = argparse.ArgumentParser()

args.add_argument("--mode", default='webcam')
args.add_argument("--filePath", default= None)

args = args.parse_args()

output_dir = "./output"
load_existing_users(output_dir) 

# detect faces
mp_face_detection = mp.solutions.face_detection 

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    
    if args.mode in ["image"]:
        # read image
        img = cv2.imread(args.filePath)
    
        img = process_img(img, face_detection)

        # save image

        cv2.imwrite(os.path.join(output_dir, 'output.jpg'), img)
    elif args.mode in['video']:
                
        cap = cv2.VideoCapture(args.filePath)
        ret, frame = cap.read()
        
        output_video = cv2.VideoWriter(os.path.join(output_dir, 'output.mp4'),
                                        cv2.VideoWriter_fourcc(*'MP4V'),
                                        25,
                                        (frame.shape[1], frame.shape[0]))

        while ret:
            frame = process_img(frame, face_detection)  
            output_video.write(frame)
            ret, frame = cap.read()
        
        cap.release()
        output_video.release()
        
    elif args.mode in['webcam']:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print(" Error: Could not open webcam.")
            exit()
            
        start_time = time.time() 
        duration = 30 
        
        ret, frame = cap.read()
        while ret:
            frame = process_img(frame, face_detection, output_dir)  
            cv2.imshow('Webcam Face Detection', frame)
            
            # if time.time() - start_time > duration:
            #     print(" Webcam session ended after 30 seconds.")
            #     break

            if cv2.waitKey(1) & 0xFF == ord('q'):  
                print(" Webcam session manually stopped.")
                break
            
            ret, frame = cap.read() 
        cap.release()
        cv2.destroyAllWindows()