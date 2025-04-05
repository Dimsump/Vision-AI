import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

from tkinter import simpledialog

def prompt_text(title):
    return simpledialog.askstring("Đăng ký", title)

def get_button(master, text, bg, command, fg='white'):
    return tk.Button(master, text=text, bg=bg, fg=fg, width=20, height=2, command=command)

def get_img_label(master, width=640, height=480):
    return tk.Label(master, width=width, height=height, bg='cyan')



def msg_box(title, message):
    messagebox.showinfo(title, message)

def update_image(label, frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
    label.imgtk = imgtk
    label.configure(image=imgtk)
