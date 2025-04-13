import tensorflow as tf
import os
from PIL import Image

def is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except:
        return False

def get_valid_image_paths_and_labels(directory, class_names):
    image_paths = []
    labels = []
    for label_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(directory, class_name)
        for fname in os.listdir(class_dir):
            fpath = os.path.join(class_dir, fname)
            if is_valid_image(fpath):
                image_paths.append(fpath)
                labels.append(label_idx)
            else:
                print(f"❌ Bỏ ảnh lỗi: {fpath}")
    return image_paths, labels

def create_safe_dataset(directory, image_size=(224, 224), batch_size=16, validation_split=0.2, seed=123):
    class_names = sorted(os.listdir(directory))
    all_image_paths, all_labels = get_valid_image_paths_and_labels(directory, class_names)

    ds = tf.data.Dataset.from_tensor_slices((all_image_paths, all_labels))
    ds = ds.shuffle(buffer_size=len(all_image_paths), seed=seed)

    val_size = int(len(all_image_paths) * validation_split)
    val_ds = ds.take(val_size)
    train_ds = ds.skip(val_size)

    def process_path(file_path, label):
        img = tf.io.read_file(file_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, image_size)
        img = tf.cast(img, tf.float32) / 255.0
        return img, label

    train_ds = train_ds.map(process_path).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(process_path).batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names
