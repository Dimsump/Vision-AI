import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import datetime
import os
import time
import face_recognition
import pickle
import pygame
import threading
from core.distract import check_distract
from core.sleepy import check_sleepy
from cloud.google_drive_utils import upload_to_drive

class MainApp:
    def __init__(self, master, user_name):
        self.master = master
        self.master.title("🧠 Hệ Thống Giám Sát Tài Xế AI")
        self.master.geometry("1200x700")
        self.master.configure(bg="#f5f6f5")
        self.user_name = user_name
        self.recording = False
        self.start_time = None
        self.elapsed_time = 0
        self.cap = None
        self.video_writer = None
        self.current_frame = None
        self.sound_playing = False  # Trạng thái phát âm thanh

        # Khởi tạo pygame mixer
        pygame.mixer.init()

        # Cấu hình style
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Segoe UI", 12), background="#f5f6f5")
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f5f6f5")

        # Container chính
        self.main_container = tk.Frame(self.master, bg="#f5f6f5")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Tiêu đề
        self.title_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.title_frame.pack(fill="x", pady=(0, 20))
        self.title_label = tk.Label(self.title_frame,
                                    text="🚗 Hệ Thống Giám Sát Tài Xế AI",
                                    font=("Segoe UI", 18, "bold"),
                                    bg="#f5f6f5",
                                    fg="#2c3e50")
        self.title_label.pack()

        # Nội dung chính
        self.content_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.content_frame.pack(fill="both", expand=True)

        # Khung video
        self.left_frame = tk.Frame(self.content_frame, bg="#ffffff", bd=2, relief="flat")
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 20))
        self.cam_label = tk.Label(self.left_frame, bg="#ffffff")
        self.cam_label.pack(pady=10, padx=10)

        # Khung điều khiển
        self.right_frame = tk.Frame(self.content_frame, bg="#f5f6f5", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill="y", padx=20)
        self.right_frame.pack_propagate(False)

        # Thông tin tài xế
        self.info_frame = tk.Frame(self.right_frame, bg="#f5f6f5")
        self.info_frame.pack(fill="x", pady=(0, 20))
        self.user_label = tk.Label(self.info_frame,
                                text=f"👤 Tài xế: {self.user_name.capitalize()}",
                                font=("Segoe UI", 14, "bold"),
                                bg="#f5f6f5",
                                fg="#2c3e50")
        self.user_label.pack(anchor="w")
        self.time_label = tk.Label(self.info_frame,
                                text="",
                                font=("Segoe UI", 12),
                                fg="#28a745",
                                bg="#f5f6f5")
        self.time_label.pack(anchor="w", pady=5)
        self.recording_label = tk.Label(self.info_frame,
                                    text="Chưa ghi hình",
                                    font=("Segoe UI", 12, "bold"),
                                    fg="#28a745",
                                    bg="#f5f6f5")
        self.recording_label.pack(anchor="w", pady=5)

        # Các nút điều khiển
        self.buttons_frame = tk.Frame(self.right_frame, bg="#f5f6f5")
        self.buttons_frame.pack(fill="both", expand=True)

        button_style = {
            "font": ("Segoe UI", 12, "bold"),
            "width": 20,
            "pady": 10,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.start_button = tk.Button(self.buttons_frame,
                                    text="▶️ Bắt đầu ghi hình",
                                    bg="#28a745",
                                    fg="white",
                                    command=self.start_recording,
                                     **button_style)
        self.start_button.pack(pady=5, fill="x")
        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg="#218838"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg="#28a745"))
        self.last_check_time = 0  
        self.last_violation_time = 0  
        self.check_interval = 1  

        self.stop_button = tk.Button(self.buttons_frame,
                                    text="⏹ Dừng ghi và lưu",
                                    bg="#6c757d",
                                    fg="white",
                                    command=self.stop_recording,
                                    state=tk.DISABLED,
                                    **button_style)
        self.stop_button.pack(pady=5, fill="x")
        self.stop_button.bind("<Enter>", lambda e: self.stop_button.config(bg="#5a6268"))
        self.stop_button.bind("<Leave>", lambda e: self.stop_button.config(bg="#6c757d"))

        self.warning_button = tk.Button(self.buttons_frame,
                                    text="🛑 Lịch sử cảnh báo",
                                    bg="#dc3545",
                                    fg="white",
                                    command=self.show_warnings,
                                       **button_style)
        self.warning_button.pack(pady=5, fill="x")
        self.warning_button.bind("<Enter>", lambda e: self.warning_button.config(bg="#c82333"))
        self.warning_button.bind("<Leave>", lambda e: self.warning_button.config(bg="#dc3545"))

        self.history_button = tk.Button(self.buttons_frame,
                                    text="📂 Lịch sử",
                                    bg="#17a2b8",
                                    fg="white",
                                    command=self.show_video_history,
                                       **button_style)
        self.history_button.pack(pady=5, fill="x")
        self.history_button.bind("<Enter>", lambda e: self.history_button.config(bg="#138496"))
        self.history_button.bind("<Leave>", lambda e: self.history_button.config(bg="#17a2b8"))

        self.profile_button = tk.Button(self.buttons_frame,
                                    text="👤 Hồ sơ người dùng",
                                    bg="#6c757d",
                                    fg="white",
                                    command=self.show_profile,
                                       **button_style)
        self.profile_button.pack(pady=5, fill="x")
        self.profile_button.bind("<Enter>", lambda e: self.profile_button.config(bg="#5a6268"))
        self.profile_button.bind("<Leave>", lambda e: self.profile_button.config(bg="#6c757d"))

        self.logout_button = tk.Button(self.buttons_frame,
                                    text="🔶 Đăng xuất",
                                    bg="#fd7e14",
                                    fg="white",
                                    command=self.logout,
                                      **button_style)
        self.logout_button.pack(pady=(20, 5), fill="x")
        self.logout_button.bind("<Enter>", lambda e: self.logout_button.config(bg="#e06c00"))
        self.logout_button.bind("<Leave>", lambda e: self.logout_button.config(bg="#fd7e14"))

        # Khởi tạo webcam
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Không thể mở webcam")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo webcam: {e}")
            self.master.destroy()
            return

        self.update_frame()
        self.update_time()

    def tao_ten_file_hanh_trinh(self):
        now = datetime.datetime.now()
        folder = os.path.join("db", self.user_name, "journey")
        os.makedirs(folder, exist_ok=True)
        ten_co_ban = f"hanh_trinh_{now.day}_{now.month}_{now.year}"
        index = 1
        ten_file = f"{ten_co_ban}_{index}.avi"
        while os.path.exists(os.path.join(folder, ten_file)):
            index += 1
            ten_file = f"{ten_co_ban}_{index}.avi"
        return ten_file

    def check_violation_async(self, frame, timestamp):
        def task():
            result_distract = check_distract(frame, self.user_name)
            result_sleepy = check_sleepy(frame, self.user_name)

            if result_distract or result_sleepy:
                if timestamp - self.last_violation_time >= 3:
                    self.last_violation_time = timestamp
                    print("⚠️ Vi phạm được ghi nhận.")

                if not self.sound_playing:
                    self.play_alert_sound()
            else:
                if self.sound_playing:
                    pygame.mixer.music.stop()
                    self.sound_playing = False

        threading.Thread(target=task, daemon=True).start()
    
    def update_time(self):
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=now)
        if self.recording:
            elapsed = time.time() - self.start_time
            self.recording_label.config(text=f"Đang ghi: {datetime.timedelta(seconds=int(elapsed))}",
                                    fg="#dc3545")
        else:
            self.recording_label.config(text="Chưa ghi hình", fg="#28a745")
        self.master.after(1000, self.update_time)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            user_encoding_path = os.path.join("db", f"{self.user_name}.pickle")
            if os.path.exists(user_encoding_path):
                try:
                    with open(user_encoding_path, "rb") as f:
                        known_encoding = pickle.load(f)
                    face_locations = face_recognition.face_locations(rgb)
                    face_encodings = face_recognition.face_encodings(rgb, face_locations)
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)[0]
                        if match:
                            cv2.rectangle(frame, (left, top), (right, bottom), (52, 152, 219), 2)
                            cv2.putText(frame, self.user_name, (left, top - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (52, 152, 219), 2)

                            if self.recording and self.video_writer:
                                self.video_writer.write(frame)

                                now = time.time()
                                if now - self.last_check_time >= self.check_interval:
                                    self.last_check_time = now
                                    self.check_violation_async(frame.copy(), now)
                                    if now - self.last_violation_time >= 3:
                                        self.last_violation_time = now
                                        print("⚠️ Vi phạm được ghi nhận.")
                                        
                                    # Phát âm thanh nếu chưa phát
                                    if not self.sound_playing:
                                        self.play_alert_sound()
                                else:
                                    # Không vi phạm → tắt âm thanh nếu đang phát
                                    if self.sound_playing:
                                        pygame.mixer.music.stop()
                                        self.sound_playing = False

                except Exception as e:
                    print(f"Lỗi trong nhận diện khuôn mặt: {e}")

            rgb_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_display)
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)

        self.master.after_idle( self.update_frame)

    def start_recording(self):
        try:
            folder = os.path.join("db", self.user_name, "journey")
            os.makedirs(folder, exist_ok=True)
            filename = self.tao_ten_file_hanh_trinh()
            self.video_path = os.path.join(folder, filename)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
            self.recording = True
            self.start_time = time.time()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            # Phát âm thanh cảnh báo nếu có
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể bắt đầu ghi hình: {e}")

    def stop_recording(self):
        try:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            # Dừng âm thanh nếu đang phát
            if self.sound_playing:
                pygame.mixer.music.stop()
                self.sound_playing = False
            messagebox.showinfo("Xong", f"✅ Đã lưu hành trình vào: {self.video_path}")
            upload_to_drive(self.video_path, folder_name="Videos")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể dừng ghi hình: {e}")

    def play_alert_sound(self):
        profile_path = os.path.join("db", f"{self.user_name}_profile.pickle")
        default_sound = os.path.join("sounds", "cho_rep.mp3")  # ✅ Đường dẫn mới
        sound_file = default_sound

        if os.path.exists(profile_path):
            try:
                with open(profile_path, "rb") as f:
                    data = pickle.load(f)
                if data.get("alert_sound") and os.path.exists(data["alert_sound"]):
                    sound_file = data["alert_sound"]
            except Exception:
                pass

        if not os.path.exists(sound_file):
            print("⚠️ Không tìm thấy file âm thanh:", sound_file)
            return

        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play(-1)  # Lặp vô hạn
            self.sound_playing = True
        except Exception as e:
            print(f"Lỗi khi phát âm thanh: {e}")


    def show_warnings(self):
        folder = os.path.join("db", self.user_name, "warnings")
        if not os.path.exists(folder):
            messagebox.showinfo("Thông báo", "Chưa có cảnh báo nào.")
            return

        files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
        if not files:
            messagebox.showinfo("Thông báo", "Không tìm thấy ảnh cảnh báo.")
            return

        top = tk.Toplevel(self.master, bg="#f5f6f5")
        top.title("Lịch sử cảnh báo")
        top.geometry("800x600")

        canvas = tk.Canvas(top, bg="#f5f6f5")
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f5f6f5")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        for f in sorted(files, reverse=True):
            img_path = os.path.join(folder, f)
            img = Image.open(img_path)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)

            frame = tk.Frame(scroll_frame, bg="#ffffff", bd=2, relief="flat", padx=5, pady=5)
            frame.pack(padx=5, pady=5, fill="x")

            label = tk.Label(frame, image=photo, bg="#ffffff")
            label.image = photo
            label.pack(side="left")

            text = tk.Label(frame, text=f, font=("Segoe UI", 12), bg="#ffffff", fg="#2c3e50")
            text.pack(side="left", padx=10)

            def open_full_image(p=img_path):
                top_img = tk.Toplevel(bg="#f5f6f5")
                top_img.title("Xem ảnh cảnh báo")
                full_img = Image.open(p)
                full_img = full_img.resize((500, 400), Image.LANCZOS)
                photo_big = ImageTk.PhotoImage(full_img)
                img_label = tk.Label(top_img, image=photo_big, bg="#ffffff")
                img_label.image = photo_big
                img_label.pack(padx=20, pady=20)

            label.bind("<Button-1>", lambda e, p=img_path: open_full_image(p))
            text.bind("<Button-1>", lambda e, p=img_path: open_full_image(p))

    def show_video_history(self):
        video_dir = os.path.join("db", self.user_name, "journey")
        if not os.path.exists(video_dir):
            messagebox.showinfo("Thông báo", "Chưa có video hành trình nào")
            return

        files = [f for f in os.listdir(video_dir) if f.endswith(".avi")]
        if not files:
            messagebox.showinfo("Thông báo", "Không tìm thấy video phù hợp")
            return

        win = tk.Toplevel(self.master, bg="#f5f6f5")
        win.title("Lịch sử hành trình")
        win.geometry("800x600")

        header = tk.Label(win,
                        text="Lịch sử hành trình",
                        font=("Segoe UI", 16, "bold"),
                        bg="#f5f6f5",
                        fg="#2c3e50")
        header.pack(pady=20)

        listbox = tk.Listbox(win,
                            width=60,
                            font=("Segoe UI", 12),
                            bg="#ffffff",
                            fg="#2c3e50",
                            selectbackground="#17a2b8",
                            selectforeground="white")
        listbox.pack(padx=20, pady=20, fill="both", expand=True)

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
                    cv2.rectangle(frame, (left, top), (right, bottom), (52, 152, 219), 2)
                    cv2.putText(frame, self.user_name, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (52, 152, 219), 2)
                cv2.imshow(f"📼 {filename}", frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

        listbox.bind("<Double-Button-1>", play_video)

    def show_profile(self):
        profile_path = os.path.join("db", f"{self.user_name}_profile.pickle")
        default_sound = os.path.join("..", "ai_code", "AI", "UI", "cho_rep.mp3")
        data = {}

        if os.path.exists(profile_path):
            try:
                with open(profile_path, "rb") as f:
                    data = pickle.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Hồ sơ không đúng định dạng")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi đọc hồ sơ: {e}")
                return
        else:
            data = {
                "name": self.user_name,
                "phone": "",
                "email": "",
                "alert_sound": default_sound
            }

        top = tk.Toplevel(self.master, bg="#f5f6f5")
        top.title("Hồ sơ người dùng")
        top.geometry("600x500")

        header = tk.Label(top,
                         text="Hồ sơ người dùng",
                         font=("Segoe UI", 16, "bold"),
                         bg="#f5f6f5",
                         fg="#2c3e50")
        header.pack(pady=20)

        form_frame = tk.Frame(top, bg="#f5f6f5")
        form_frame.pack(padx=20, pady=20, fill="both")

        fields = {}
        row = 0
        for key, value in data.items():
            tk.Label(form_frame,
                    text=f"{key.capitalize()}:",
                    font=("Segoe UI", 12, "bold"),
                    bg="#f5f6f5",
                    fg="#2c3e50").grid(row=row, column=0, sticky="w", padx=10, pady=10)
            ent = tk.Entry(form_frame, width=40, font=("Segoe UI", 12))
            ent.insert(0, str(value) if value else "")
            ent.grid(row=row, column=1, padx=10, pady=10)
            fields[key] = ent
            row += 1

        def choose_alert():
            file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
            if file_path:
                fields["alert_sound"].delete(0, tk.END)
                fields["alert_sound"].insert(0, file_path)

        tk.Button(form_frame,
                text="🔊 Chọn chuông cảnh báo",
                bg="#6c757d",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                relief="flat",
                cursor="hand2",
                command=choose_alert).grid(row=row, column=1, pady=20, sticky="w")

        def save_changes():
            for key in fields:
                data[key] = fields[key].get()
            with open(profile_path, "wb") as f:
                pickle.dump(data, f)
            messagebox.showinfo("✅", "Đã lưu thay đổi thành công.")
            top.destroy()

        tk.Button(form_frame,
                text="💾 Lưu thay đổi",
                bg="#28a745",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                relief="flat",
                cursor="hand2",
                command=save_changes).grid(row=row+1, column=1, pady=20, sticky="e")

    def logout(self):
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        if self.sound_playing:
            pygame.mixer.music.stop()
            self.sound_playing = False
        self.master.destroy()
        from UI.login_screen import LoginScreen
        root = tk.Tk()
        app = LoginScreen(root)
        app.start()

    def __del__(self):
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        if self.sound_playing:
            pygame.mixer.music.stop()
            self.sound_playing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root, "trung")
    root.mainloop()