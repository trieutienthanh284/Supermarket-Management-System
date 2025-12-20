#Base Service connect database (lớp cha)
import mysql.connector
from mysql.connector import Error

class BaseService:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='quản lý siêu thị',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
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

