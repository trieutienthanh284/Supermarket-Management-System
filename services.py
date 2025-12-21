#Base Service connect database (lớp cha)
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

class BaseService:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='quản lý siêu thị',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=True
        )

    def get_cursor(self):
        return self.connection.cursor(dictionary=True)  # dictionary=True để trả về dict dễ map sang object

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()

#Product service
from models import Product, Category, Supplier

class ProductService(BaseService):
    def get_all_products(self, active_only=True):
        cursor = self.get_cursor()
        query = "SELECT * FROM product"
        if active_only:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [Product(
            product_id=row['product_id'],
            name=row['name'],
            price=row['price'],
            description=row['description'],
            quantity=row['quantity'],
            category_id=row['category_id'],
            supplier_id=row['supplier_id']
        ) for row in rows]

    def get_product_by_id(self, product_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Product(**row)
        return None

    def search_products(self, keyword):
        cursor = self.get_cursor()
        cursor.execute("""
            SELECT * FROM product 
            WHERE name LIKE %s OR description LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = cursor.fetchall()
        cursor.close()
        return [Product(**row) for row in rows]

    def decrease_stock(self, product_id, amount):
        cursor = self.get_cursor()
        cursor.execute("""
            UPDATE product 
            SET quantity = quantity - %s 
            WHERE product_id = %s AND quantity >= %s
        """, (amount, product_id, amount))
        affected = cursor.rowcount
        self.commit()
        cursor.close()
        return affected > 0  # True nếu trừ kho thành công

#Quản lý khách hàng
from models import Customer

class CustomerService(BaseService):
    def get_customer_by_phone(self, phone_number):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM customer WHERE phone_number = %s", (phone_number,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Customer(row['customer_id'], row['name'], row['phone_number'])
        return None

    def create_customer(self, name, phone_number):
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO customer (name, phone_number) 
                VALUES (%s, %s)
            """, (name, phone_number))
            self.commit()
            customer_id = cursor.lastrowid
            cursor.close()
            return Customer(customer_id, name, phone_number)
        except Error:
            self.rollback()
            cursor.close()
            return None

    def add_points(self, customer_id, points):
        cursor = self.get_cursor()
        cursor.execute("""
            UPDATE customer 
            SET shopping_point = shopping_point + %s 
            WHERE customer_id = %s
        """, (points, customer_id))
        self.commit()
        cursor.close()

    def use_points(self, customer_id, points):
        cursor = self.get_cursor()
        cursor.execute("""
            UPDATE customer 
            SET shopping_point = GREATEST(shopping_point - %s, 0)
            WHERE customer_id = %s AND shopping_point >= %s
        """, (points, customer_id, points))
        success = cursor.rowcount > 0
        self.commit()
        cursor.close()
        return success

#Nghiệp vụ bán hàng
from models import Bill, BillItem
from datetime import datetime

class BillService(BaseService):
    def create_bill(self, customer_id=None, employee_id=1):  # employee_id mặc định 1 để test
        cursor = self.get_cursor()
        cursor.execute("""
            INSERT INTO bill (customer_id, employee_id) 
            VALUES (%s, %s)
        """, (customer_id, employee_id))
        bill_id = cursor.lastrowid
        self.commit()
        cursor.close()
        return Bill(bill_id, customer_id, employee_id)

    def add_item_to_bill(self, bill_id, product_id, quantity):
        product_service = ProductService()
        product = product_service.get_product_by_id(product_id)
        if not product or product.quantity < quantity:
            return False

        cursor = self.get_cursor()
        cursor.execute("""
            INSERT INTO bill_item (bill_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (bill_id, product_id, quantity, product.price))

        # Cập nhật tổng tiền bill
        cursor.execute("""
            UPDATE bill 
            SET total_amount = (
                SELECT SUM(quantity * price) FROM bill_item WHERE bill_id = %s
            )
            WHERE bill_id = %s
        """, (bill_id, bill_id))

        # Trừ kho
        if product_service.decrease_stock(product_id, quantity):
            self.commit()
            cursor.close()
            return True
        self.rollback()
        cursor.close()
        return False

    def apply_points(self, bill_id, used_points, customer_id):
        customer_service = CustomerService()
        if customer_service.use_points(customer_id, used_points):
            cursor = self.get_cursor()
            cursor.execute("""
                UPDATE bill 
                SET applied_point = %s,
                    total_amount = total_amount - %s
                WHERE bill_id = %s
            """, (used_points, used_points, bill_id))
            self.commit()
            cursor.close()
            return True
        return False

    def complete_bill(self, bill_id, customer_id=None, points_earned=0):
        if customer_id and points_earned > 0:
            CustomerService().add_points(customer_id, points_earned)
        return True

class CategoryService(BaseService):
    def get_all_categories(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM category WHERE is_active = 1")
        rows = cursor.fetchall()
        cursor.close()
        return rows

class SupplierService(BaseService):
    def get_all_suppliers(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM supplier")
        rows = cursor.fetchall()
        cursor.close()
        return rows

#Report service
class ReportService(BaseService):
    def __init__(self):
        super().__init__()

    # 1. Doanh thu theo ngày
    def get_revenue_by_date_range(self, start_date, end_date):
        """
        start_date, end_date: định dạng 'YYYY-MM-DD'
        Trả về tổng doanh thu thực thu (sau khi trừ điểm)
        """
        cursor = self.get_cursor()
        cursor.execute("""
            SELECT 
                DATE(created_at) AS sale_date,
                SUM(total_amount) AS revenue
            FROM bill 
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY sale_date
            ORDER BY sale_date
        """, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # 2. Doanh thu ngày hiện tại
    def get_today_revenue(self):
        cursor = self.get_cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS today_revenue
            FROM bill 
            WHERE DATE(created_at) = CURDATE()
        """)
        row = cursor.fetchone()
        cursor.close()
        return row['today_revenue'] or 0

    # 3. Top sản phẩm bán chạy
    def get_top_selling_products(self, limit=10, by_revenue=True):
        cursor = self.get_cursor()
        order_by = "SUM(bi.quantity * bi.price)" if by_revenue else "SUM(bi.quantity)"
        cursor.execute(f"""
            SELECT 
                p.name,
                p.price,
                SUM(bi.quantity) AS total_quantity,
                SUM(bi.quantity * bi.price) AS total_revenue
            FROM bill_item bi
            JOIN product p ON bi.product_id = p.product_id
            JOIN bill b ON bi.bill_id = b.bill_id
            GROUP BY p.product_id, p.name, p.price
            ORDER BY {order_by} DESC
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # 4. Sản phẩm sắp hết hàng
    def get_low_stock_products(self, threshold=20):
        cursor = self.get_cursor()
        if not cursor:
            return []
        try:
            cursor.execute("""
                SELECT product_id, name, price, description, quantity, 
                       category_id, supplier_id, is_active
                FROM product
                WHERE is_active = 1 AND quantity <= %s
                ORDER BY quantity ASC
            """, (threshold,))
            rows = cursor.fetchall()
            return [Product(**row) for row in rows]
        except Error as e:
            print(f"[ReportService] Lỗi get_low_stock_products: {e}")
            return []
        finally:
            cursor.close()

    # 5. Thống kê theo danh mục
    def get_revenue_by_category(self, start_date=None, end_date=None):
        cursor = self.get_cursor()
        query = """
            SELECT 
                c.name AS category_name,
                COALESCE(SUM(bi.quantity * bi.price), 0) AS category_revenue
            FROM category c
            LEFT JOIN product p ON c.category_id = p.category_id
            LEFT JOIN bill_item bi ON p.product_id = bi.product_id
            LEFT JOIN bill b ON bi.bill_id = b.bill_id
        """
        params = []
        if start_date and end_date:
            query += " WHERE DATE(b.created_at) BETWEEN %s AND %s"
            params = [start_date, end_date]
        query += " GROUP BY c.category_id, c.name ORDER BY category_revenue DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # 6. Tổng số hóa đơn và khách hàng trong ngày
    def get_daily_summary(self):
        cursor = self.get_cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_bills,
                COUNT(DISTINCT customer_id) AS unique_customers,
                COALESCE(SUM(total_amount), 0) AS total_revenue,
                COALESCE(SUM(applied_point), 0) AS total_points_used
            FROM bill 
            WHERE DATE(created_at) = CURDATE()
        """)
        row = cursor.fetchone()
        cursor.close()
        return row

    # 7. Tổng hợp
    def print_all_reports(self):
        print("=" * 60)
        print("                BÁO CÁO TỔNG HỢP SIÊU THỊ")
        print("=" * 60)

        # 1. Doanh thu hôm nay
        today_revenue = self.get_today_revenue()
        print(f"DOANH THU HÔM NAY ({datetime.now().strftime('%d/%m/%Y')}):")
        print(f"   {today_revenue:,.0f} VND\n")

        # 2. Tóm tắt hoạt động hôm nay
        summary = self.get_daily_summary()
        print("TỔNG KẾT HOẠT ĐỘNG HÔM NAY:")
        print(f"   Số hóa đơn: {summary['total_bills']}")
        print(f"   Số khách hàng khác nhau: {summary['unique_customers']}")
        print(f"   Tổng điểm khách dùng giảm giá: {summary['total_points_used']:,} điểm\n")

        # 3. Top 10 sản phẩm bán chạy
        print("TOP 10 SẢN PHẨM BÁN CHẠY NHẤT (theo doanh thu):")
        top_products = self.get_top_selling_products(limit=10, by_revenue=True)
        if top_products:
            print(f"{'STT':<4} {'Tên sản phẩm':<40} {'SL':<6} {'Doanh thu':<15}")
            print("-" * 70)
            for i, p in enumerate(top_products, 1):
                print(f"{i:<4} {p['name']:<40} {p['total_quantity']:<6} {p['total_revenue']:,.0f} VND")
        else:
            print("   Chưa có dữ liệu bán hàng")
        print()

        # 4. Sản phẩm sắp hết hàng
        print("CẢNH BÁO TỒN KHO THẤP (≤ 20 cái):")
        low_stock = self.get_low_stock_products(threshold=20)
        if low_stock:
            print(f"{'Tên sản phẩm':<40} {'Còn lại':<8} {'Giá':<12}")
            print("-" * 65)
            for p in low_stock:
                print(f"{p.name:<40} {p.quantity:<8} {p.price:,.0f} VND")
        else:
            print("   Tất cả sản phẩm đều còn đủ hàng!")
        print()

        # 5. Doanh thu theo danh mục (7 ngày gần nhất)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        print(f"DOANH THU THEO DANH MỤC (từ {start_date} đến {end_date}):")
        cat_revenue = self.get_revenue_by_category(start_date, end_date)
        if cat_revenue:
            total_cat = sum(item['category_revenue'] for item in cat_revenue)
            print(f"{'Danh mục':<30} {'Doanh thu':<15} {'Tỷ lệ':<8}")
            print("-" * 60)
            for c in cat_revenue:
                ratio = (c['category_revenue'] / total_cat * 100) if total_cat > 0 else 0
                print(f"{c['category_name']:<30} {c['category_revenue']:,.0f} VND {ratio:>6.1f}%")
        else:
            print("Chưa có dữ liệu bán hàng trong tuần")
        print()