import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from datetime import datetime
import os

MODEL_PATH = "models/sleepy_model_mobilenetv2.h5"

try:
    model = load_model(MODEL_PATH)
except Exception as e:
    print(f"Model loading failed: {str(e)}")
    model = None

CLASSES = ["awake", "sleepy"]

def preprocess_frame(frame):
    img = cv2.resize(frame, (224, 224))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)

def check_sleepy(frame, user_name="Unknown", output_folder="warnings"):
    if model is None:
        print("Model not loaded, skipping prediction.")
        return

    input_img = preprocess_frame(frame)
    preds = model.predict(input_img, verbose=0)
    class_id = np.argmax(preds)
    label = CLASSES[class_id]
    confidence = preds[0][class_id]

    if label == "sleepy":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        warning_text = f"😴 {label} ({confidence*100:.1f}%)"
        cv2.putText(frame, warning_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"{user_name}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        os.makedirs(output_folder, exist_ok=True)
        filename = f"ai_sleepy_{user_name}_{timestamp}.jpg"
        filepath = os.path.join(output_folder, filename)
        cv2.imwrite(filepath, frame)