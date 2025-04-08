import cv2
import numpy as np
import tensorflow as tf
import json

MODEL_PATH = "distract_model_mobilenetv2.h5"
LABELS_PATH = "distract_labels.json"
IMAGE_PATH = "test.jpg"  # 👉 thay bằng đường dẫn ảnh test của bạn

# Load model & nhãn
model = tf.keras.models.load_model(MODEL_PATH)

with open(LABELS_PATH, "r") as f:
    class_indices = json.load(f)
    idx2label = {v: k for k, v in class_indices.items()}

# Dự đoán ảnh
img = cv2.imread(IMAGE_PATH)
img = cv2.resize(img, (224, 224))
img = img.astype("float32") / 255.0
img = np.expand_dims(img, axis=0)

pred = model.predict(img)[0]
class_id = np.argmax(pred)
confidence = pred[class_id] * 100

print(f"🔍 Dự đoán: {idx2label[class_id]} ({confidence:.2f}%)")
