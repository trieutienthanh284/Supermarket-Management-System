import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import ProductService, CustomerService, BillService
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class SaleTab(ttk.Frame):
    def __init__(self, parent, employee):
        super().__init__(parent)
        self.employee = employee
        self.current_customer = None
        self.cart = []

        self.product_service = ProductService()
        self.customer_service = CustomerService()
        self.bill_service = BillService()

        self.create_widgets()

    def create_widgets(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tìm khách hàng
        customer_frame = tk.LabelFrame(left_frame, text="THÔNG TIN KHÁCH HÀNG", font=("Arial", 12, "bold"))
        customer_frame.pack(fill="x", pady=10)

        tk.Label(customer_frame, text="Số điện thoại:", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        self.entry_phone = tk.Entry(customer_frame, font=("Arial", 12), width=20)
        self.entry_phone.pack(side="left", padx=5, pady=10)
        tk.Button(customer_frame, text="Tìm khách", font=("Arial", 10), bg="#3498db", fg="white",
                  command=self.search_customer).pack(side="left", padx=10, pady=10)

        self.lbl_customer = tk.Label(customer_frame, text="Khách vãng lai", font=("Arial", 12, "bold"), fg="#27ae60")
        self.lbl_customer.pack(side="left", padx=20, pady=10)

        # Giỏ hàng
        cart_frame = tk.LabelFrame(left_frame, text="GIỎ HÀNG", font=("Arial", 12, "bold"))
        cart_frame.pack(fill="both", expand=True, pady=10)

        columns = ("STT", "Tên sản phẩm", "SL", "Giá", "Thành tiền")
        self.tree_cart = ttk.Treeview(cart_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_cart.heading(col, text=col)
            self.tree_cart.column(col, width=120, anchor="center")
        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=10)

        # Tổng tiền
        self.lbl_total = tk.Label(left_frame, text="TỔNG TIỀN: 0 VND", font=("Arial", 18, "bold"), fg="red")
        self.lbl_total.pack(pady=10)

        # Nút thanh toán & hủy
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="THANH TOÁN", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", width=15, height=4,
                  command=self.checkout).pack(side="left", padx=20)
        tk.Button(btn_frame, text="HỦY GIỎ", font=("Arial", 12), bg="#e74c3c", fg="white", width=12, height=4,
                  command=self.clear_cart).pack(side="left", padx=20)

        right_frame = tk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        search_frame = tk.LabelFrame(right_frame, text="TÌM SẢN PHẨM", font=("Arial", 12, "bold"))
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Tên sản phẩm:", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.entry_search.pack(side="left", padx=5, pady=10)
        tk.Button(search_frame, text="Tìm", font=("Arial", 10), bg="#3498db", fg="white",
                  command=self.search_products).pack(side="left", padx=10, pady=10)
        tk.Button(search_frame, text="Tất cả", font=("Arial", 10),
                  command=self.load_all_products).pack(side="left", padx=10, pady=10)

        # Danh sách sản phẩm
        prod_frame = tk.LabelFrame(right_frame, text="DANH SÁCH SẢN PHẨM", font=("Arial", 12, "bold"))
        prod_frame.pack(fill="both", expand=True)

        columns_prod = ("ID", "Tên sản phẩm", "Giá", "Tồn kho")
        self.tree_products = ttk.Treeview(prod_frame, columns=columns_prod, show="headings", height=20)
        for col in columns_prod:
            self.tree_products.heading(col, text=col)
            self.tree_products.column(col, width=180, anchor="center")
        self.tree_products.pack(fill="both", expand=True, padx=10, pady=10)

        # Double click để thêm vào giỏ
        self.tree_products.bind("<Double-1>", self.add_to_cart)

        # Load sản phẩm ban đầu
        self.load_all_products()

    def load_all_products(self):
        products = self.product_service.get_all_products()
        self.update_product_tree(products)

    def search_products(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_all_products()
            return
        products = self.product_service.search_products(keyword)
        self.update_product_tree(products)

    def update_product_tree(self, products):
        # Xóa cũ
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)
        # Thêm mới
        for p in products:
            self.tree_products.insert("", "end", values=(
                p.product_id,
                p.name,
                f"{p.price:,.0f}",
                p.quantity
            ))

    def search_customer(self):
        phone = self.entry_phone.get().strip()
        if not phone:
            self.current_customer = None
            self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")
            return

        # Tìm khách cũ
        customer = self.customer_service.get_customer_by_phone(phone)
        if customer:
            self.current_customer = customer
            points = getattr(customer, 'shopping_point', 0)  # Lấy điểm từ object
            self.lbl_customer.config(text=f"{customer.name} - Điểm: {points}", fg="#27ae60")
            return

        # Nếu không tìm thấy → hỏi tạo mới
        if messagebox.askyesno("Khách mới", f"Không tìm thấy khách với SĐT {phone}.\nBạn muốn tạo khách hàng mới không?"):
            name = simpledialog.askstring("Tên khách", "Nhập tên khách hàng:", initialvalue="Khách lẻ")
            if name and name.strip():
                new_customer = self.customer_service.create_customer(name.strip(), phone)
                if new_customer:
                    self.current_customer = new_customer
                    self.lbl_customer.config(text=f"{new_customer.name} - Điểm: 0", fg="#27ae60")
                    messagebox.showinfo("Thành công", f"Đã tạo khách mới: {new_customer.name}\nSĐT: {phone}")
                else:
                    messagebox.showerror("Lỗi", "Không thể tạo khách mới! (SĐT có thể đã tồn tại)")
            else:
                messagebox.showinfo("Hủy", "Không tạo khách mới.")
                self.current_customer = None
                self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")
        else:
            self.current_customer = None
            self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")

    def load_all_products(self):
        products = self.product_service.get_all_products()
        self.update_product_tree(products)

    def search_products(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_all_products()
            return
        products = self.product_service.search_products(keyword)
        self.update_product_tree(products)

    def update_product_tree(self, products):
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)
        for p in products:
            self.tree_products.insert("", "end", values=(p.product_id, p.name, f"{p.price:,.0f}", p.quantity))

    def add_to_cart(self, event):
        selected = self.tree_products.selection()
        if not selected:
            return
        item = self.tree_products.item(selected[0])
        product_id = item['values'][0]
        product = self.product_service.get_product_by_id(product_id)
        if not product:
            messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm!")
            return
        if product.quantity <= 0:
            messagebox.showwarning("Hết hàng", f"Sản phẩm {product.name} đã hết hàng!")
            return

        qty = simpledialog.askinteger("Số lượng", f"Nhập số lượng (tồn kho: {product.quantity}):",
                                      minvalue=1, maxvalue=product.quantity)
        if qty:
            # Kiểm tra đã có trong giỏ chưa
            for item in self.cart:
                if item['product'].product_id == product.product_id:
                    item['quantity'] += qty
                    break
            else:
                self.cart.append({'product': product, 'quantity': qty})
            self.refresh_cart()

    def refresh_cart(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)
        total = 0
        for i, item in enumerate(self.cart, 1):
            p = item['product']
            qty = item['quantity']
            subtotal = qty * p.price
            total += subtotal
            self.tree_cart.insert("", "end", values=(i, p.name, qty, f"{p.price:,.0f}", f"{subtotal:,.0f}"))
        self.lbl_total.config(text=f"TỔNG TIỀN: {total:,.0f} VND")

    def clear_cart(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy giỏ hàng?"):
            self.cart = []
            self.refresh_cart()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Giỏ trống", "Chưa có sản phẩm nào trong giỏ!")
            return

        total = sum(item['quantity'] * item['product'].price for item in self.cart)

        used_points = 0
        if self.current_customer:
            current_points = getattr(self.current_customer, 'shopping_point', 0)
            if current_points > 0:
                max_use = min(current_points, total)
                use = messagebox.askyesno("Dùng điểm", f"Khách có {current_points:,} điểm. Dùng để giảm giá? (tối đa {max_use:,}đ)")
                if use:
                    used_points = simpledialog.askinteger("Dùng điểm", f"Nhập số điểm dùng (tối đa {max_use:,}):",
                                                          minvalue=0, maxvalue=max_use)
                    used_points = used_points or 0

        final_total = total - used_points

        if not messagebox.askyesno("Xác nhận thanh toán",
                                   f"Tổng tiền: {total:,.0f} VND\n"
                                   f"Dùng điểm: {used_points:,} điểm\n"
                                   f"Thành tiền: {final_total:,.0f} VND\n\n"
                                   f"Xác nhận thanh toán?"):
            return

        # Tạo bill
        bill = self.bill_service.create_bill(
            customer_id=getattr(self.current_customer, 'customer_id', None),
            employee_id=self.employee['employee_id']
        )

        success = True
        for item in self.cart:
            if not self.bill_service.add_item_to_bill(bill.bill_id, item['product'].product_id, item['quantity']):
                success = False
                break

        if used_points > 0 and self.current_customer:
            self.bill_service.apply_points(bill.bill_id, used_points, self.current_customer.customer_id)

        if success:
            points_earned = final_total // 100000
            self.bill_service.complete_bill(bill.bill_id, getattr(self.current_customer, 'customer_id', None),
                                            points_earned)

            messagebox.showinfo("THÀNH CÔNG!",
                                f"Thanh toán thành công!\n"
                                f"Thành tiền: {final_total:,.0f} VND\n"
                                f"Tích điểm mới: +{points_earned} điểm")

            self.print_bill(bill.bill_id, self.cart, total, used_points, final_total, points_earned)

            self.clear_cart()
            self.search_customer()
            self.load_all_products()

    def print_bill(self, bill_id, cart_items, total, used_points, final_total, points_earned):
        # Popup hóa đơn
        bill_window = tk.Toplevel(self)
        bill_window.title(f"HÓA ĐƠN THANH TOÁN - MÃ {bill_id}")
        bill_window.geometry("800x700")
        bill_window.configure(bg="white")

        # Header hóa đơn
        header = tk.Frame(bill_window, bg="white")
        header.pack(pady=20)

        tk.Label(header, text="SIÊU THỊ ABC GROUP", font=("Arial", 24, "bold"), bg="white", fg="#2c3e50").pack()
        tk.Label(header, text="Địa chỉ: 120 An Liễng", font=("Arial", 12), bg="white").pack()
        tk.Label(header, text="Hotline: 1936 363 636", font=("Arial", 12), bg="white").pack()
        tk.Label(header, text=f"Mã hóa đơn: HD{bill_id:06d}", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        tk.Label(header, text=f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", font=("Arial", 12), bg="white").pack()
        tk.Label(header, text=f"Nhân viên: {self.employee['name']}", font=("Arial", 12), bg="white").pack()

        if self.current_customer:
            tk.Label(header, text=f"Khách hàng: {self.current_customer.name} - SĐT: {self.current_customer.phone_number}",
                     font=("Arial", 12), bg="white").pack(pady=5)

        # Bảng sản phẩm
        table_frame = tk.Frame(bill_window, bg="white")
        table_frame.pack(fill="both", expand=True, padx=50, pady=20)

        columns = ("STT", "Tên sản phẩm", "SL", "Giá", "Thành tiền")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=len(cart_items))
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)

        for i, item in enumerate(cart_items, 1):
            p = item['product']
            qty = item['quantity']
            subtotal = qty * p.price
            tree.insert("", "end", values=(i, p.name, qty, f"{p.price:,.0f}", f"{subtotal:,.0f}"))

        # Tổng kết
        footer = tk.Frame(bill_window, bg="white")
        footer.pack(pady=30)

        tk.Label(footer, text=f"TỔNG TIỀN:", font=("Arial", 16, "bold"), bg="white").pack(anchor="e")
        tk.Label(footer, text=f"{total:,.0f} VND", font=("Arial", 16, "bold"), bg="white", fg="blue").pack(anchor="e")

        if used_points > 0:
            tk.Label(footer, text=f"Giảm điểm tích lũy:", font=("Arial", 14), bg="white").pack(anchor="e")
            tk.Label(footer, text=f"- {used_points:,} điểm", font=("Arial", 14), bg="white", fg="green").pack(anchor="e")

        tk.Label(footer, text=f"THÀNH TIỀN:", font=("Arial", 18, "bold"), bg="white").pack(anchor="e")
        tk.Label(footer, text=f"{final_total:,.0f} VND", font=("Arial", 18, "bold"), bg="white", fg="red").pack(anchor="e")

        if points_earned > 0:
            tk.Label(footer, text=f"Tích điểm mới: +{points_earned} điểm", font=("Arial", 14, "bold"), bg="white", fg="#27ae60").pack(pady=10)

        tk.Label(footer, text="CẢM ƠN QUÝ KHÁCH ĐÃ MUA HÀNG!", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=20)
        tk.Label(footer, text="Hẹn gặp lại quý khách!", font=("Arial", 12), bg="white").pack()

        # Nút in
        tk.Button(bill_window, text="IN HÓA ĐƠN", font=("Arial", 14, "bold"), bg="#3498db", fg="white", width=20, height=2,
                  command=lambda: messagebox.showinfo("In", "Đã gửi lệnh in hóa đơn! (chức năng in thật sẽ thêm sau)")).pack(pady=20)