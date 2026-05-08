from tkinter import *
from tkinter import ttk

class AppStockFlow:
    def __init__(self, root):
        self.root = root
        root.title('АО НПП "РЕСПИРАТОР" - Stock Flow')
        root.geometry("1600x900")
        root.resizable(False, False)

        icon = PhotoImage(file='images/logo.png')
        root.iconphoto(True, icon)

        self.header = Frame(root, background='#1D1D21', height=75)
        self.header.pack(fill="x")

        self.main_frame = Frame(root, background='white')
        self.main_frame.pack(fill="both", expand=True)

        self.current_window = None

    def show_window(self, page_class, *args, **kwargs):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = page_class(self.main_frame, self, *args, **kwargs)

