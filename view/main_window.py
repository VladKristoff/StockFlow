from tkinter import *
from tkinter import ttk

class MainWindow:
    def __init__(self, main_frame, app):
        self.main_frame = main_frame
        self.app = app

        self.create_widgets()

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = Label(self.main_frame, text="Stock Flow")
        title.pack(anchor="center")