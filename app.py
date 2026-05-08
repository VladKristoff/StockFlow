from tkinter import *
from tkinter import ttk

from PIL import Image, ImageTk

class AppStockFlow:
    def __init__(self, root):
        self.root = root
        root.title('АО НПП "РЕСПИРАТОР" - Stock Flow')
        root.geometry("1600x900")
        root.resizable(False, False)

        self.icon = PhotoImage(file='images/logo.png')
        self.header_logo = None
        root.iconphoto(True, self.icon)

        self.create_header()

        self.main_frame = Frame(root, background='white')
        self.main_frame.pack(fill="both", expand=True)

        self.current_window = None

    def create_header(self):
        # Создание фрейма для шапки
        header = Frame(self.root, background='#1D1D21', height=100)
        header.pack(fill="x")

        try:
            pil_img = Image.open('images/logo_with_background.png')
            pil_img = pil_img.resize((100, 92), Image.LANCZOS)

            self.header_logo = ImageTk.PhotoImage(pil_img)

            canvas = Canvas(header, width=100, height=100, background='#1D1D21', highlightthickness=0)
            canvas.pack(side="left", padx=100, pady=7)

            canvas.create_image(0, 0, anchor="nw", image=self.header_logo)

        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")

    def show_window(self, page_class, *args, **kwargs):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = page_class(self.main_frame, self, *args, **kwargs)

