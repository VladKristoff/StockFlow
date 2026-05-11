from tkinter import *
from tkinter import ttk
from database.db_manager import connect_bd, get_products

class TableWindow:
    def __init__(self, main_frame, app):
        self.tree = None
        self.main_frame = main_frame
        self.app = app

        self.db_conn = connect_bd()

        self.create_widgets()
        self.create_table_frame()

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ttk.Label(self.main_frame, text="StockFlow", style="Text.TLabel")
        title.pack(anchor="w", padx=67)

        self.create_crud_frame() # Создание рамки с CRUD - операциями

    def create_crud_frame(self):
        CRUD_frame = Frame(self.main_frame,
                           background="#1D1D21")
        CRUD_frame.pack(anchor="w", padx=15, pady=15, fill="y", side="left")

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

        if self.db_conn:
            status_text = "База данных подключена"
            status_color = "#B9FFDC"
        else:
            status_text = "База данных не подключена"
            status_color = "#FF6D70"

        bd_info_label = ttk.Label(bd_info_frame,
                                  text=status_text,
                                  foreground=status_color,
                                  style="BD_info.TLabel")
        bd_info_label.pack(anchor="center")

    def create_table_frame(self):
        table_frame = Frame(self.main_frame, background="red")
        table_frame.pack(anchor="center", fill="both", expand=True, pady=15, padx=15)

        columns = ("id", "name", "price", "count", "type_id")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")

        # Настраиваем заголовки
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("price", text="Цена")
        self.tree.heading("count", text="Количество")
        self.tree.heading("type_id", text="type_id")

        # Настраиваем ширину колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("count", width=50, anchor="center")
        self.tree.column("name", width=250)
        self.tree.column("price", anchor="center")
        self.tree.column("type_id", anchor="center")

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = get_products()

        for row in data:
            self.tree.insert("", END, values=row)

    def destroy(self):
        if self.db_conn:
            self.db_conn.close()
        for widget in self.main_frame.winfo_children():
            widget.destroy()