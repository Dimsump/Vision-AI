import os
import numpy as np

def match_faces(detected_faces, known_encoding_paths):
    """Match detected faces against known encodings."""
    matches = {}
    
    for path in known_encoding_paths:
        with open(path, 'rb') as f:
            encoding = np.load(f)
            
            distances = []
            for face in detected_faces:
                distance = dlib.face_recognize(encoding, face)
                distances.append(distance)
                
                if distance < 0.75:  # Set a threshold
                    matches[face_index] = name
                    break
            
    return matches
