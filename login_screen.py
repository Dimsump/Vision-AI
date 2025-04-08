import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
import pickle
import json
import util
from google_drive_utils import get_service, upload_to_drive
from main_app import MainApp
from admin_app import AdminApp

USER_DATA_FILE = "user.json"

class LoginScreen:
    def __init__(self, master=None):
        self.window = master or tk.Tk()
        self.window.title("Face Login System")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        self.window.configure(bg='white')
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        self.db_dir = "db"
        os.makedirs(self.db_dir, exist_ok=True)

        self.title_label = tk.Label(self.window,
                                    text="🎯 Hệ thống giám sát tài xế - Đăng nhập bằng khuôn mặt",
                                    font=("Arial", 16, 'bold'),
                                    bg="white",
                                    fg="black")
        self.title_label.place(x=150, y=10)

        self.cam_label = util.get_img_label(self.window, width=640, height=480)
        self.cam_label.place(x=30, y=50)

        self.login_btn = util.get_button(self.window, "🚗 Đăng nhập", "green", self.login)
        self.login_btn.place(x=700, y=150)

        self.register_btn = util.get_button(self.window, "📝 Đăng ký", "gray", self.register_user, fg='black')
        self.register_btn.place(x=700, y=220)

        self.quit_btn = util.get_button(self.window, "❌ Thoát", "red", self.window.destroy)
        self.quit_btn.place(x=700, y=290)

        self.cap = cv2.VideoCapture(0)
        self.update_cam()

    def update_cam(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)
        self.cam_label.after(20, self.update_cam)

    def recognize_face(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            return None
        user_encoding = encodings[0]

        for file in os.listdir(self.db_dir):
            if file.endswith(".pickle"):
                with open(os.path.join(self.db_dir, file), "rb") as f:
                    known_encoding = pickle.load(f)
                result = face_recognition.compare_faces([known_encoding], user_encoding, tolerance=0.5)
                if result[0]:
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
        if name:
            role = self.get_user_role(name)
            if not role:
                util.msg_box("Lỗi", f"Người dùng '{name}' chưa có trong hệ thống")
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
        else:
            util.msg_box("Thất bại", "Không nhận diện được khuôn mặt! Vui lòng đăng ký nếu bạn là người mới.")

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

        util.msg_box("Thành công", f"✅ Đã đăng ký người dùng {name} và tải ảnh lên Google Drive.")

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    login = LoginScreen()
    login.start()
