import os
import shutil

# Danh sách các thư mục hoặc file cần loại bỏ để làm sạch trước khi commit
cleanup_targets = [
    "__pycache__",
    ".ipynb_checkpoints",
    ".DS_Store",
    "temp",
    "token.pickle",
    "*.pyc",
    "*.pyo",
]

# Hàm đệ quy xóa file/thư mục theo tiêu chí
def clean_project_structure(base_path="."):
    removed_items = []
    for root, dirs, files in os.walk(base_path):
        for name in dirs:
            if name in cleanup_targets:
                path = os.path.join(root, name)
                shutil.rmtree(path, ignore_errors=True)
                removed_items.append(path)
        for name in files:
            full_path = os.path.join(root, name)
            if any(name.endswith(pattern.replace("*", "")) for pattern in cleanup_targets):
                try:
                    os.remove(full_path)
                    removed_items.append(full_path)
                except:
                    pass
    return removed_items

if __name__ == "__main__":
    removed = clean_project_structure()
    print("🧹 Đã xoá các file/thư mục sau:")
    for item in removed:
        print(" -", item)
