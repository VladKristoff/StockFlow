from tkinter import *
from app import AppStockFlow
from view.table_window import TableWindow

if __name__ == "__main__":
    root = Tk()
    app = AppStockFlow(root)

    app.show_window(TableWindow)

    root.mainloop()
