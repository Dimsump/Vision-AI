import os
from PIL import Image
import imghdr

VALID_FORMATS = {"jpeg", "png", "bmp", "gif"}
DATASET_PATH = "dataset/dataset_distract"

bad_files = []

for root, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        file_path = os.path.join(root, file)

        # Bỏ qua file 0 byte
        if os.path.getsize(file_path) < 1024:
            print(f"❌ File quá nhỏ hoặc rỗng: {file_path}")
            bad_files.append(file_path)
            continue

        # Kiểm tra định dạng thực tế bằng imghdr
        format_detected = imghdr.what(file_path)
        if format_detected not in VALID_FORMATS:
            print(f"❌ Không phải ảnh hợp lệ (thực tế là {format_detected}): {file_path}")
            bad_files.append(file_path)
            continue

        # Cố gắng mở ảnh bằng PIL
        try:
            with Image.open(file_path) as img:
                img.convert("RGB")
        except Exception as e:
            print(f"❌ Lỗi khi đọc ảnh bằng PIL: {file_path} → {e}")
            bad_files.append(file_path)

print(f"\n🧹 Tổng số file lỗi/phát hiện trá hình: {len(bad_files)}")

if bad_files:
    confirm = input("Bạn có muốn xoá toàn bộ ảnh lỗi này không? (y/n): ")
    if confirm.lower() == "y":
        for f in bad_files:
            try:
                os.remove(f)
                print(f"🗑️ Đã xoá: {f}")
            except Exception as e:
                print(f"⚠️ Không thể xoá: {f} → {e}")
    else:
        print("❌ Đã huỷ xoá.")
else:
    print("✅ Không phát hiện ảnh trá hình.")
