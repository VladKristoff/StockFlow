from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from database.db_doc_manager import get_contractors, get_employees


class AddDocumentWindow(Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.title("Создание приходной накладной")
        self.geometry("1000x700")
        self.db_manager = db_manager

        # Данные для табличной части (список словарей)
        self.items = []

        self.create_widgets()

    def create_widgets(self):
        header_frame = LabelFrame(self, text="Реквизиты документа", padx=10, pady=10)
        header_frame.pack(fill="x", padx=10, pady=5)

        Label(header_frame, text="Дата:").grid(row=0, column=0, sticky="w")
        self.date_entry = Entry(header_frame)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=0, column=1, padx=5)

        Label(header_frame, text="Контрагент:").grid(row=0, column=2, padx=10)
        self.contractor_cb = ttk.Combobox(header_frame, values=self.get_contractors())
        self.contractor_cb.grid(row=0, column=3)

        Label(header_frame, text="Ответственный:").grid(row=0, column=4, padx=10)
        self.employee_cb = ttk.Combobox(header_frame, values=self.get_employees())
        self.employee_cb.grid(row=0, column=5)

        items_frame = LabelFrame(self, text="Товары", padx=10, pady=10)
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_panel = Frame(items_frame)
        btn_panel.pack(fill="x", pady=5)
        Button(btn_panel, text="+ Добавить товар", command=self.add_item_row, bg="#4CAF50", fg="white").pack(
            side="left")
        Button(btn_panel, text="- Удалить строку", command=self.remove_item_row, bg="#f44336", fg="white").pack(
            side="left", padx=5)

        self.tree = ttk.Treeview(items_frame, columns=("name", "count", "price", "sum"), show="headings")
        self.tree.heading("name", text="Товар")
        self.tree.heading("count", text="Кол-во")
        self.tree.heading("price", text="Цена")
        self.tree.heading("sum", text="Сумма")
        self.tree.pack(fill="both", expand=True)

        self.total_label = Label(self, text="ИТОГО: 0.00 руб.", font=("Arial", 14, "bold"))
        self.total_label.pack(anchor="e", padx=20)

        Button(self, text="ПРОВЕСТИ ДОКУМЕНТ", command=self.save_document, height=2, bg="#2196F3", fg="white").pack(
            fill="x", padx=10, pady=10)