import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
import pickle
import json
import util
from cloud.google_drive_utils import get_service, upload_to_drive
from UI.main_app import MainApp
from UI.admin_app import AdminApp

USER_DATA_FILE = "user.json"

class LoginScreen:
    def __init__(self, master=None):
        self.window = master or tk.Tk()
        self.window.title("Face Login System")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        self.window.configure(bg='#f5f6f5')  # Màu nền nhẹ, giống web
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.db_dir = "db"
        os.makedirs(self.db_dir, exist_ok=True)

        # Cấu hình style cho giao diện
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
        self.style.configure("TLabel", font=("Segoe UI", 14), background="#f5f6f5")
        
        # Container chính
        self.main_container = tk.Frame(self.window, bg="#f5f6f5")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Tiêu đề
        self.title_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.title_frame.pack(fill="x", pady=(0, 20))
        self.title_label = tk.Label(self.title_frame,
                                    text="🎯 Hệ Thống Giám Sát Tài Xế - Đăng Nhập Bằng Khuôn Mặt",
                                    font=("Segoe UI", 18, "bold"),
                                    bg="#f5f6f5",
                                    fg="#2c3e50")
        self.title_label.pack()

        # Nội dung chính (chia thành 2 cột: video và nút)
        self.content_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.content_frame.pack(fill="both", expand=True)

        # Khung video
        self.video_frame = tk.Frame(self.content_frame, bg="#ffffff", bd=2, relief="flat")
        self.video_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.cam_label = util.get_img_label(self.video_frame, width=640, height=480)
        self.cam_label.pack(pady=10, padx=10)

        # Khung nút điều khiển
        self.control_frame = tk.Frame(self.content_frame, bg="#f5f6f5")
        self.control_frame.pack(side="right", fill="y", padx=20)

        # Các nút với hiệu ứng web
        button_style = {
            "font": ("Segoe UI", 12, "bold"),
            "width": 15,
            "pady": 10,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        # Nút Đăng nhập
        self.login_btn = tk.Button(self.control_frame,
                                   text="🚗 Đăng nhập",
                                   bg="#28a745",  # Giữ màu xanh
                                   fg="white",
                                   command=self.login,
                                   **button_style)
        self.login_btn.pack(pady=10, fill="x")
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#218838"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg="#28a745"))

        # Nút Đăng ký
        self.register_btn = tk.Button(self.control_frame,
                                      text="📝 Đăng ký",
                                      bg="#6c757d",  # Giữ màu xám
                                      fg="white",
                                      command=self.register_user,
                                      **button_style)
        self.register_btn.pack(pady=10, fill="x")
        self.register_btn.bind("<Enter>", lambda e: self.register_btn.config(bg="#5a6268"))
        self.register_btn.bind("<Leave>", lambda e: self.register_btn.config(bg="#6c757d"))

        # Nút Thoát
        self.quit_btn = tk.Button(self.control_frame,
                                  text="❌ Thoát",
                                  bg="#dc3545",  # Giữ màu đỏ
                                  fg="white",
                                  command=self.window.destroy,
                                  **button_style)
        self.quit_btn.pack(pady=10, fill="x")
        self.quit_btn.bind("<Enter>", lambda e: self.quit_btn.config(bg="#c82333"))
        self.quit_btn.bind("<Leave>", lambda e: self.quit_btn.config(bg="#dc3545"))

        # Khởi tạo webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            util.msg_box("Lỗi", "Không thể mở webcam!")
            self.window.destroy()
            return

        self.update_cam()

    def update_cam(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)
        self.cam_label.after(20, self.update_cam)

    def recognize_face(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if not encodings:
            return None

        for user_encoding in encodings:
            for file in os.listdir(self.db_dir):
                if file.endswith(".pickle"):
                    with open(os.path.join(self.db_dir, file), "rb") as f:
                        known_encoding = pickle.load(f)
                    match = face_recognition.compare_faces([known_encoding], user_encoding, tolerance=0.5)
                    if match[0]:
                        return file.replace(".pickle", "")
        return None

    def get_user_role(self, username):
        if not os.path.exists(USER_DATA_FILE):
            return None
        with open(USER_DATA_FILE, "r") as f:
            users = json.load(f)
            return users.get(username, {}).get("role", None)

    def login(self):
        name = self.recognize_face(self.current_frame)
        if not name:
            util.msg_box("Thất bại", "Không nhận diện được khuôn mặt! Vui lòng đăng ký nếu bạn là người mới.")
            return

        role = self.get_user_role(name)
        if not role:
            util.msg_box("Lỗi", f"Người dùng '{name}' chưa được đăng ký trong hệ thống.")
            return

        try:
            self.gdrive = get_service()
        except Exception as e:
            util.msg_box("Lỗi OAuth", f"Không thể kết nối Google Drive:\n{str(e)}")
            return

        util.msg_box("Đăng nhập thành công", f"Xin chào {name}! Đang mở hệ thống giám sát...")
        self.cap.release()
        self.window.destroy()

        app_root = tk.Tk()
        if role == "admin":
            app = AdminApp(master=app_root, admin_name=name)
        else:
            app = MainApp(master=app_root, user_name=name)
        app_root.mainloop()

    def register_user(self):
        name = util.prompt_text("Nhập tên đăng ký")
        if not name:
            return

        rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            util.msg_box("Lỗi", "Không tìm thấy khuôn mặt để đăng ký.")
            return

        new_encoding = encodings[0]

        for file in os.listdir(self.db_dir):
            if file.endswith(".pickle"):
                with open(os.path.join(self.db_dir, file), "rb") as f:
                    known_encoding = pickle.load(f)
                matched = face_recognition.compare_faces([known_encoding], new_encoding, tolerance=0.5)
                if matched[0]:
                    util.msg_box("Trùng khuôn mặt", f"Khuôn mặt này đã được đăng ký với tên: {file.replace('.pickle', '')}")
                    return

        with open(os.path.join(self.db_dir, f"{name}.pickle"), "wb") as f:
            pickle.dump(new_encoding, f)

        img_path = os.path.join("temp", f"{name}_face.jpg")
        os.makedirs("temp", exist_ok=True)
        cv2.imwrite(img_path, self.current_frame)

        try:
            self.gdrive = get_service()
            upload_to_drive(img_path, folder_name="RegisteredFaces")
        except Exception as e:
            util.msg_box("Lỗi OAuth", f"Không thể upload ảnh lên Google Drive:\n{str(e)}")
            return

        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
        else:
            users = {}

        users[name] = {
            "role": "driver",
            "supervisor": name
        }

        with open(USER_DATA_FILE, "w") as f:
            json.dump(users, f, indent=2)

        util.msg_box("Thành công", f"✅ Đã đăng ký người dùng {name} và tải ảnh lên Google Drive.")

    def start(self):
        self.window.mainloop()

    def __del__(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    login = LoginScreen()
    login.start()