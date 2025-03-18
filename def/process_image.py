import cv2
import os

def process_image(frame):
    """Process an image to detect and recognize faces."""
    W, H = frame.shape[1], frame.shape[0]
    
    # Detect faces
    detected_faces = detect_and Recognize_faces(frame)
    
    # Save existing faces
    for idx, (x1, y1, x2, y2) in enumerate(detected_faces):
        face_crop = frame[y1:y2, x1:x2]
        
        # Load known encodings from output directory
        known_encoding_paths = [os.path.join("face_encodings", f"{name}.npy") for name in session_faces.keys()]
        
        results = []
        for i, face in enumerate(face_crops):
            try:
                encoding_path = os.path.join("face_encodings", f"face_{idx}_{i}.npy")
                
                if not os.path.exists(encoding_path):
                    continue
                
                with open(encoding_path, 'rb') as f:
                    encoding = np.load(f)
                    
                    # Perform face recognition
                    distance = dlib.face_recognize(encoding, results[i])
                    print(f"Distance to {name}: {distance}")
                    
                    if distance < 0.75:
                        match_index = i
                        name = get_person_name(encoding)
                        
                        session_faces[name] = True
                        
            except Exception as e:
                continue
                
        # Save new faces
        for j in range(len(results)):
            encoding_path = os.path.join("face_encodings", f"face_{idx}_{j}.npy")
            
            if not os.path.exists(encoding_path):
                np.save(encoding_path, results[j])
                
    return frame
