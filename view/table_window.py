from tkinter import *
from tkinter import ttk, messagebox
from database.db_manager import connect_bd, get_any_table, add_record, delete_record, update_record, search_records, \
    get_foreign_key_options


class TableWindow:
    def __init__(self, main_frame, app):
        self.tree = None
        self.main_frame = main_frame
        self.app = app
        self.db_conn = connect_bd()
        self.current_table = "products"
        self.tab_labels = {}
        self.current_search_term = ""  # Для хранения текущего поискового запроса

        self.table_configs = {
            "products": {
                "display_name": "Товары",
                "columns": ("id", "name", "price", "count", "type_name"),
                "headings": ("ID", "Название", "Цена", "Кол-во", "Тип товара"),
                "widths": {"id": 50, "count": 80, "name": 250, "price": 100, "type_name": 150},
                "foreign_keys": {"type_name": "type_id"}  # Для преобразования
            },
            "contractors": {
                "display_name": "Контрагенты",
                "columns": ("id", "name", "phone", "inn", "address"),
                "headings": ("ID", "Название", "Телефон", "ИНН", "Адрес"),
                "widths": {"id": 50, "name": 200, "phone": 120, "inn": 120, "address": 200}
            },
            "employees": {
                "display_name": "Сотрудники",
                "columns": ("id", "name", "position_name"),
                "headings": ("ID", "ФИО", "Должность"),
                "widths": {"id": 50, "name": 300, "position_name": 200},
                "foreign_keys": {"position_name": "position_id"}
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

        # Привязываем поиск к нажатию клавиши Enter
        self.search_entry.bind("<Return>", lambda e: self.on_search())

        search_button = ttk.Button(search_frame, text="Найти", style="Button.TButton", command=self.on_search)
        search_button.pack(anchor="center", pady=(0, 10))

        # Кнопка сброса поиска
        reset_button = ttk.Button(search_frame, text="Сбросить", style="Button.TButton", command=self.reset_search)
        reset_button.pack(anchor="center")

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
        self.current_search_term = ""  # Сбрасываем поиск при смене таблицы
        self.search_entry.delete(0, END)  # Очищаем поле поиска

        bg_color = "#3C4250"
        for key, lbl in self.tab_labels.items():
            if key == table_name:
                lbl.configure(fg="#FFFFFF", font=("Arial", 12, "bold"), bg=bg_color)
            else:
                lbl.configure(fg="#888888", font=("Arial", 12), bg=bg_color)

        # Конфигурация колонок
        config = self.table_configs[table_name]
        self.tree["columns"] = config["columns"]
        for i, col in enumerate(config["columns"]):
            self.tree.heading(col, text=config["headings"][i])
            w = config["widths"].get(col, 150)
            self.tree.column(col, width=w, anchor="center" if col != "name" else "w")

        self.load_data()

    def load_data(self):
        """Загрузка данных с учетом поиска"""
        self.tree.delete(*self.tree.get_children())

        if self.current_search_term:
            # Если есть активный поиск, используем поиск
            data = search_records(self.current_table, self.current_search_term)
        else:
            # Иначе загружаем все данные
            data = get_any_table(self.current_table)

        for row in data:
            self.tree.insert("", END, values=row)

    def on_search(self):
        """Обработчик поиска"""
        search_term = self.search_entry.get().strip()
        if search_term:
            self.current_search_term = search_term
            self.load_data()
        else:
            self.reset_search()

    def reset_search(self):
        """Сброс поиска"""
        self.current_search_term = ""
        self.search_entry.delete(0, END)
        self.load_data()

    def on_add_click(self):
        config = self.table_configs[self.current_table]

        fields_to_input = [col for col in config["columns"] if col != "id"]
        labels_to_show = [config["headings"][config["columns"].index(col)] for col in fields_to_input]

        add_window = Toplevel(self.main_frame, background="#1D1D21")
        add_window.title(f"Добавить: {config['display_name']}")
        add_window.geometry("400x450")
        add_window.resizable(width=False, height=False)
        add_window.grab_set()

        entries = {}
        comboboxes = {}

        for i, (field, label_text) in enumerate(zip(fields_to_input, labels_to_show)):
            ttk.Label(add_window, text=label_text, font=("Arial", 10),
                      foreground="white",
                      style="SmallText.TLabel").pack(pady=(10, 0))

            # Проверяем, является ли поле внешним ключом
            if self.current_table in ["products", "employees"] and field in ["type_name", "position_name"]:
                # Создаем Combobox для выбора
                foreign_field = "type_id" if field == "type_name" else "position_id"
                options = get_foreign_key_options(self.current_table, foreign_field)

                combo = ttk.Combobox(add_window, values=options, width=27, state="readonly")
                combo.pack()
                if options:
                    combo.set(options[0])  # Выбираем первый элемент по умолчанию
                comboboxes[field] = combo
            else:
                # Обычное поле ввода
                entry = ttk.Entry(add_window, width=30)
                entry.pack()
                entries[field] = entry

        def save_new_record():
            # Собираем данные
            values = []
            for field in fields_to_input:
                if field in comboboxes:
                    values.append(comboboxes[field].get())
                else:
                    values.append(entries[field].get())

            if any(v == "" for v in values):
                messagebox.showwarning("Ошибка валидации", "Заполните все поля!")
                return

            # Отправляем в БД
            success, message = add_record(self.current_table, fields_to_input, tuple(values))

            if success:
                messagebox.showinfo("Успех", message)
                add_window.destroy()
                self.reset_search()  # Сбрасываем поиск
                self.load_data()
            else:
                messagebox.showerror("Ошибка добавления", f"Невозможно добавить запись:\n{message}")

        # Добавляем подсказку для полей с ценой/количеством
        if self.current_table == "products":
            hint_label = ttk.Label(add_window,
                                   text="* Цена должна быть больше 0, количество не может быть отрицательным",
                                   font=("Arial", 8), foreground="#FFA500",
                                   style="SmallText.TLabel")
            hint_label.pack(pady=(10, 0))

        ttk.Button(add_window, text="Сохранить", command=save_new_record, style="Button.TButton").pack(pady=20)

    def on_edit_click(self):
        # Проверяем, выбрана ли строка в таблице
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите строку для редактирования!")
            return

        # Извлекаем текущие значения строки и конфигурацию таблицы
        row_values = self.tree.item(selected_item)['values']
        config = self.table_configs[self.current_table]

        # ID всегда идет первым в списке колонок
        record_id = row_values[0]

        # Исключаем ID из полей для редактирования
        fields_to_edit = [col for col in config["columns"] if col != "id"]

        # Создаем модальное окно редактирования
        edit_window = Toplevel(self.main_frame, background="#1D1D21")
        edit_window.title(f"Редактировать запись ID {record_id} — {config['display_name']}")
        edit_window.geometry("400x500")
        edit_window.resizable(width=False, height=False)
        edit_window.grab_set()

        entries = {}
        comboboxes = {}

        # Строим поля ввода и заполняем их старыми данными
        for i, field in enumerate(fields_to_edit):
            # Находим индекс колонки в общем списке, чтобы правильно сопоставить с row_values
            idx = config["columns"].index(field)
            label_text = config["headings"][idx]
            old_value = row_values[idx]

            ttk.Label(edit_window, text=label_text, font=("Arial", 10),
                      foreground="white",
                      style="SmallText.TLabel").pack(pady=(10, 0))

            # Проверяем, является ли поле внешним ключом
            if self.current_table in ["products", "employees"] and field in ["type_name", "position_name"]:
                # Создаем Combobox для выбора
                foreign_field = "type_id" if field == "type_name" else "position_id"
                options = get_foreign_key_options(self.current_table, foreign_field)

                combo = ttk.Combobox(edit_window, values=options, width=27, state="readonly")
                combo.pack()
                if old_value in options:
                    combo.set(old_value)
                elif options:
                    combo.set(options[0])
                comboboxes[field] = combo
            else:
                # Обычное поле ввода
                entry = ttk.Entry(edit_window, width=30)
                entry.pack()
                entry.insert(0, old_value)
                entries[field] = entry

        def save_changes():
            new_values = []
            for field in fields_to_edit:
                if field in comboboxes:
                    new_values.append(comboboxes[field].get())
                else:
                    new_values.append(entries[field].get())

            if any(v == "" for v in new_values):
                messagebox.showwarning("Ошибка валидации", "Поля не должны быть пустыми!")
                return

            # Вызываем универсальный UPDATE запрос
            success, message = update_record(self.current_table, fields_to_edit, new_values, record_id)

            if success:
                messagebox.showinfo("Успех", message)
                edit_window.destroy()
                self.reset_search()  # Сбрасываем поиск
                self.load_data()
            else:
                messagebox.showerror("Ошибка редактирования", f"Невозможно обновить запись:\n{message}")

        # Добавляем подсказку для полей с ценой/количеством
        if self.current_table == "products":
            hint_label = ttk.Label(edit_window,
                                   text="* Цена должна быть больше 0, количество не может быть отрицательным",
                                   font=("Arial", 8), foreground="#FFA500",
                                   style="SmallText.TLabel")
            hint_label.pack(pady=(10, 0))

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

        # Получаем название записи для информативного сообщения
        record_name = row_values[1] if len(row_values) > 1 else f"ID {record_id}"

        config = self.table_configs[self.current_table]

        # Специальные сообщения для разных таблиц
        if self.current_table == "positions":
            confirm_msg = f"Удалить должность '{record_name}'?\n\nВнимание! Если есть сотрудники с этой должностью, удаление будет невозможно."
        elif self.current_table == "product_types":
            confirm_msg = f"Удалить тип товара '{record_name}'?\n\nВнимание! Если есть товары этого типа, удаление будет невозможно."
        else:
            confirm_msg = f"Удалить запись '{record_name}' из таблицы {config['display_name']}?"

        confirm = messagebox.askyesno("Подтверждение удаления", confirm_msg)

        if confirm:
            success, message = delete_record(self.current_table, record_id)

            if success:
                messagebox.showinfo("Успех", message)
                self.reset_search()  # Сбрасываем поиск
                self.load_data()
            else:
                messagebox.showerror("Ошибка удаления", f"Невозможно удалить запись:\n{message}")

    def destroy(self):
        if self.db_conn:
            self.db_conn.close()
        for widget in self.main_frame.winfo_children():
            widget.destroy()