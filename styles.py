from tkinter import *
from tkinter import ttk

def set_styles(root):
    style = ttk.Style(root)

    style.theme_use("clam")

    # Обычная кнопка
    style.configure("Button.TButton",
                    background="#2F323A",
                    font=("Inter Bold", 16),
                    width=22,
                    foreground="white",
                    borderwidth=0,
                    focusthickness=0,
                    focuscolor="none",
                    relief="flat")

    style.map("Button.TButton",
              background=[
                  ('pressed', '#595E6C'),
                  ('active', '#444853')
              ],
              foreground=[
                  ('pressed', 'white'),
                  ('active', 'white')
              ])

    # Обычная большая кнопка
    style.configure("BigButton.TButton",
                         background="#2F323A",
                         font=("Inter Bold", 16),
                         foreground="white",
                         width=20,
                         borderwidth=0,
                         focusthickness=0,
                         focuscolor="none",
                         relief="flat")

    style.map("BigButton.TButton",
              background=[
                  ('pressed', '#595E6C'),
                  ('active', '#444853')
              ],
              foreground=[
                  ('pressed', 'white'),
                  ('active', 'white')
              ])

    # Выбранная большая кнопка
    style.configure("Select.BigButton.TButton",
                    background="#444853")

    style.map("Select.BigButton.TButton",
              background=[('pressed', '#444853'), ('active', '#444853')],
              foreground=[('pressed', 'white'), ('active', 'white')])

    # Надпись StockFlow
    style.configure("Text.TLabel",
                    background="#3C4250",
                    foreground="white",
                    font=("Arial Black", 26))

    style.configure("SmallText.TLabel",
                    background="#3C4250",
                    foreground="white")

    # Надпись с информацией о подключении к БД
    style.configure("BD_info.TLabel",
                    background="#1D1D21",
                    font=("Arial", 14))

    # Entry поле
    style.configure("Entry.TEntry",
                    background="#7A7D84",)

    # Таблица
    # 1. Основной стиль таблицы
    style.configure("Treeview",
                    background="#1D1D21",
                    foreground="white",
                    rowheight=30,
                    fieldbackground="#1D1D21",
                    borderwidth=0,
                    font=("Arial", 11)
                    )

    # 2. Стиль заголовков
    style.configure("Treeview.Heading",
                    background="#2A2A2E",
                    foreground="white",
                    relief="flat",
                    font=("Arial", 12, "bold")
                    )

    # 3. Цвет выделенной строки
    style.map("Treeview",
              background=[('selected', '#444853')],
              foreground=[('selected', '#B9FFDC')])

    # 4. Цвет выделенного заголовка
    style.map("Treeview.Heading",
              background=[('selected', '#7A7D84')],
              foreground=[('selected', '#B9FFDC')])