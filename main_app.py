import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import datetime
import os
import threading
import time
import face_recognition
import pickle
from distract import check_distract
from sleepy import check_sleepy
from google_drive_utils import upload_to_drive

class MainApp:
    def __init__(self, master, user_name):
        self.master = master
        self.master.title("🧠 Hệ thống giám sát tài xế AI")
        self.master.geometry("1200x700")
        self.user_name = user_name
        self.recording = False
        self.start_time = None
        self.elapsed_time = 0

        # Layout
        self.left_frame = tk.Frame(self.master, bg="white")
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_frame = tk.Frame(self.master, bg="white")
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.cam_label = tk.Label(self.left_frame)
        self.cam_label.pack()

        # Info
        self.title_label = tk.Label(self.right_frame, text=f"👤 Tài xế: {self.user_name}", font=("Arial", 14, 'bold'), bg='white')
        self.title_label.pack(pady=5)

        self.time_label = tk.Label(self.right_frame, text="", font=("Arial", 12), fg="green", bg="white")
        self.time_label.pack()

        self.recording_label = tk.Label(self.right_frame, text="Ghi: 00:00:00", font=("Arial", 12, 'bold'), fg="green", bg="white")
        self.recording_label.pack(pady=5)

        self.start_button = tk.Button(self.right_frame, text="▶️ Bắt đầu ghi hình", bg="green", fg="white", command=self.start_recording)
        self.start_button.pack(pady=2)

        self.stop_button = tk.Button(self.right_frame, text="⏹ Dừng ghi và lưu", bg="gray", fg="white", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=2)

        self.warning_button = tk.Button(self.right_frame, text="🛑 Lịch sử cảnh báo", bg="red", fg="white", command=self.show_warnings)
        self.warning_button.pack(pady=2)

        self.history_button = tk.Button(self.right_frame, text="📂 Lịch sử", bg="lightblue", command=self.show_video_history)
        self.history_button.pack(pady=2)

        self.profile_button = tk.Button(self.right_frame, text="👤 Hồ sơ người dùng", command=self.show_profile)
        self.profile_button.pack(pady=2)

        self.logout_button = tk.Button(self.right_frame, text="🔶 Đăng xuất", bg="orange", command=self.logout)
        self.logout_button.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.update_frame()
        self.update_time()

    def update_time(self):
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=now)
        if self.recording:
            elapsed = time.time() - self.start_time
            self.recording_label.config(text=f"Ghi: {datetime.timedelta(seconds=int(elapsed))}")
        self.master.after(1000, self.update_time)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_locations = face_recognition.face_locations(rgb)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)
                cv2.putText(frame, self.user_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255, 0, 255), 2)

            if self.recording:
                self.video_writer.write(frame)
                check_distract(frame, self.user_name)
                check_sleepy(frame, self.user_name)

            rgb_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_display)
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)

        self.master.after(10, self.update_frame)

    def start_recording(self):
        folder = os.path.join("db", self.user_name, "journey")
        os.makedirs(folder, exist_ok=True)
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_hanhtrinh.avi"
        self.video_path = os.path.join(folder, filename)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
        self.recording = True
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_recording(self):
        self.recording = False
        self.video_writer.release()
        messagebox.showinfo("Xong", f"✅ Đã lưu hành trình vào: {self.video_path}")
        upload_to_drive(self.video_path, folder_name="Videos")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def show_warnings(self):
        folder = os.path.join("db", self.user_name, "warnings")
        if not os.path.exists(folder):
            messagebox.showinfo("Thông báo", "Chưa có cảnh báo nào.")
            return
        files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
        if not files:
            messagebox.showinfo("Thông báo", "Không tìm thấy ảnh cảnh báo.")
            return
        top = tk.Toplevel(self.master)
        top.title("Lịch sử cảnh báo")
        for f in files:
            tk.Label(top, text=f).pack()

    def show_video_history(self):
        video_dir = os.path.join("db", self.user_name, "journey")
        if not os.path.exists(video_dir):
            messagebox.showinfo("Thông báo", "Chưa có video hành trình nào")
            return

        files = [f for f in os.listdir(video_dir) if f.endswith(".avi")]
        if not files:
            messagebox.showinfo("Thông báo", "Không tìm thấy video phù hợp")
            return

        win = tk.Toplevel()
        win.title("Lịch sử hành trình")
        listbox = tk.Listbox(win, width=60)
        listbox.pack(padx=10, pady=10)

        for f in files:
            listbox.insert(tk.END, f)

        def play_video(event):
            selection = listbox.curselection()
            if not selection:
                return
            filename = listbox.get(selection[0])
            path = os.path.join(video_dir, filename)
            cap = cv2.VideoCapture(path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                face_locations = face_recognition.face_locations(frame)
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)
                    cv2.putText(frame, self.user_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                cv2.imshow(f"📼 {filename}", frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

        listbox.bind("<Double-Button-1>", play_video)

    def show_profile(self):
        profile_path = os.path.join("db", f"{self.user_name}.pickle")
        if not os.path.exists(profile_path):
            messagebox.showinfo("Thông báo", "Chưa có thông tin hồ sơ.")
            return

        with open(profile_path, "rb") as f:
            data = pickle.load(f)

        top = tk.Toplevel(self.master)
        top.title("Hồ sơ người dùng")

        fields = {}
        row = 0
        for key, value in data.items():
            tk.Label(top, text=f"{key.capitalize()}:", anchor="w").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            ent = tk.Entry(top, width=40)
            ent.insert(0, str(value) if value else "")
            ent.grid(row=row, column=1, padx=10, pady=5)
            fields[key] = ent
            row += 1

        def choose_alert():
            file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
            if file_path:
                if "alert_sound" not in fields:
                    fields["alert_sound"] = tk.Entry(top, width=40)
                    fields["alert_sound"].grid(row=row, column=1, padx=10, pady=5)
                fields["alert_sound"].delete(0, tk.END)
                fields["alert_sound"].insert(0, file_path)

        btn_alert = tk.Button(top, text="🔊 Chọn chuông cảnh báo", command=choose_alert)
        btn_alert.grid(row=row, column=1, pady=5, sticky="w")

        def save_changes():
            for key in fields:
                data[key] = fields[key].get()
            with open(profile_path, "wb") as f:
                pickle.dump(data, f)
            messagebox.showinfo("✅", "Đã lưu thay đổi thành công.")
            top.destroy()

        tk.Button(top, text="💾 Lưu thay đổi", bg="green", fg="white", command=save_changes).grid(row=row+1, column=1, pady=10, sticky="e")

    def logout(self):
        self.cap.release()
        self.master.destroy()
        from login_screen import LoginScreen
        root = tk.Tk()
        app = LoginScreen(root)
        app.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root, "trung")
    root.mainloop()
