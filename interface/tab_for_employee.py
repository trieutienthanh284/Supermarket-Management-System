# ui/employee_tab.py - QUẢN LÝ NHÂN VIÊN (lấy data thật từ database)
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

class EmployeeTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_employees()  # Load ngay khi mở tab

    def get_db_connection(self):
        try:
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='123456789',
                database='quản lý siêu thị',
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
        except Error as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối database: {e}")
            return None

    def create_widgets(self):
        # Header
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)

        tk.Label(header, text="QUẢN LÝ NHÂN VIÊN", font=("Arial", 20, "bold")).pack(side="left", padx=20)

        tk.Button(header, text="THÊM NHÂN VIÊN MỚI", font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
                  command=self.add_employee).pack(side="right", padx=20)

        # Tìm kiếm
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Tìm kiếm:", font=("Arial", 12)).pack(side="left", padx=20)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.entry_search.pack(side="left", padx=10)
        tk.Button(search_frame, text="Tìm", bg="#3498db", fg="white",
                  command=self.search_employee).pack(side="left", padx=10)
        tk.Button(search_frame, text="Tất cả", bg="#95a5a6", fg="white",
                  command=self.load_employees).pack(side="left", padx=10)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Mã NV", "Họ tên", "SĐT", "Ngày sinh", "Giới tính", "CMND", "Chức vụ", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.edit_employee)

        tk.Button(self, text="CHO NGHỈ VIỆC", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white",
                  command=self.delete_employee).pack(pady=10)

    def load_employees(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT employee_id, name, phone_number, DATE_FORMAT(birthday, '%d/%m/%Y'), gender, 
                       identification, title, IF(is_working=1, 'Đang làm', 'Đã nghỉ') 
                FROM employee 
                ORDER BY employee_id
            """)
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_tree(self, employees):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for emp in employees:
            self.tree.insert("", "end", values=emp)

    def add_employee(self):
        # Popup thêm nhân viên mới
        dialog = tk.Toplevel(self)
        dialog.title("Thêm nhân viên mới")
        dialog.geometry("500x700")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f2f5")

        # Tự sinh mã nhân viên tiếp theo (lấy từ database)
        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT employee_id FROM employee ORDER BY employee_id DESC LIMIT 1")
                last = cursor.fetchone()
                if last:
                    last_num = int(last[0][2:])  # Lấy số từ NVxxx
                    next_num = last_num + 1
                else:
                    next_num = 1
                next_id = f"NV{next_num:03d}"
            except:
                next_id = "NV001"  # fallback
            finally:
                cursor.close()
                conn.close()
        else:
            next_id = "NV001"

        tk.Label(dialog, text="THÊM NHÂN VIÊN MỚI", font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=20)
        tk.Label(dialog, text=f"Mã nhân viên: {next_id}", font=("Arial", 14), bg="#f0f2f5", fg="#2c3e50").pack(pady=10)

        fields = [
            "Họ và tên",
            "Số điện thoại",
            "Ngày sinh (dd/mm/yyyy)",
            "Giới tính (Nam/Nữ/Khác)",
            "CMND/CCCD",
            "Chức vụ"
        ]
        entries = {}

        for field in fields:
            frame = tk.Frame(dialog, bg="#f0f2f5")
            frame.pack(fill="x", padx=50, pady=8)
            tk.Label(frame, text=field + ":", font=("Arial", 12), bg="#f0f2f5", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame, font=("Arial", 12), width=35)
            entry.pack(side="left", fill="x", expand=True)
            entries[field] = entry

        def save():
            data = [next_id]
            for field in fields:
                val = entries[field].get().strip()
                if not val:
                    messagebox.showerror("Lỗi", f"Vui lòng nhập {field}")
                    return
                data.append(val)
            data.append(1)  # is_working = 1

            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO employee 
                        (employee_id, name, phone_number, birthday, gender, identification, title, is_working)
                        VALUES (%s, %s, %s, STR_TO_DATE(%s, '%d/%m/%Y'), %s, %s, %s, %s)
                    """, data)
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Đã thêm nhân viên {data[1]} - Mã {next_id}")
                    self.load_employees()  # Cập nhật danh sách
                    dialog.destroy()
                except Error as e:
                    messagebox.showerror("Lỗi database", f"Không thể thêm: {e}")
                    conn.rollback()
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(dialog, text="LƯU NHÂN VIÊN", font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                  width=25, height=2, command=save).pack(pady=30)

    def edit_employee(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item['values']
        emp_id = values[0]

        dialog = tk.Toplevel(self)
        dialog.title("Sửa thông tin nhân viên")
        dialog.geometry("500x700")
        dialog.configure(bg="#f0f2f5")

        fields = ["Họ và tên", "Số điện thoại", "Ngày sinh (dd/mm/yyyy)", "Giới tính", "CMND/CCCD", "Chức vụ"]
        entries = {}

        tk.Label(dialog, text=f"SỬA NHÂN VIÊN: {emp_id}", font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=20)

        for i, field in enumerate(fields):
            frame = tk.Frame(dialog, bg="#f0f2f5")
            frame.pack(fill="x", padx=50, pady=8)
            tk.Label(frame, text=field + ":", font=("Arial", 12), bg="#f0f2f5", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame, font=("Arial", 12), width=35)
            entry.insert(0, values[i+1])
            entry.pack(side="left", fill="x", expand=True)
            entries[field] = entry

        def save():
            new_data = []
            for field in fields:
                new_data.append(entries[field].get().strip())

            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE employee SET 
                        name = %s, phone_number = %s, birthday = STR_TO_DATE(%s, '%d/%m/%Y'),
                        gender = %s, identification = %s, title = %s
                        WHERE employee_id = %s
                    """, (*new_data, emp_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên!")
                    self.load_employees()
                    dialog.destroy()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
                    conn.rollback()
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(dialog, text="LƯU THAY ĐỔI", font=("Arial", 14, "bold"), bg="#3498db", fg="white",
                  width=25, height=2, command=save).pack(pady=30)

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn nhân viên", "Vui lòng chọn nhân viên cần cho nghỉ việc!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        emp_id = values[0]
        name = values[1]

        if messagebox.askyesno("Xác nhận", f"Cho nhân viên {name} ({emp_id}) nghỉ việc?"):
            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE employee SET is_working = 0 WHERE employee_id = %s", (emp_id,))
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Nhân viên {name} đã nghỉ việc!")
                    self.load_employees()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
                finally:
                    cursor.close()
                    conn.close()

    def search_employee(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_employees()
            return

        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT employee_id, name, phone_number, DATE_FORMAT(birthday, '%d/%m/%Y'), gender, 
                       identification, title, IF(is_working=1, 'Đang làm', 'Đã nghỉ')
                FROM employee 
                WHERE name LIKE %s OR phone_number LIKE %s OR identification LIKE %s OR title LIKE %s
                ORDER BY employee_id
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {e}")
        finally:
            cursor.close()
            conn.close()
