from tkinter import *
from tkinter import ttk, messagebox
from database.db_doc_manager import get_all_documents, get_document_items, get_document_by_id, delete_document, \
    create_document
from database.db_manager import get_any_table
from utils.doc_generator import create_expense_invoice
import os
from datetime import datetime


class ExpensesWindow:
    def __init__(self, main_frame, app):
        self.tree = None
        self.main_frame = main_frame
        self.app = app
        self.bg_color = "#3C4250"

        self.contractors = get_any_table("contractors")
        self.employees = get_any_table("employees")
        self.products = get_any_table("products")

        self.contractor_map = {row[1]: row[0] for row in self.contractors}
        self.employee_map = {row[1]: row[0] for row in self.employees}
        self.product_map = {row[1]: (row[0], row[2], row[3]) for row in self.products}

        self.create_widgets()

    def create_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        top_bar = Frame(self.main_frame, background=self.bg_color)
        top_bar.pack(side="top", fill="x", padx=(67, 20), pady=(15, 0))

        title = ttk.Label(top_bar, text="StockFlow", style="Text.TLabel")
        title.pack(side="left", padx=(0, 50))

        add_btn = ttk.Button(top_bar, text="Добавить", style="Button.TButton", command=self.open_add_dialog)
        add_btn.pack(side="right", padx=10)

        delete_btn = ttk.Button(top_bar, text="Удалить", style="Button.TButton", command=self.delete_document)
        delete_btn.pack(side="right", padx=10)

        refresh_btn = ttk.Button(top_bar, text="Обновить", style="Button.TButton", command=self.load_data)
        refresh_btn.pack(side="right", padx=10)

        self.create_table()

    def create_table(self):
        table_frame = Frame(self.main_frame, background=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=30, pady=30)

        columns = ("id", "doc_number", "doc_date", "created_at", "contractor", "employee")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")

        self.tree.heading("id", text="ID")
        self.tree.heading("doc_number", text="№ Документа")
        self.tree.heading("doc_date", text="Дата документа")
        self.tree.heading("created_at", text="Дата создания")
        self.tree.heading("contractor", text="Контрагент")
        self.tree.heading("employee", text="Ответственный")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("doc_number", width=150, anchor="center")
        self.tree.column("doc_date", width=120, anchor="center")
        self.tree.column("created_at", width=180, anchor="center")
        self.tree.column("contractor", width=200, anchor="center")
        self.tree.column("employee", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-Button-1>", self.view_document)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = get_all_documents(2)
        for row in data:
            self.tree.insert("", "end", values=row)

    def open_add_dialog(self):
        AddExpenseDocumentDialog(self.main_frame, self)

    def view_document(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            doc_id = item['values'][0]
            ViewExpenseDocumentDialog(self.main_frame, self, doc_id)

    def delete_document(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите документ для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный документ? Это действие нельзя отменить!"):
            item = self.tree.item(selection[0])
            doc_id = item['values'][0]

            success, message = delete_document(doc_id, 2)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_data()
            else:
                messagebox.showerror("Ошибка", message)

    def destroy(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


class AddExpenseDocumentDialog:
    def __init__(self, parent, window):
        self.window = window
        self.items = []

        self.dialog = Toplevel(parent)
        self.dialog.title("Добавление расходной накладной")
        self.dialog.geometry("730x700")
        self.dialog.resizable(False, False)
        self.dialog.configure(background="#3C4250")

        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self.dialog, background="#3C4250")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Контрагент
        ttk.Label(main_frame, text="Контрагент:",
                 style="SmallText.TLabel",
                 font="Arial, 14").grid(row=0, column=0, sticky="w", pady=5)

        self.contractor_combo = ttk.Combobox(main_frame, values=list(self.window.contractor_map.keys()), width=40)
        self.contractor_combo.grid(row=0, column=1, sticky="w", pady=8, padx=10)

        # Ответственный
        ttk.Label(main_frame, text="Ответственный:", style="SmallText.TLabel", font="Arial, 14").grid(row=1, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=5)

        self.employee_combo = ttk.Combobox(main_frame, values=list(self.window.employee_map.keys()), width=40)
        self.employee_combo.grid(row=1, column=1, sticky="w", pady=8, padx=10)

        # Дата
        ttk.Label(main_frame, text="Дата документа:", style="SmallText.TLabel", font="Arial, 14").grid(row=2, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=5)
        self.date_entry = Entry(main_frame, width=30, font=("Arial", 11))
        self.date_entry.grid(row=2, column=1, sticky="w", pady=8, padx=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Текущая дата

        # Товары
        ttk.Label(main_frame, text="Товары:", style="SmallText.TLabel", font=("Arial Black", 17)).grid(row=3, column=0,
                                                                                                       columnspan=2,
                                                                                                       sticky="w",
                                                                                                       pady=(20, 10))

        # Фрейм для таблицы
        table_frame = Frame(main_frame, background="#3C4250")
        table_frame.grid(row=4, column=0, columnspan=2, pady=10)

        columns = ("product", "quantity", "price", "available", "total")
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        self.items_tree.heading("product", text="Товар")
        self.items_tree.heading("quantity", text="Кол-во")
        self.items_tree.heading("price", text="Цена")
        self.items_tree.heading("available", text="Доступно")
        self.items_tree.heading("total", text="Сумма")

        self.items_tree.column("product", width=250)
        self.items_tree.column("quantity", width=100, anchor="center")
        self.items_tree.column("price", width=100, anchor="center")
        self.items_tree.column("available", width=100, anchor="center")
        self.items_tree.column("total", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления товарами
        btn_frame = Frame(main_frame, background="#3C4250")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        (ttk.Button(btn_frame, text="Добавить товар", command=self.add_product, style="Button.TButton")
         .pack(side="left", padx=5))
        (ttk.Button(btn_frame, text="Удалить товар", command=self.remove_product, style="Button.TButton")
         .pack(side="left", padx=5))

        # Итоговая сумма
        self.total_label = Label(main_frame, text="Общая сумма: 0.00 руб.", bg="#3C4250", fg="#B9FFDC",
                                 font=("Arial", 15, "bold"))
        self.total_label.grid(row=6, column=0, columnspan=2, pady=20)

        action_frame = Frame(main_frame, background="#3C4250")
        action_frame.grid(row=7, column=0, columnspan=2, pady=25)

        ttk.Button(action_frame, text="Сохранить", command=self.save_document, style="Button.TButton",
               width=15).pack(side="left", padx=10)
        ttk.Button(action_frame, text="Отмена", command=self.dialog.destroy, style="Button.TButton",
               width=15).pack(side="left", padx=10)

    def add_product(self):
        AddExpenseProductDialog(self.dialog, self)

    def remove_product(self):
        selection = self.items_tree.selection()
        if selection:
            item = self.items_tree.item(selection[0])
            for i, prod in enumerate(self.items):
                if prod[0] == item['values'][0]:
                    self.items.pop(i)
                    break
            self.update_items_table()

    def update_items_table(self):
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        total = 0
        for product_name, product_id, quantity, price, available in self.items:
            summa = quantity * price
            total += summa
            self.items_tree.insert("", "end",
                                   values=(product_name, quantity, f"{price:.2f}", available, f"{summa:.2f}"))

        if any(qty > avail for _, _, qty, _, avail in self.items):
            self.total_label.config(text=f"⚠️ Общая сумма: {total:.2f} руб. (ВНИМАНИЕ: есть превышение!)",
                                    foreground="#FF6B6B")
        else:
            self.total_label.config(text=f"💰 Общая сумма: {total:.2f} руб.", foreground="#B9FFDC")

    def save_document(self):
        if not self.contractor_combo.get():
            messagebox.showerror("Ошибка", "Выберите контрагента!")
            return
        if not self.employee_combo.get():
            messagebox.showerror("Ошибка", "Выберите ответственного!")
            return
        if not self.items:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один товар!")
            return

        # Проверка наличия товаров
        for product_name, product_id, quantity, price, available in self.items:
            if quantity > available:
                messagebox.showerror("Ошибка",
                                     f"Недостаточно товара '{product_name}'!\nДоступно: {available}, запрошено: {quantity}")
                return

        contractor_id = self.window.contractor_map[self.contractor_combo.get()]
        employee_id = self.window.employee_map[self.employee_combo.get()]
        doc_date = self.date_entry.get()

        items_for_db = [(prod_id, qty, price) for _, prod_id, qty, price, _ in self.items]

        success, message, doc_id = create_document(2, doc_date, contractor_id, employee_id, items_for_db)

        if success:
            messagebox.showinfo("Успех", f"Документ {message} успешно создан!")
            self.dialog.destroy()
            self.window.load_data()

            if messagebox.askyesno("Создать документ", "Создать Word документ накладной?"):
                doc_data = {
                    'doc_number': message,
                    'doc_date': doc_date,
                    'contractor_name': self.contractor_combo.get(),
                    'employee_name': self.employee_combo.get()
                }
                items_for_word = [{'product_name': name, 'quantity': qty, 'price': price}
                                  for name, _, qty, price, _ in self.items]

                filepath = create_expense_invoice(doc_id, doc_data, items_for_word)
                messagebox.showinfo("Успех", f"Документ сохранен: {filepath}")
                os.startfile(filepath)
        else:
            messagebox.showerror("Ошибка", message)


class AddExpenseProductDialog:
    def __init__(self, parent, parent_dialog):
        self.parent_dialog = parent_dialog
        self.dialog = Toplevel(parent)
        self.dialog.title("Добавить товар")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.configure(background="#3C4250")

        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self.dialog, background="#3C4250")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Товар:", style="SmallText.TLabel", font="Arial, 14").grid(row=0, column=0,
                                                                                              sticky="w",
                                                                                              pady=5)

        self.product_combo = ttk.Combobox(main_frame, values=list(self.parent_dialog.window.product_map.keys()),
                                          width=35)
        self.product_combo.grid(row=0, column=1, sticky="w", pady=8, padx=10)

        ttk.Label(main_frame, text="Количество:", style="SmallText.TLabel", font="Arial, 14").grid(row=1, column=0,
                                                                                                   sticky="w", pady=5)
        self.quantity_entry = Entry(main_frame, width=25, font=("Arial", 11))
        self.quantity_entry.grid(row=1, column=1, sticky="w", pady=8, padx=10)

        ttk.Label(main_frame, text="Доступно:", style="SmallText.TLabel", font="Arial, 14").grid(row=2, column=0,
                                                                                               sticky="w", pady=8)

        self.available_label = Label(main_frame, text="0", bg="#3C4250", fg="#B9FFDC", font=("Arial", 12, "bold"))
        self.available_label.grid(row=2, column=1, sticky="w", pady=8, padx=10)

        ttk.Label(main_frame, text="Цена:", style="SmallText.TLabel", font="Arial, 14").grid(row=3, column=0, sticky="w",
                                                                                           pady=8)
        self.price_label = Label(main_frame, text="0.00 руб.", bg="#3C4250", fg="#B9FFDC", font=("Arial", 12, "bold"))
        self.price_label.grid(row=3, column=1, sticky="w", pady=8, padx=10)

        self.product_combo.bind("<<ComboboxSelected>>", self.update_info)

        (ttk.Button(main_frame, text="Добавить", command=self.add, style="Button.TButton",
                    width=15).grid(row=4, column=0, columnspan=2, pady=20))

    def update_info(self, event):
        product_name = self.product_combo.get()
        if product_name in self.parent_dialog.window.product_map:
            product_id, price, count = self.parent_dialog.window.product_map[product_name]
            self.price_label.config(text=f"{price:.2f} руб.")
            self.available_label.config(text=str(count))
            self.current_product_id = product_id
            self.current_price = price
            self.current_available = count

    def add(self):
        if not self.product_combo.get():
            messagebox.showerror("Ошибка", "Выберите товар!")
            return

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше 0!")
                return
            if quantity > self.current_available:
                if not messagebox.askyesno("Внимание",
                                           f"Доступно только {self.current_available} единиц.\nДобавить в документ?"):
                    return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество!")
            return

        self.parent_dialog.items.append((
            self.product_combo.get(),
            self.current_product_id,
            quantity,
            self.current_price,
            self.current_available
        ))
        self.parent_dialog.update_items_table()
        self.dialog.destroy()


class ViewExpenseDocumentDialog:
    def __init__(self, parent, window, doc_id):
        self.window = window
        self.doc_id = doc_id

        doc_data = get_document_by_id(doc_id)
        items = get_document_items(doc_id)

        self.dialog = Toplevel(parent)
        self.dialog.title(f"Просмотр документа №{doc_data[1] if doc_data else ''}")
        self.dialog.geometry("1200x900")
        self.dialog.resizable(False, False)
        self.dialog.configure(background="#3C4250")

        if doc_data:
            self.create_widgets(doc_data, items)

    def create_widgets(self, doc_data, items):
        main_frame = Frame(self.dialog, background="#3C4250")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_frame = LabelFrame(main_frame, text="Информация о документе", bg="#3C4250", fg="white",
                                font=("Arial", 12, "bold"))
        info_frame.pack(fill="x", pady=10)

        info_text = f"""
        Номер документа: {doc_data[1]}
        Дата документа: {doc_data[2]}
        Дата создания: {doc_data[3]}
        Контрагент: {doc_data[7] if doc_data[7] else 'Не указан'}
        Ответственный: {doc_data[8] if doc_data[8] else 'Не указан'}
        """
        Label(info_frame, text=info_text, bg="#3C4250", fg="white", font=("Arial", 11), justify="left").pack(padx=10,
                                                                                                             pady=10)

        table_frame = LabelFrame(main_frame, text="Товары", bg="#3C4250", fg="white", font=("Arial", 12, "bold"))
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("product", "quantity", "price", "total")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        tree.heading("product", text="Товар")
        tree.heading("quantity", text="Кол-во")
        tree.heading("price", text="Цена")
        tree.heading("total", text="Сумма")

        tree.column("product", width=350)
        tree.column("quantity", width=100, anchor="center")
        tree.column("price", width=120, anchor="center")
        tree.column("total", width=150, anchor="center")

        total_sum = 0
        for item in items:
            total = item[3] * item[4]
            total_sum += total
            tree.insert("", "end", values=(item[2], item[3], f"{item[4]:.2f} руб.", f"{total:.2f} руб."))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        Label(main_frame, text=f"Общая сумма: {total_sum:.2f} руб.", bg="#3C4250", fg="#B9FFDC",
              font=("Arial", 15, "bold")).pack(pady=15)

        btn_frame = Frame(main_frame, background="#3C4250")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Создать документ Word", command=lambda: self.print_document(doc_data, items),
               style="Button.TButton").pack(side="left", padx=10)

        ttk.Button(btn_frame, text="Закрыть", command=self.dialog.destroy,
               style="Button.TButton").pack(side="left", padx=10)

    @staticmethod
    def print_document(doc_data, items):
        items_for_word = [{'product_name': item[2], 'quantity': item[3], 'price': item[4]} for item in items]

        doc_info = {
            'doc_number': doc_data[1],
            'doc_date': doc_data[2],
            'contractor_name': doc_data[7] if doc_data[7] else 'Не указан',
            'employee_name': doc_data[8] if doc_data[8] else 'Не указан'
        }

        filepath = create_expense_invoice(doc_data[0], doc_info, items_for_word)
        messagebox.showinfo("Успех", f"Документ сохранен: {filepath}")
        os.startfile(filepath)