#Chạy toàn bộ hệ thống
import tkinter as tk
from interface.login_dashboard import LoginWindow
from interface.main_dashboard import MainWindow

def open_dashboard(employee):
    root = tk.Tk()
    MainWindow(root, employee)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, open_dashboard)
    root.mainloop()



