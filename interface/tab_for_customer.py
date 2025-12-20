import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

class CustomerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_customers()

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

        tk.Label(header, text="QUẢN LÝ KHÁCH HÀNG", font=("Arial", 20, "bold")).pack(side="left", padx=20)

        tk.Button(header, text="THÊM KHÁCH MỚI", font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
                  width=18, height=2, command=self.add_new_customer).pack(side="right", padx=20, pady=10)

        # Tìm kiếm
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Tìm kiếm:", font=("Arial", 12)).pack(side="left", padx=20)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.entry_search.pack(side="left", padx=10)
        tk.Button(search_frame, text="Tìm", bg="#3498db", fg="white",
                  command=self.search_customer).pack(side="left", padx=10)
        tk.Button(search_frame, text="Tất cả", bg="#95a5a6", fg="white",
                  command=self.load_customers).pack(side="left", padx=10)

        # Treeview danh sách khách
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Mã KH", "Họ tên", "SĐT", "Điểm tích lũy", "Tổng tiền mua", "Số lần mua")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.edit_customer)

        # Nút chỉnh điểm thủ công
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="CHỈNH ĐIỂM TÍCH LŨY", font=("Arial", 12, "bold"), bg="#f39c12", fg="white",
                  command=self.adjust_points).pack(side="left", padx=20)

    def load_customers(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.customer_id, 
                    c.name, 
                    c.phone_number, 
                    c.shopping_point,
                    COALESCE(SUM(b.total_amount), 0) AS total_spent,
                    COALESCE(COUNT(b.bill_id), 0) AS total_bills
                FROM customer c
                LEFT JOIN bill b ON c.customer_id = b.customer_id
                GROUP BY c.customer_id
                ORDER BY c.shopping_point DESC
            """)
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_tree(self, customers):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cust in customers:
            self.tree.insert("", "end", values=(
                cust[0], cust[1], cust[2], cust[3], f"{cust[4]:,.0f}", cust[5]
            ))

    def search_customer(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_customers()
            return

        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.customer_id, 
                    c.name, 
                    c.phone_number, 
                    c.shopping_point,
                    COALESCE(SUM(b.total_amount), 0) AS total_spent,
                    COALESCE(COUNT(b.bill_id), 0) AS total_bills
                FROM customer c
                LEFT JOIN bill b ON c.customer_id = b.customer_id
                WHERE c.name LIKE %s OR c.phone_number LIKE %s
                GROUP BY c.customer_id
                ORDER BY c.shopping_point DESC
            """, (f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {e}")
        finally:
            cursor.close()
            conn.close()

    def edit_customer(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item['values']
        cust_id = values[0]

        dialog = tk.Toplevel(self)
        dialog.title("Sửa thông tin khách hàng")
        dialog.geometry("500x400")

        fields = ["Họ tên", "Số điện thoại"]
        entries = {}

        tk.Label(dialog, text=f"Mã KH: {cust_id}", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(dialog, text=f"Điểm hiện tại: {values[3]}", font=("Arial", 12)).pack(pady=10)

        for i, field in enumerate(fields):
            frame = tk.Frame(dialog)
            frame.pack(fill="x", padx=50, pady=10)
            tk.Label(frame, text=field + ":", font=("Arial", 12), width=15, anchor="w").pack(side="left")
            entry = tk.Entry(frame, font=("Arial", 12), width=30)
            entry.insert(0, values[i+1])
            entry.pack(side="left")
            entries[field] = entry

        def save():
            new_name = entries["Họ tên"].get().strip()
            new_phone = entries["Số điện thoại"].get().strip()

            if not new_name or not new_phone:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ")
                return

            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE customer SET name = %s, phone_number = %s WHERE customer_id = %s
                    """, (new_name, new_phone, cust_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng!")
                    self.load_customers()
                    dialog.destroy()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(dialog, text="LƯU THAY ĐỔI", font=("Arial", 14, "bold"), bg="#3498db", fg="white",
                  width=20, height=2, command=save).pack(pady=30)

    def adjust_points(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn khách", "Vui lòng chọn khách hàng cần chỉnh điểm!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        cust_id = values[0]
        current_points = values[3]

        new_points = simpledialog.askinteger("Chỉnh điểm", f"Điểm hiện tại: {current_points}\nNhập điểm mới:",
                                             minvalue=0)
        if new_points is None:
            return

        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE customer SET shopping_point = %s WHERE customer_id = %s", (new_points, cust_id))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã chỉnh điểm thành {new_points}")
                self.load_customers()
            except Error as e:
                messagebox.showerror("Lỗi", f"Không thể chỉnh điểm: {e}")
            finally:
                cursor.close()
                conn.close()

    def add_new_customer(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm khách hàng mới")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f2f5")

        tk.Label(dialog, text="THÊM KHÁCH HÀNG MỚI", font=("Arial", 18, "bold"), bg="#f0f2f5", fg="#2c3e50").pack(pady=30)

        # Tự sinh mã KH tiếp theo
        conn = self.get_db_connection()
        next_id = "KH001"
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1")
                last = cursor.fetchone()
                if last:
                    last_num = int(last[0][2:])  # Lấy số từ KHxxx
                    next_num = last_num + 1
                    next_id = f"KH{next_num:03d}"
            except:
                next_id = "KH001"
            finally:
                cursor.close()
                conn.close()

        tk.Label(dialog, text=f"Mã khách hàng: {next_id}", font=("Arial", 14), bg="#f0f2f5", fg="#2980b9").pack(pady=10)

        # Nhập tên
        tk.Label(dialog, text="Họ và tên:", font=("Arial", 12), bg="#f0f2f5").pack(pady=10)
        entry_name = tk.Entry(dialog, font=("Arial", 12), width=35)
        entry_name.pack(pady=5)

        # Nhập SĐT
        tk.Label(dialog, text="Số điện thoại:", font=("Arial", 12), bg="#f0f2f5").pack(pady=10)
        entry_phone = tk.Entry(dialog, font=("Arial", 12), width=35)
        entry_phone.pack(pady=5)

        def save():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()

            if not name or not phone:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên và số điện thoại!")
                return

            if not phone.isdigit() or len(phone) < 10:
                messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ!")
                return

            conn = self.get_db_connection()
            if not conn:
                return

            try:
                cursor = conn.cursor()
                # Kiểm tra trùng SĐT
                cursor.execute("SELECT customer_id FROM customer WHERE phone_number = %s", (phone,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Số điện thoại này đã tồn tại!")
                    return

                # Thêm khách mới
                cursor.execute("""
                    INSERT INTO customer (customer_id, name, phone_number, shopping_point)
                    VALUES (%s, %s, %s, 0)
                """, (next_id, name, phone))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã thêm khách mới:\n{next_id} - {name}\nSĐT: {phone}")
                self.load_customers()  # Refresh danh sách
                dialog.destroy()
            except Error as e:
                messagebox.showerror("Lỗi database", f"Không thể thêm khách: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()

        tk.Button(dialog, text="LƯU KHÁCH HÀNG", font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                  width=25, height=2, command=save).pack(pady=30)
