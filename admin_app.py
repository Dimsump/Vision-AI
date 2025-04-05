import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import pickle
import os
import json
from google_drive_utils import upload_to_drive
import util

USER_DATA_FILE = "user.json"

class AdminApp:
    def __init__(self, master=None, admin_name=None):
        self.admin_name = admin_name
        self.window = master or tk.Tk()
        self.window.title("Quản lý tài xế")
        self.window.geometry("1000x700")
        self.window.configure(bg='white')

        # Tiêu đề
        self.label = tk.Label(self.window, text=f"👤 Quản trị viên: {admin_name}", font=("Arial", 14), bg='white')
        self.label.pack(pady=10)

        # Danh sách tài xế
        self.driver_listbox = tk.Listbox(self.window, height=10, width=50)
        self.driver_listbox.pack(pady=20)
        self.load_driver_list()

        # Khung nhập thông tin
        self.driver_info_frame = tk.Frame(self.window, bg='white')
        self.driver_info_frame.pack(pady=10)

        self.driver_name_label = tk.Label(self.driver_info_frame, text="Tên tài xế:", bg='white')
        self.driver_name_label.grid(row=0, column=0)
        self.driver_name_entry = tk.Entry(self.driver_info_frame)
        self.driver_name_entry.grid(row=0, column=1)

        self.cccd_label = tk.Label(self.driver_info_frame, text="Số CCCD:", bg='white')
        self.cccd_label.grid(row=1, column=0)
        self.cccd_entry = tk.Entry(self.driver_info_frame)
        self.cccd_entry.grid(row=1, column=1)

        self.phone_label = tk.Label(self.driver_info_frame, text="Số điện thoại:", bg='white')
        self.phone_label.grid(row=2, column=0)
        self.phone_entry = tk.Entry(self.driver_info_frame)
        self.phone_entry.grid(row=2, column=1)

        self.email_label = tk.Label(self.driver_info_frame, text="Email:", bg='white')
        self.email_label.grid(row=3, column=0)
        self.email_entry = tk.Entry(self.driver_info_frame)
        self.email_entry.grid(row=3, column=1)

        self.alert_sound_label = tk.Label(self.driver_info_frame, text="Chuông cảnh báo:", bg='white')
        self.alert_sound_label.grid(row=4, column=0)
        self.alert_sound_button = tk.Button(self.driver_info_frame, text="Chọn chuông cảnh báo", command=self.change_alert_sound)
        self.alert_sound_button.grid(row=4, column=1)

        # Phân quyền
        self.role_label = tk.Label(self.driver_info_frame, text="Phân quyền:", bg='white')
        self.role_label.grid(row=5, column=0)
        self.role_var = tk.StringVar(value="user")
        self.role_admin_radio = tk.Radiobutton(self.driver_info_frame, text="Admin", variable=self.role_var, value="admin", bg='white')
        self.role_user_radio = tk.Radiobutton(self.driver_info_frame, text="User", variable=self.role_var, value="user", bg='white')
        self.role_admin_radio.grid(row=5, column=1)
        self.role_user_radio.grid(row=5, column=2)

        # Lưu
        self.save_button = tk.Button(self.window, text="Lưu thay đổi", command=self.save_changes)
        self.save_button.pack(pady=20)

        # Đăng xuất
        self.logout_button = tk.Button(self.window, text="🔙 Đăng xuất", command=self.logout)
        self.logout_button.pack(pady=10)

    def load_driver_list(self):
        self.driver_listbox.delete(0, tk.END)
        for file in os.listdir("db"):
            if file.endswith(".pickle"):
                self.driver_listbox.insert(tk.END, file.replace(".pickle", ""))

    def change_alert_sound(self):
        file_path = filedialog.askopenfilename(title="Chọn âm thanh chuông cảnh báo", filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.alert_sound_button.config(text="Đã chọn chuông cảnh báo")
            self.alert_sound = file_path

    def save_changes(self):
        selected_driver = self.driver_listbox.get(tk.ACTIVE)
        if not selected_driver:
            messagebox.showerror("Lỗi", "Vui lòng chọn một tài xế để thay đổi.")
            return

        driver_name = self.driver_name_entry.get()
        cccd = self.cccd_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        alert_sound = self.alert_sound if hasattr(self, "alert_sound") else None
        role = self.role_var.get()

        driver_data = {
            "name": driver_name,
            "cccd": cccd,
            "phone": phone,
            "email": email,
            "alert_sound": alert_sound,
            "role": role
        }

        with open(os.path.join("db", f"{selected_driver}.pickle"), "wb") as f:
            pickle.dump(driver_data, f)

        # Ghi vào user.json nếu là admin/user
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                user_data = json.load(f)
        else:
            user_data = {}

        user_data[selected_driver] = {"role": role, "supervisor": self.admin_name}
        with open(USER_DATA_FILE, "w") as f:
            json.dump(user_data, f, indent=2)

        messagebox.showinfo("Thành công", "Thông tin tài xế đã được lưu.")
        self.load_driver_list()

    def logout(self):
        import login_screen
        self.window.destroy()
        login = login_screen.LoginScreen()
        login.start()

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    admin = AdminApp()
    admin.start()
