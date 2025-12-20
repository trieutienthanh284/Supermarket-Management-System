import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from services import ReportService
from interface.tab_for_sales import SaleTab
from interface.tab_for_employee import EmployeeTab
from interface.tab_for_customer import CustomerTab

class MainWindow:
    def __init__(self, root, employee):
        self.root = root
        self.employee = employee
        self.root.title(f"HỆ THỐNG QUẢN LÝ SIÊU THỊ - {employee['name']} ({employee['title']})")
        self.root.geometry("1380x730")
        self.root.state('zoomed')

        self.report_service = ReportService()

        self.create_layout()

    def create_layout(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=f"Chào mừng {self.employee['name']} - Chức vụ: {self.employee['title']}",
                 font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=15)

        tk.Button(header, text="ĐĂNG XUẤT", font=("Arial", 12, "bold"),
                  bg="#e74c3c", fg="white", width=15, height=2,
                  command=self.logout).pack(side="right", padx=20, pady=15)

        # Notebook (các tab)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Phân quyền tab theo chức vụ
        title = self.employee['title'].strip()

        if title in ['Quản lý', 'Phó quản lý']:
            self.create_sale_tab()
            self.create_product_tab()
            self.create_customer_tab()
            self.create_employee_tab()
            self.create_report_tab()
        elif title == 'Thu ngân':
            self.create_sale_tab()
        else:
            messagebox.showerror("Quyền truy cập", f"Chức vụ '{title}' không được phép sử dụng hệ thống này!")
            self.root.destroy()
            return

    # Các tab
    def create_sale_tab(self):
        sale_tab = SaleTab(self.notebook, self.employee)  # Truyền employee nếu cần
        self.notebook.add(sale_tab, text="BÁN HÀNG")

    def create_product_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="QUẢN LÝ SẢN PHẨM")

        label = tk.Label(tab, text="DANH SÁCH & QUẢN LÝ SẢN PHẨM\n(Sẽ hoàn thiện sau)", font=("Arial", 24), fg="#3498db")
        label.pack(expand=True)

    def create_customer_tab(self):
        customer_tab = CustomerTab(self.notebook)
        self.notebook.add(customer_tab, text="QUẢN LÝ KHÁCH HÀNG")

    def create_employee_tab(self):
        employee_tab = EmployeeTab(self.notebook)
        self.notebook.add(employee_tab, text="QUẢN LÝ NHÂN VIÊN")

    def create_report_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="BÁO CÁO")

        title = tk.Label(tab, text="BÁO CÁO TỔNG HỢP DOANH THU & HOẠT ĐỘNG", font=("Arial", 18, "bold"))
        title.pack(pady=20)

        btn = tk.Button(tab, text="XEM BÁO CÁO CHI TIẾT", font=("Arial", 14, "bold"),
                        width=40, height=2, bg="#f39c12", fg="white",
                        command=self.show_report)
        btn.pack(pady=20)

        self.report_text = scrolledtext.ScrolledText(tab, width=150, height=30, font=("Courier", 10))
        self.report_text.pack(padx=20, pady=10, fill="both", expand=True)

    def show_report(self):
        self.report_text.delete(1.0, tk.END)
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = captured = StringIO()

        self.report_service.print_all_reports()  # Gọi hàm báo cáo tổng hợp

        sys.stdout = old_stdout
        self.report_text.insert(tk.END, captured.getvalue())

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.root.destroy()
            # Quay lại login
            import tkinter as tk
            from interface.login_dashboard import LoginWindow
            new_root = tk.Tk()
            LoginWindow(new_root, lambda e: MainWindow(tk.Tk(), e))
            new_root.mainloop()