import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import json
import os

from safe_image_dataset import create_safe_dataset

# Cấu hình
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 20
DATASET_PATH = "dataset/dataset_distract"
MODEL_NAME = "distract_model_mobilenetv2.h5"
LABELS_FILE = "distract_labels.json"

# Load dataset an toàn
train_ds, val_ds, class_names = create_safe_dataset(
    DATASET_PATH,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    validation_split=0.2
)

# Lưu nhãn
class_indices = {name: i for i, name in enumerate(class_names)}
with open(LABELS_FILE, "w") as f:
    json.dump(class_indices, f)
print("✅ Lưu class mapping:", class_indices)

# Mô hình
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
output = Dense(len(class_names), activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=output)
model.compile(optimizer=Adam(1e-4), loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Callback
early_stop = EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
checkpoint = ModelCheckpoint(MODEL_NAME, monitor="val_accuracy", save_best_only=True)

# Huấn luyện
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=[early_stop, checkpoint])

# Biểu đồ
plt.plot(history.history["accuracy"], label="Train Acc")
plt.plot(history.history["val_accuracy"], label="Val Acc")
plt.title("Accuracy")
plt.legend()
plt.show()

plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.title("Loss")
plt.legend()
plt.show()

print(f"✅ Huấn luyện hoàn tất, đã lưu mô hình: {MODEL_NAME}")
