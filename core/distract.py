import cv2
import os
import datetime
import numpy as np
import json
from tensorflow.keras.models import load_model

model = None
try:
    model = load_model("models/distract_model_mobilenetv2.h5")
except Exception as e:
    print("Model loading failed:", e)

# ✅ Load nhãn từ file JSON
with open("models/distract_labels.json", "r") as f:
    label_map = json.load(f)

LABELS = [label for label, idx in sorted(label_map.items(), key=lambda x: x[1])]

# Chỉ cảnh báo nếu thuộc các nhãn này
VALID_DISTRACT_LABELS = ["looking_away", "on_phone"]

IMG_SIZE = (224, 224)

def check_distract(frame, username, warn_dir="db"):
    if model is None:
        print("Model not loaded, skipping prediction.")
        return False

    try:
        img = cv2.resize(frame, IMG_SIZE)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        pred = model.predict(img, verbose=0)
        class_idx = np.argmax(pred)
        label = LABELS[class_idx]

        if label in VALID_DISTRACT_LABELS:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            user_dir = os.path.join(warn_dir, username, "warnings")
            os.makedirs(user_dir, exist_ok=True)
            filepath = os.path.join(user_dir, f"{timestamp}_{label}.jpg")
            cv2.imwrite(filepath, frame)
            print(f"⚠️ Distracted: {label} - Image saved at {filepath}")
            return True
        return False
    except Exception as e:
        print("Error in check_distract:", e)
        return False
