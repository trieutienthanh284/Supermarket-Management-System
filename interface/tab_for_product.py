import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

class ProductTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_products()

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

        tk.Label(header, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 20, "bold")).pack(side="left", padx=20)

        btn_add = tk.Button(header, text="THÊM SẢN PHẨM MỚI", font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
                            command=self.add_product)
        btn_add.pack(side="right", padx=10)

        btn_stock = tk.Button(header, text="NHẬP KHO", font=("Arial", 12, "bold"), bg="#3498db", fg="white",
                              command=self.stock_in)
        btn_stock.pack(side="right", padx=10)

        # Tìm kiếm
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Tìm kiếm:", font=("Arial", 12)).pack(side="left", padx=20)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), width=50)
        self.entry_search.pack(side="left", padx=10)
        tk.Button(search_frame, text="Tìm", bg="#3498db", fg="white",
                  command=self.search_product).pack(side="left", padx=10)
        tk.Button(search_frame, text="Tất cả", bg="#95a5a6", fg="white",
                  command=self.load_products).pack(side="left", padx=10)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Tên sản phẩm", "Giá", "Tồn kho", "Danh mục", "Nhà cung cấp", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.edit_product)

        # Nút ngừng bán
        tk.Button(self, text="NGỪNG BÁN SẢN PHẨM", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white",
                  command=self.disable_product).pack(pady=10)

    def load_products(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.name, p.price, p.quantity, 
                       c.name AS category_name, s.name AS supplier_name,
                       IF(p.is_active=1, 'Đang bán', 'Ngừng bán')
                FROM product p
                LEFT JOIN category c ON p.category_id = c.category_id
                LEFT JOIN supplier s ON p.supplier_id = s.supplier_id
                ORDER BY p.product_id
            """)
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_tree(self, products):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in products:
            self.tree.insert("", "end", values=(
                p[0], p[1], f"{p[2]:,.0f}", p[3], p[4] or "N/A", p[5] or "N/A", p[6]
            ))

    def search_product(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_products()
            return

        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.name, p.price, p.quantity, 
                       c.name, s.name,
                       IF(p.is_active=1, 'Đang bán', 'Ngừng bán')
                FROM product p
                LEFT JOIN category c ON p.category_id = c.category_id
                LEFT JOIN supplier s ON p.supplier_id = s.supplier_id
                WHERE p.product_id LIKE %s OR p.name LIKE %s OR p.description LIKE %s
                ORDER BY p.product_id
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            self.update_tree(rows)
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {e}")
        finally:
            cursor.close()
            conn.close()

    def add_product(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm sản phẩm mới")
        dialog.geometry("600x700")
        dialog.configure(bg="#f0f2f5")

        # Tự sinh mã SP
        conn = self.get_db_connection()
        next_id = "SP001"
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT product_id FROM product ORDER BY product_id DESC LIMIT 1")
                last = cursor.fetchone()
                if last:
                    last_num = int(last[0][2:])
                    next_num = last_num + 1
                    next_id = f"SP{next_num:03d}"
            except:
                next_id = "SP001"
            finally:
                cursor.close()
                conn.close()

        tk.Label(dialog, text="THÊM SẢN PHẨM MỚI", font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=20)
        tk.Label(dialog, text=f"Mã sản phẩm: {next_id}", font=("Arial", 14), bg="#f0f2f5", fg="#2980b9").pack(pady=10)

        fields = ["Tên sản phẩm", "Giá bán", "Mô tả", "Số lượng ban đầu", "Danh mục (mã DMxxx)", "Nhà cung cấp (mã NCCxxx)"]
        entries = {}

        for field in fields:
            frame = tk.Frame(dialog, bg="#f0f2f5")
            frame.pack(fill="x", padx=50, pady=8)
            tk.Label(frame, text=field + ":", font=("Arial", 12), bg="#f0f2f5", width=25, anchor="w").pack(side="left")
            entry = tk.Entry(frame, font=("Arial", 12), width=40)
            entry.pack(side="left", fill="x", expand=True)
            entries[field] = entry

        def save():
            data = [next_id]
            for field in fields:
                val = entries[field].get().strip()
                if not val and field not in ["Mô tả", "Danh mục (mã DMxxx)", "Nhà cung cấp (mã NCCxxx)"]:
                    messagebox.showerror("Lỗi", f"Vui lòng nhập {field}")
                    return
                data.append(val if val else None)

            data.append(1)  # is_active = 1

            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO product 
                        (product_id, name, price, description, quantity, category_id, supplier_id, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, data)
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Đã thêm sản phẩm {data[1]} - Mã {next_id}")
                    self.load_products()
                    dialog.destroy()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể thêm: {e}")
                    conn.rollback()
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(dialog, text="LƯU SẢN PHẨM", font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                  width=30, height=2, command=save).pack(pady=30)

    def edit_product(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item['values']
        prod_id = values[0]

        dialog = tk.Toplevel(self)
        dialog.title("Sửa sản phẩm")
        dialog.geometry("600x700")
        dialog.configure(bg="#f0f2f5")

        fields = ["Tên sản phẩm", "Giá bán", "Mô tả", "Số lượng tồn kho", "Danh mục", "Nhà cung cấp"]
        entries = {}

        tk.Label(dialog, text=f"SỬA SẢN PHẨM: {prod_id}", font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=20)

        for i, field in enumerate(fields):
            frame = tk.Frame(dialog, bg="#f0f2f5")
            frame.pack(fill="x", padx=50, pady=8)
            tk.Label(frame, text=field + ":", font=("Arial", 12), bg="#f0f2f5", width=25, anchor="w").pack(side="left")
            entry = tk.Entry(frame, font=("Arial", 12), width=40)
            entry.insert(0, values[i+1])
            entry.pack(side="left", fill="x", expand=True)
            entries[field] = entry

        def save():
            new_data = []
            for field in fields:
                new_data.append(entries[field].get().strip() or None)

            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE product SET 
                        name = %s, price = %s, description = %s, quantity = %s,
                        category_id = %s, supplier_id = %s
                        WHERE product_id = %s
                    """, (*new_data, prod_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm!")
                    self.load_products()
                    dialog.destroy()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(dialog, text="LƯU THAY ĐỔI", font=("Arial", 14, "bold"), bg="#3498db", fg="white",
                  width=30, height=2, command=save).pack(pady=30)

    def disable_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn sản phẩm", "Vui lòng chọn sản phẩm cần ngừng bán!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        prod_id = values[0]
        name = values[1]

        if messagebox.askyesno("Xác nhận", f"Ngừng bán sản phẩm {name} ({prod_id})?"):
            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET is_active = 0 WHERE product_id = %s", (prod_id,))
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Sản phẩm {name} đã ngừng bán!")
                    self.load_products()
                except Error as e:
                    messagebox.showerror("Lỗi", f"Không thể ngừng bán: {e}")
                finally:
                    cursor.close()
                    conn.close()

    def stock_in(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn sản phẩm", "Vui lòng chọn sản phẩm cần nhập kho!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        prod_id = values[0]
        name = values[1]
        current_stock = values[3]

        qty = simpledialog.askinteger("Nhập kho", f"Nhập số lượng nhập kho cho {name} (hiện có {current_stock}):",
                                      minvalue=1)
        if not qty:
            return

        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET quantity = quantity + %s WHERE product_id = %s", (qty, prod_id))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã nhập kho +{qty} cho {name}\nTồn kho mới: {current_stock + qty}")
                self.load_products()
            except Error as e:
                messagebox.showerror("Lỗi", f"Không thể nhập kho: {e}")
            finally:
                cursor.close()
                conn.close()