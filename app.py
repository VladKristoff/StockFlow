from logging import DEBUG
from tkinter import *
from tkinter import ttk

from PIL import Image, ImageTk
from styles import set_styles

class AppStockFlow:
    def __init__(self, root):
        self.root = root
        root.title('АО НПП "РЕСПИРАТОР" - Stock Flow')
        root.geometry("1600x900")
        root.resizable(False, False)

        self.icon = PhotoImage(file='images/logo.png')
        self.header_logo = None
        root.iconphoto(True, self.icon)

        self.page_buttons = {}

        set_styles(self.root)
        self.create_header()

        self.main_frame = Frame(root, background='#3C4250')
        self.main_frame.pack(fill="both", expand=True)

        self.current_window = None

    def create_header(self):
        # Создание фрейма для шапки
        header = Frame(self.root, background='#1D1D21', height=112)
        header.pack(fill="x")

        # Добавление логотипа
        try:
            pil_img = Image.open('images/logo_with_background.png')
            pil_img = pil_img.resize((105, 97), Image.LANCZOS)

            self.header_logo = ImageTk.PhotoImage(pil_img)

            canvas = Canvas(header, width=100, height=100, background='#1D1D21', highlightthickness=0)
            canvas.pack(side="left", padx=120, pady=7)

            canvas.create_image(0, 0, anchor="nw", image=self.header_logo)

        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")

        # Добавление кнопок
        incoming_button = ttk.Button(header, text="Приходная накладная", style='BigButton.TButton',
                                     command=lambda: self.on_page_button_click("incoming"))
        incoming_button.pack(side="right", padx=30, pady=10, ipady=10)

        expenses_button = ttk.Button(header, text="Расходная накладная", style='BigButton.TButton',
                                     command=lambda: self.on_page_button_click("expenses"))
        expenses_button.pack(side="right", padx=30, pady=10, ipady=10)

        tables_button = ttk.Button(header, text="Справочники", style='BigButton.TButton',
                                   command=lambda: self.on_page_button_click("tables"))
        tables_button.pack(side="right", padx=30, pady=10, ipady=10)

        self.page_buttons = {
            "incoming": incoming_button,
            "expenses": expenses_button,
            "tables": tables_button
        }

    def on_page_button_click(self, page_name):
        from view.incoming_window import IncomingWindow
        from view.expenses_window import ExpensesWindow
        from view.table_window import TableWindow

        page_classes = {
            "incoming": IncomingWindow,
            "expenses": ExpensesWindow,
            "tables": TableWindow
        }

        if page_name in page_classes:
            self.show_window(page_classes[page_name])

    def update_header_button_style(self, current_page_class):
        page_to_button = {
            "TableWindow": "tables",
            "IncomingWindow": "incoming",
            "ExpensesWindow": "expenses",
        }

        current_class_name = current_page_class.__class__.__name__
        active_button_name = page_to_button.get(current_class_name)

        for button_name, button in self.page_buttons.items():
            if button_name == active_button_name:
                button['style'] = 'Select.BigButton.TButton'
            else:
                button.configure(style='BigButton.TButton')

    def show_window(self, page_class, *args, **kwargs):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = page_class(self.main_frame, self, *args, **kwargs)

        self.update_header_button_style(self.current_window)