from tkinter import *
from tkinter import ttk, messagebox
from database.db_manager import connect_bd, get_any_table, add_record, delete_record, update_record


class TableWindow:
    def __init__(self, main_frame, app):
        self.tree = None
        self.main_frame = main_frame
        self.app = app
        self.db_conn = connect_bd()
        self.current_table = "products"
        self.tab_labels = {}

        self.table_configs = {
            "products": {
                "display_name": "Товары",
                "columns": ("id", "name", "price", "count", "type_id"),
                "headings": ("ID", "Название", "Цена", "Кол-во", "Тип ID"),
                "widths": {"id": 50, "count": 80, "name": 250, "price": 100, "type_id": 80}
            },
            "contractors": {
                "display_name": "Контрагенты",
                "columns": ("id", "name", "phone", "inn", "address"),
                "headings": ("ID", "Название", "Телефон", "ИНН", "Адрес"),
                "widths": {"id": 50, "name": 200, "phone": 120, "inn": 120}
            },
            "employees": {
                "display_name": "Сотрудники",
                "columns": ("id", "name", "position_id"),
                "headings": ("ID", "ФИО", "ID Должности"),
                "widths": {"id": 50, "name": 300, "position_id": 100}
            },
            "positions": {
                "display_name": "Должности",
                "columns": ("id", "name"),
                "headings": ("ID", "Наименование должности"),
                "widths": {"id": 50, "name": 300}
            },
            "product_types": {
                "display_name": "Типы товаров",
                "columns": ("id", "name"),
                "headings": ("ID", "Категория"),
                "widths": {"id": 50, "name": 300}
            }
        }

        self.create_widgets()
        self.create_table_frame()
        self.switch_table(self.current_table)

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        bg_color = "#3C4250"

        top_bar = Frame(self.main_frame, background=bg_color)
        top_bar.pack(side="top", fill="x", padx=67, pady=(15, 0))

        title = ttk.Label(top_bar, text="StockFlow", style="Text.TLabel")
        title.pack(side="left", padx=(0, 50))

        # Контейнер для вкладок
        self.tabs_container = Frame(top_bar, background=bg_color)
        self.tabs_container.pack(side="left", fill="x", expand=True)

        self.tab_labels = {}
        font_style = ("Arial", 14)

        for table_key, config in self.table_configs.items():
            lbl = Label(self.tabs_container,
                        text=config["display_name"],
                        fg="#888888",
                        bg=bg_color,
                        font=font_style,
                        cursor="hand2",
                        padx=20)

            lbl.pack(side="left", expand=True)

            lbl.bind("<Button-1>", lambda e, k=table_key: self.switch_table(k))
            self.tab_labels[table_key] = lbl

        self.create_crud_frame()

    def create_crud_frame(self):
        CRUD_frame = Frame(self.main_frame, background="#1D1D21")
        CRUD_frame.pack(anchor="w", padx=15, pady=30, fill="y", side="left")

        # Поиск
        search_frame = Frame(CRUD_frame, background="#1D1D21")
        search_frame.pack(anchor="center")
        self.search_entry = ttk.Entry(search_frame, width=27, font=("Arial", 12), style="Entry.TEntry")
        self.search_entry.pack(anchor="center", padx=32, pady=20)
        ttk.Button(search_frame, text="Найти", style="Button.TButton").pack(anchor="center")

        # CRUD кнопки
        mini_crud_frame = Frame(CRUD_frame, background="#1D1D21")
        mini_crud_frame.pack(anchor="center", pady=70)

        ttk.Button(mini_crud_frame, text="Добавить", style="Button.TButton", command=self.on_add_click).pack(pady=10)
        ttk.Button(mini_crud_frame, text="Редактировать", style="Button.TButton", command=self.on_edit_click).pack(
            pady=10)
        ttk.Button(mini_crud_frame, text="Удалить", style="Button.TButton", command=self.on_delete_click).pack(pady=10)

        # Статус БД
        bd_info_frame = Frame(CRUD_frame, background="#1D1D21")
        bd_info_frame.pack(side="bottom", fill="x", pady=15)
        status_text = "База данных подключена" if self.db_conn else "База данных не подключена"
        status_color = "#B9FFDC" if self.db_conn else "#FF6D70"
        ttk.Label(bd_info_frame, text=status_text, foreground=status_color, style="BD_info.TLabel").pack()

    def create_table_frame(self):
        # Правая часть под таблицу
        self.right_content = Frame(self.main_frame, background="#1D1D21")
        self.right_content.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        self.tree = ttk.Treeview(self.right_content, show="headings", style="Treeview")
        scrollbar = ttk.Scrollbar(self.right_content, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def switch_table(self, table_name):
        self.current_table = table_name

        bg_color = "#3C4250"
        for key, lbl in self.tab_labels.items():
            if key == table_name:
                lbl.configure(fg="#FFFFFF", font=("Arial", 12, "bold"), bg=bg_color)
            else:
                lbl.configure(fg="#888888", font=("Arial", 12), bg=bg_color)

        # Конфигурация колонок (оставляем как было)
        config = self.table_configs[table_name]
        self.tree["columns"] = config["columns"]
        for i, col in enumerate(config["columns"]):
            self.tree.heading(col, text=config["headings"][i])
            w = config["widths"].get(col, 150)
            self.tree.column(col, width=w, anchor="center" if col != "name" else "w")

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        data = get_any_table(self.current_table)
        for row in data:
            self.tree.insert("", END, values=row)

    def on_add_click(self):
        config = self.table_configs[self.current_table]

        fields_to_input = [col for col in config["columns"] if col != "id"]
        labels_to_show = [config["headings"][config["columns"].index(col)] for col in fields_to_input]

        add_window = Toplevel(self.main_frame, background="#1D1D21")
        add_window.title(f"Добавить: {config['display_name']}")
        add_window.geometry("400x300")
        add_window.resizable(width=False, height=False)
        add_window.grab_set()

        entries = {}
        for i, (field, label_text) in enumerate(zip(fields_to_input, labels_to_show)):
            ttk.Label(add_window, text=label_text, font=("Arial", 10),
                      foreground="white",
                      style="SmallText.TLabel").pack(pady=(10, 0))
            entry = ttk.Entry(add_window, width=30)
            entry.pack()
            entries[field] = entry

        def save_new_record():
            # Собираем данные из полей ввода
            values = tuple(entries[field].get() for field in fields_to_input)

            if any(v == "" for v in values):
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return

            # Отправляем в БД, используя имя текущей таблицы
            add_record(self.current_table, fields_to_input, values)

            add_window.destroy()
            self.load_data()  # Перезагружаем таблицу, чтобы увидеть изменения

        ttk.Button(add_window, text="Сохранить", command=save_new_record, style="Button.TButton").pack(pady=20)


    def on_edit_click(self):
        # 1. Проверяем, выбрана ли строка в таблице
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите строку для редактирования!")
            return

        # 2. Извлекаем текущие значения строки и конфигурацию таблицы
        row_values = self.tree.item(selected_item)['values']
        config = self.table_configs[self.current_table]

        # ID всегда идет первым в списке колонок
        record_id = row_values[0]

        # Исключаем ID из полей для редактирования
        fields_to_edit = [col for col in config["columns"] if col != "id"]

        # 3. Создаем модальное окно редактирования
        edit_window = Toplevel(self.main_frame, background="#1D1D21")
        edit_window.title(f"Редактировать запись ID {record_id} — {config['display_name']}")
        edit_window.geometry("400x350")
        edit_window.resizable(width=False, height=False)
        edit_window.grab_set()

        entries = {}

        # Строим поля ввода и заполняем их старыми данными
        for col in fields_to_edit:
            # Находим индекс колонки в общем списке, чтобы правильно сопоставить с row_values
            idx = config["columns"].index(col)
            label_text = config["headings"][idx]
            old_value = row_values[idx]

            ttk.Label(edit_window, text=label_text, font=("Arial", 10),
                      foreground="white",
                      style="SmallText.TLabel").pack(pady=(10, 0))
            entry = ttk.Entry(edit_window, width=30)
            entry.pack()

            # Предзаполняем поле старым значением
            entry.insert(0, old_value)
            entries[col] = entry

        # 4. Логика сохранения изменений
        def save_changes():
            new_values = [entries[col].get() for col in fields_to_edit]

            if any(v == "" for v in new_values):
                messagebox.showwarning("Ошибка", "Поля не должны быть пустыми!")
                return

            # Вызываем универсальный UPDATE запрос
            update_record(self.current_table, fields_to_edit, new_values, record_id)

            edit_window.destroy()
            self.load_data()  # Обновляем Treeview

        ttk.Button(edit_window, text="Сохранить изменения", command=save_changes, style="Button.TButton").pack(pady=20)

    def on_delete_click(self):
        # Получаем выделенную строку в Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите строку для удаления!")
            return

        # Берем значения строки (ID всегда первый в твоих конфигах)
        row_values = self.tree.item(selected_item)['values']
        record_id = row_values[0]

        confirm = messagebox.askyesno("Подтверждение",
                                      f"Удалить запись с ID {record_id} из таблицы {self.table_configs[self.current_table]['display_name']}?")
        if confirm:
            delete_record(self.current_table, record_id)
            self.load_data()  # Обновляем интерфейс

    def destroy(self):
        if self.db_conn: self.db_conn.close()
        for widget in self.main_frame.winfo_children(): widget.destroy()