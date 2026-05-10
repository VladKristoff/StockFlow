from tkinter import *
from tkinter import ttk

class TableWindow:
    def __init__(self, main_frame, app):
        self.main_frame = main_frame
        self.app = app

        self.create_widgets()

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ttk.Label(self.main_frame, text="StockFlow", style="Text.TLabel")
        title.pack(anchor="w", padx=67)

        self.create_crud_frame() # Создание рамки с CRUD - операциями

    def create_crud_frame(self):
        CRUD_frame = Frame(self.main_frame,
                           background="#1D1D21")
        CRUD_frame.pack(anchor="w", padx=15, pady=15, fill="y", expand=True)

        # Группа поиска
        search_frame = Frame(CRUD_frame,
                             background="#1D1D21")
        search_frame.pack(anchor="center")

        name_entry = ttk.Entry(search_frame, width=27, font=("Arial", 12), style="Entry.TEntry")
        name_entry.pack(anchor="center", padx=32, pady=20)

        search_btn = ttk.Button(search_frame, text="Найти", style="Button.TButton")
        search_btn.pack(anchor="center", padx=10)

        # Группа CRUD - операций
        mini_crud_frame = Frame(CRUD_frame,
                                background="#1D1D21")
        mini_crud_frame.pack(anchor="center", pady=70)

        add_btn = ttk.Button(mini_crud_frame, text="Добавить", style="Button.TButton")
        add_btn.pack(anchor="center", padx=10, pady=10)

        edit_btn = ttk.Button(mini_crud_frame, text="Редактировать", style="Button.TButton")
        edit_btn.pack(anchor="center", padx=10, pady=10)

        delete_btn = ttk.Button(mini_crud_frame, text="Удалить", style="Button.TButton")
        delete_btn.pack(anchor="center", padx=10, pady=10)

        # Информация о подключении БД
        bd_info_frame = Frame(CRUD_frame, background="#1D1D21")
        bd_info_frame.pack(side="bottom", fill="x", pady=15)

        bd_info_label = ttk.Label(bd_info_frame,
                                  text="База данных подключена",
                                  style="BD_info.TLabel")
        bd_info_label.pack(anchor="center")

    def destroy(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()