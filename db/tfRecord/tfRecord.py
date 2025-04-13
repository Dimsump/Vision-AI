import tensorflow as tf
import io
import os
from PIL import Image

TFRECORD_PATH = "safe-looking-away.tfrecord"
OUTPUT_DIR = "extracted_jpg"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hàm parse
def parse_tfrecord_fn(example_proto):
    feature_description = {
        "image/encoded": tf.io.FixedLenFeature([], tf.string),
    }
    return tf.io.parse_single_example(example_proto, feature_description)

# Đọc TFRecord và trích ảnh
raw_dataset = tf.data.TFRecordDataset(TFRECORD_PATH)
parsed_dataset = raw_dataset.map(parse_tfrecord_fn)

count = 0
for record in parsed_dataset:
    img_bytes = record["image/encoded"].numpy()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img.save(os.path.join(OUTPUT_DIR, f"looking_away_{count:04d}.jpg"))
    count += 1

print(f"✅ Đã trích xuất {count} ảnh vào thư mục '{OUTPUT_DIR}'")
