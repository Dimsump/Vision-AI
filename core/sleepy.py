
import cv2
import os
import datetime
import numpy as np
from tensorflow.keras.models import load_model

model = None
try:
    model = load_model("models/sleepy_model_mobilenetv2.h5")
except Exception as e:
    print("Model loading failed:", e)

LABELS = ["normal", "micro_sleep", "yawning"]
IMG_SIZE = (224, 224)

def check_sleepy(frame, username, warn_dir="db"):
    if model is None:
        print("Model not loaded, skipping prediction.")
        return

    try:
        img = cv2.resize(frame, IMG_SIZE)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        pred = model.predict(img)
        class_idx = np.argmax(pred)
        label = LABELS[class_idx]

        if label != "normal":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            user_dir = os.path.join(warn_dir, username, "warnings")
            os.makedirs(user_dir, exist_ok=True)
            filepath = os.path.join(user_dir, f"{timestamp}_{label}.jpg")
            cv2.imwrite(filepath, frame)
            print(f"⚠️ Sleepy: {label} - Image saved at {filepath}")
    except Exception as e:
        print("Error in check_sleepy:", e)
