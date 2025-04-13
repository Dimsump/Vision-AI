from PIL import Image
import os

DATASET_PATH = "dataset/dataset_distract"
bad_files = []

for root, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            with Image.open(file_path) as img:
                img.convert("RGB")  # Mạnh hơn verify
        except Exception as e:
            print(f"❌ Lỗi ảnh: {file_path} → {e}")
            bad_files.append(file_path)

print(f"\n🧹 Tổng số file lỗi (nâng cao): {len(bad_files)}")

if bad_files:
    confirm = input("\nBạn có muốn xoá tất cả các ảnh lỗi? (y/n): ")
    if confirm.lower() == "y":
        for file_path in bad_files:
            try:
                os.remove(file_path)
                print(f"🗑️ Đã xoá: {file_path}")
            except Exception as e:
                print(f"⚠️ Không thể xoá {file_path}: {e}")
    else:
        print("❌ Đã huỷ xoá file.")
else:
    print("✅ Không phát hiện ảnh lỗi nâng cao.")
