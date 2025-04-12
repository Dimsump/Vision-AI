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

    def tao_ten_file_hanh_trinh(self):
        now = datetime.datetime.now()
        folder = os.path.join("db", self.user_name, "journey")
        os.makedirs(folder, exist_ok=True)

        # Tạo tên cơ bản theo ngày tháng năm
        ten_co_ban = f"hanh_trinh_{now.day}_{now.month}_{now.year}"

        # Kiểm tra xem file đã tồn tại hay chưa để tự động tăng số thứ tự
        index = 1
        ten_file = f"{ten_co_ban}_{index}.avi"
        while os.path.exists(os.path.join(folder, ten_file)):
            index += 1
            ten_file = f"{ten_co_ban}_{index}.avi"

        return ten_file

    
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

            # Load user's face encoding from pickle file
            user_encoding_path = os.path.join("db", f"{self.user_name}.pickle")
            if not os.path.exists(user_encoding_path):
                print(f"Error: No face encoding found for {self.user_name}")
                return

            with open(user_encoding_path, "rb") as f:
                known_encoding = pickle.load(f)

            # Detect faces
            face_locations = face_recognition.face_locations(rgb)
            face_encodings = face_recognition.face_encodings(rgb, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Compare with known user encoding
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)[0]
                if match:
                    # Only process the matched face
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)
                    cv2.putText(frame, self.user_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (255, 0, 255), 2)

                    if self.recording:
                        # Only check distract or sleepy for the matched face
                        self.video_writer.write(frame)
                        check_distract(frame, self.user_name)
                        check_sleepy(frame, self.user_name)

            # Display the frame
            rgb_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_display)
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)

        self.master.after(10, self.update_frame)
        
    def start_recording(self):
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

        canvas = tk.Canvas(top)
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for f in sorted(files, reverse=True):
            img_path = os.path.join(folder, f)
            img = Image.open(img_path)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)

            frame = tk.Frame(scroll_frame, bd=2, relief="groove", padx=5, pady=5)
            frame.pack(padx=5, pady=5, fill="x")

            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack(side="left")

            text = tk.Label(frame, text=f, anchor="w")
            text.pack(side="left", padx=10)

            def open_full_image(p=img_path):
                top_img = tk.Toplevel()
                top_img.title("Xem ảnh cảnh báo")
                full_img = Image.open(p)
                full_img = full_img.resize((500, 400))
                photo_big = ImageTk.PhotoImage(full_img)
                img_label = tk.Label(top_img, image=photo_big)
                img_label.image = photo_big
                img_label.pack()

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
        profile_path = os.path.join("db", f"{self.user_name}_profile.pickle")
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
                "alert_sound": ""
            }

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
                fields["alert_sound"].delete(0, tk.END)
                fields["alert_sound"].insert(0, file_path)

        tk.Button(top, text="🔊 Chọn chuông cảnh báo", command=choose_alert).grid(row=row, column=1, pady=5, sticky="w")

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