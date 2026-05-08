from tkinter import *
from app import AppStockFlow
from view.main_window import MainWindow

if __name__ == "__main__":
    root = Tk()
    app = AppStockFlow(root)

    app.show_window(MainWindow)

    root.mainloop()
