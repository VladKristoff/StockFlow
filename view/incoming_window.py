from tkinter import *
from tkinter import ttk
from database.db_doc_manager import get_all_documents

class IncomingWindow:
    def __init__(self, main_frame, app):
        self.tree = None
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

        columns = ("doc_number", "doc_date", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")

        self.tree.heading("doc_number", text="№ Документа")
        self.tree.heading("doc_date", text="Дата документа")
        self.tree.heading("created_at", text="Дата создания")

        self.tree.column("doc_number", width=150, anchor="center")
        self.tree.column("doc_date", width=150, anchor="center")
        self.tree.column("created_at", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = get_all_documents(1)

        for row in data:
            self.tree.insert("", "end", values=row)

    def destroy(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()