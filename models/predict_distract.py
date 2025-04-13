import os
import cv2
import numpy as np
import tensorflow as tf
import json

# === Cấu hình ===
MODEL_PATH = "distract_model_mobilenetv2.h5"
LABELS_PATH = "distract_labels.json"
TEST_FOLDER = "D:/KLTN/AI/models/dataset_distract_processed/blink"

# === Load model và nhãn
model = tf.keras.models.load_model(MODEL_PATH)
with open(LABELS_PATH, "r") as f:
    label_map = json.load(f)
    idx2label = {v: k for k, v in label_map.items()}

# === Duyệt tất cả ảnh trong thư mục
image_files = [f for f in os.listdir(TEST_FOLDER) if f.lower().endswith(('.jpg', '.png'))]

for filename in image_files:
    img_path = os.path.join(TEST_FOLDER, filename)
    img = cv2.imread(img_path)
    if img is None:
        print(f"⚠️ Không đọc được ảnh: {filename}")
        continue

    img = cv2.resize(img, (224, 224))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img)[0]
    class_id = np.argmax(pred)
    confidence = pred[class_id] * 100
    label = idx2label[class_id]

    print(f"{filename:35} → 🧠 {label.upper():15} ({confidence:.2f}%)")
