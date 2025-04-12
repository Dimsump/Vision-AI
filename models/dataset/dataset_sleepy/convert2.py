import cv2
import os

SOURCE_PATHS = [
    ("Yawning/male",             "../../dataset_sleepy_processed/Yawning"),
]

FRAME_INTERVAL = 10

for VIDEO_DIR, OUTPUT_DIR in SOURCE_PATHS:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for video_file in os.listdir(VIDEO_DIR):
        if video_file.endswith('.avi'):
            video_path = os.path.join(VIDEO_DIR, video_file)
            cap = cv2.VideoCapture(video_path)
            count = 0
            saved = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % FRAME_INTERVAL == 0:
                    filename = f"{os.path.splitext(video_file)[0]}_{saved}.jpg"
                    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), frame)
                    saved += 1
                count += 1
            cap.release()
            print(f"✅ Trích xuất {saved} ảnh từ {video_file}")
