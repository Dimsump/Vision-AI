import cv2
import os

# ✅ Cập nhật đường dẫn chứa video sleepy
base_video_path = "D:\KLTN\AI\models\dataset\dataset_distract"

videos = {
    "blink": [
        "blink.mp4",
        "blink(1).mp4",
        "blink(2).mp4",
        "blink(3).mp4",
    ]
}

# ✅ Nơi xuất ảnh
output_base = "D:/KLTN/AI/dataset/dataset_distract"
frame_interval = 10  # lấy 1 ảnh mỗi 10 frame

def extract_frames(video_path, output_dir, interval=10):
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            frame_resized = cv2.resize(frame, (224, 224))
            filename = os.path.join(
                output_dir,
                f"{os.path.basename(video_path).split('.')[0]}_{frame_id}.jpg"
            )
            cv2.imwrite(filename, frame_resized)
            count += 1

        frame_id += 1

    cap.release()
    print(f"✅ {video_path} → {count} ảnh → {output_dir}")

# ✅ Lặp qua video
for label, file_list in videos.items():
    out_dir = os.path.join(output_base, label)
    os.makedirs(out_dir, exist_ok=True)

    for filename in file_list:
        full_path = os.path.normpath(os.path.join(base_video_path, filename))
        if os.path.isfile(full_path):
            extract_frames(full_path, out_dir, frame_interval)
        else:
            print(f"❌ Không tìm thấy video: {full_path}")
