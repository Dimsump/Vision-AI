import os
import numpy as np

def load_existing_users(output_dir="face_encodings"):
    """Load existing users' face encodings from the output directory."""
    users = {}
    
    if not os.path.exists(output_dir):
        return users
        
    for file in os.listdir(output_dir):
        if os.path.isfile(os.path.join(output_dir, file)) and file.endswith('.npy'):
            encoding_path = os.path.join(output_dir, file)
            
            try:
                with open(encoding_path, 'rb') as f:
                    encoding = np.load(f)
                    
                    # Map encodings to names using your predefined logic
                    name = get_person_name(encoding)  # Replace this with actual mapping
                    users[name] = True
                
            except Exception as e:
                print(f"Error loading face encoding: {e}")
                
    return users
