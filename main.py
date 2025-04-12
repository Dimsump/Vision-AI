import tkinter as tk
from ui.login_screen import LoginScreen

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginScreen(master=root)
    app.start()
