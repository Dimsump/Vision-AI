import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os, pickle, json

USER_DATA_FILE = "user.json"
TEMP_PATH = "temp"

class AdminApp:
    def __init__(self, master=None, admin_name="Admin"):
        self.admin_name = admin_name
        self.window = master or tk.Tk()
        self.window.title("Quản Lý Tài Xế")
        self.window.geometry("980x600")
        self.window.resizable(False, False)
        self.window.configure(bg="#f5f6f5")

        self.main_container = tk.Frame(self.window, bg="#f5f6f5")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.title_frame.pack(fill="x", pady=(0, 20))
        self.title_label = tk.Label(self.title_frame,
                                    text="👤 Quản Lý Tài Xế",
                                    font=("Segoe UI", 18, "bold"),
                                    bg="#f5f6f5", fg="#2c3e50")
        self.title_label.pack()

        self.content_frame = tk.Frame(self.main_container, bg="#f5f6f5")
        self.content_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.content_frame, bg="#ffffff", bd=2, relief="flat", width=250, height=420)
        self.left_frame.pack(side=tk.LEFT, fill="y", padx=(0, 20))
        self.left_frame.pack_propagate(False)

        self.admin_label = tk.Label(self.left_frame,
                                    text=f"👤 Quản trị viên: {admin_name}",
                                    font=("Segoe UI", 14, "bold"),
                                    bg="#ffffff", fg="#2c3e50")
        self.admin_label.pack(anchor="w", padx=10, pady=(10, 10))

        self.driver_listbox = tk.Listbox(self.left_frame,
                                         font=("Segoe UI", 12),
                                         bg="#ffffff", fg="#2c3e50",
                                         selectbackground="#17a2b8", selectforeground="white")
        self.driver_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.driver_listbox.bind("<<ListboxSelect>>", self.show_driver_info)

        self.logout_button = tk.Button(self.left_frame, text="🔙 Đăng xuất",
                                       bg="#dc3545", fg="white",
                                       font=("Segoe UI", 12, "bold"),
                                       width=15, pady=10, bd=0,
                                       relief="flat", cursor="hand2",
                                       command=self.logout)
        self.logout_button.pack(side="bottom", pady=10, padx=10)
        self.logout_button.bind("<Enter>", lambda e: self.logout_button.config(bg="#c82333"))
        self.logout_button.bind("<Leave>", lambda e: self.logout_button.config(bg="#dc3545"))

        self.right_frame = tk.Frame(self.content_frame, bg="#ffffff", bd=2, relief="flat")
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=20)

        self.info_label = tk.Label(self.right_frame, text="Thông tin tài xế",
                                   font=("Segoe UI", 16, "bold"),
                                   bg="#ffffff", fg="#2c3e50")
        self.info_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.image_label = tk.Label(self.right_frame, bg="#ffffff", font=("Segoe UI", 12))
        self.image_label.pack(pady=10)

        self.info_text = tk.Text(self.right_frame, height=8, width=50,
                                 font=("Segoe UI", 12),
                                 bg="#f5f6f5", fg="#2c3e50",
                                 bd=0, relief="flat", padx=10, pady=10)
        self.info_text.pack(padx=20, pady=(10, 0), fill="both", expand=True)


        # Radio phân quyền
        self.role_var = tk.StringVar(value="driver")
        self.role_frame = tk.Frame(self.right_frame, bg="#ffffff")
        self.role_frame.pack(padx=20, pady=(5, 10), anchor="w")
        self.role_var = tk.StringVar()
        tk.Label(self.role_frame, text="Phân quyền:", font=("Segoe UI", 12), bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(self.role_frame, text="Admin", variable=self.role_var, value="admin", bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(self.role_frame, text="Driver", variable=self.role_var, value="driver", bg="#ffffff").pack(side=tk.LEFT)

        self.button_frame = tk.Frame(self.right_frame, bg="#ffffff")
        self.button_frame.pack(pady=(0, 20), padx=20, side="bottom", fill="x")

        self.save_button = tk.Button(self.button_frame, text="💾 Lưu thay đổi", bg="#28a745",
                                     fg="white", font=("Segoe UI", 12, "bold"),
                                     pady=8, bd=0, relief="flat", cursor="hand2",
                                     command=self.save_driver_info)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.save_button.bind("<Enter>", lambda e: self.save_button.config(bg="#218838"))
        self.save_button.bind("<Leave>", lambda e: self.save_button.config(bg="#28a745"))

        self.history_button = tk.Button(self.button_frame, text="📂 Lịch sử hành trình", bg="#17a2b8",
                                        fg="white", font=("Segoe UI", 12, "bold"),
                                        pady=8, bd=0, relief="flat", cursor="hand2",
                                        command=self.view_history)
        self.history_button.pack(side=tk.LEFT, padx=5)

        self.warning_button = tk.Button(self.button_frame, text="⚠️ Cảnh báo", bg="#dc3545",
                                        fg="white", font=("Segoe UI", 12, "bold"),
                                        pady=8, bd=0, relief="flat", cursor="hand2",
                                        command=self.view_warnings)
        self.warning_button.pack(side=tk.LEFT, padx=5)

        self.load_driver_list()

    def load_driver_list(self):
        self.driver_listbox.delete(0, tk.END)
        if os.path.exists("db"):
            for file in os.listdir("db"):
                if file.endswith(".pickle") and not file.endswith("_profile.pickle"):
                    self.driver_listbox.insert(tk.END, file.replace(".pickle", ""))

    def show_driver_info(self, event=None):
        selection = self.driver_listbox.curselection()
        if not selection:
            return
        selected_driver = self.driver_listbox.get(selection[0])
        self.current_driver = selected_driver

        self.info_text.delete("1.0", tk.END)
        self.role_var.set("driver")

        profile_path = os.path.join("db", f"{selected_driver}_profile.pickle")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "rb") as f:
                    data = pickle.load(f)
                if isinstance(data, dict):
                    display = "\n".join([f"{k}: {v}" for k, v in data.items()])
                    self.info_text.insert(tk.END, display)
            except Exception as e:
                self.info_text.insert(tk.END, f"(Lỗi khi đọc hồ sơ: {str(e)})")
        else:
            self.info_text.insert(tk.END, "(Chưa có hồ sơ tài xế)")

        # Load avatar từ temp
        face_path = os.path.join("temp", f"{selected_driver}_face.jpg")
        if os.path.exists(face_path):
            image = Image.open(face_path)
            image.thumbnail((150, 150))
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.tk_image, text="")
        else:
            self.image_label.config(image="", text="(Không có ảnh)", font=("Segoe UI", 12))

        # Gán quyền từ user.json nếu có
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
            role = users.get(selected_driver, {}).get("role", "driver")
            self.role_var.set(role)

    def save_driver_info(self):
        if not hasattr(self, "current_driver"):
            messagebox.showerror("Lỗi", "Vui lòng chọn người dùng.")
            return
        try:
            # Lưu nội dung text
            lines = self.info_text.get("1.0", tk.END).strip().split("\n")
            updated_data = {}
            for line in lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    updated_data[k.strip()] = v.strip()
            with open(os.path.join("db", f"{self.current_driver}_profile.pickle"), "wb") as f:
                pickle.dump(updated_data, f)

            # Cập nhật quyền vào user.json
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    users = json.load(f)
            else:
                users = {}

            if self.current_driver not in users:
                users[self.current_driver] = {}
            users[self.current_driver]["role"] = self.role_var.get()
            with open(USER_DATA_FILE, "w") as f:
                json.dump(users, f, indent=2)

            messagebox.showinfo("✅", "Đã lưu thông tin người dùng.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thông tin: {e}")

    def view_history(self):
        if not hasattr(self, "current_driver"):
            messagebox.showerror("Lỗi", "Chưa chọn tài xế.")
            return

        history_window = tk.Toplevel(self.window)
        history_window.title("Lịch sử hành trình")
        history_window.geometry("600x400")
        history_window.configure(bg="#f5f6f5")

        title_label = tk.Label(history_window,
                            text="Lịch sử hành trình",
                            font=("Segoe UI", 16, "bold"),
                            bg="#f5f6f5")
        title_label.pack(pady=10)

        listbox = tk.Listbox(history_window, font=("Segoe UI", 12), height=15)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)

        history_path = os.path.join("db", self.current_driver, "journey")
        if os.path.exists(history_path):
            files = [f for f in os.listdir(history_path) if f.lower().endswith((".mp4", ".avi", ".mov"))]
            if not files:
                messagebox.showinfo("Lịch sử", f"Không tìm thấy video hành trình nào cho {self.current_driver}.")
            for file in files:
                listbox.insert(tk.END, file)

            def play_selected(event=None):
                selection = listbox.curselection()
                if not selection:
                    return
                filename = listbox.get(selection[0])
                filepath = os.path.join(history_path, filename)
                if os.path.exists(filepath):
                    os.startfile(filepath)

            listbox.bind("<Double-1>", play_selected)
        else:
            messagebox.showinfo("Lịch sử", f"Thư mục lịch sử không tồn tại cho {self.current_driver}.")

    def view_warnings(self):
        if not hasattr(self, "current_driver"):
            messagebox.showerror("Lỗi", "Chưa chọn tài xế.")
            return

        warning_dir = os.path.join("db", self.current_driver, "warnings")
        if not os.path.exists(warning_dir):
            messagebox.showinfo("⚠️ Cảnh báo", f"Không có thư mục cảnh báo cho {self.current_driver}.")
            return

        image_files = [f for f in os.listdir(warning_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not image_files:
            messagebox.showinfo("⚠️ Cảnh báo", f"Không có ảnh cảnh báo nào của {self.current_driver}.")
            return

        # Cửa sổ hiển thị ảnh cảnh báo
        warning_window = tk.Toplevel(self.window)
        warning_window.title("Lịch sử cảnh báo")
        warning_window.geometry("800x600")

        canvas = tk.Canvas(warning_window, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(warning_window, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=frame, anchor="nw")

        for img_file in image_files:
            img_path = os.path.join(warning_dir, img_file)
            try:
                image = Image.open(img_path)
                image.thumbnail((200, 150))
                photo = ImageTk.PhotoImage(image)
                panel = tk.Label(frame, image=photo)
                panel.image = photo  # Giữ tham chiếu
                panel.pack(padx=5, pady=5)

                label = tk.Label(frame, text=img_file, bg="white", font=("Segoe UI", 10))
                label.pack()
            except Exception as e:
                continue

        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))



    def logout(self):
        import UI.login_screen as login_screen
        self.window.destroy()
        login_screen.LoginScreen().start()

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    AdminApp().start()