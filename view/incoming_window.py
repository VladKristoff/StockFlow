from tkinter import *
from tkinter import ttk

class IncomingWindow:
    def __init__(self, main_frame, app):
        self.main_frame = main_frame
        self.app = app

        self.bg_color = "#3C4250"

        self.create_widgets()

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        top_bar = Frame(self.main_frame, background=self.bg_color)
        top_bar.pack(side="top", fill="x", padx=(67, 20), pady=(15, 0))

        title = ttk.Label(top_bar, text="StockFlow", style="Text.TLabel")
        title.pack(side="left", padx=(0, 50))

        add_btn = ttk.Button(top_bar, text="Добавить", style="Button.TButton")
        add_btn.pack(side="right", padx=10)

        delete_btn = ttk.Button(top_bar, text="Удалить", style="Button.TButton")
        delete_btn.pack(side="right", padx=10)

        self.create_table()

    def create_table(self):
        table_frame = Frame(self.main_frame, background=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=30, pady=30)

    def destroy(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()