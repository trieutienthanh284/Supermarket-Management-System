class Employee():
    def __init__(self, employee_id, name, phone_number,birthday, gender, identification, title):
        self.employee_id = employee_id
        self.name = name
        self.phone_number = phone_number
        self.identification = identification
        self.gender = gender
        self.title = title
        self.birthday = birthday
        self.is_working = True

    def resign(self):
        self.is_working = False

    def is_active(self):
        return self.is_working

class Customer():
    def __init__(self, customer_id, name, phone_number):
        self.customer_id = customer_id
        self.name = name
        self.phone_number = phone_number
        self.shopping_point = 0

    def add_point(self, point):
        if not isinstance(point, int):
            raise TypeError("Point must be an integer")
        self.shopping_point += point

    def use_point(self, point):
        if not isinstance(point, int):
            raise TypeError("Point must be an integer")
        if point > self.shopping_point:
            raise ValueError("Point is more than the shopping point")
        self.shopping_point -= point

class Supplier():
    def __init__(self, supplier_id, name, hotline, manager, address):
        self.supplier_id = supplier_id
        self.name = name
        self.hotline = hotline
        self.manager = manager
        self.address = address

class Product():
    def __init__(self, product_id, name, price, description, quantity, category_id, supplier_id):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.quantity = quantity
        self.category_id = category_id
        self.supplier_id = supplier_id
        self.is_active = True

    def increase_stock(self, amount):
        if amount <= 0:
            raise ValueError("Amount cannot be zero")
        self.quantity += amount

    def decrease_stock(self, amount):
        if amount <= 0:
            raise ValueError("Amount cannot be zero")
        if amount > self.quantity:
            raise ValueError("Amount exceeds the stock quantity")
        self.quantity -= amount

    def is_out_of_stock(self):
        return self.quantity == 0

    def enable(self):
        self.is_active = True

    def disable(self):
        self.is_active = False

class Category():
    def __init__(self, category_id, name, description = ""):
        self.category_id = category_id
        self.name = name
        self.description = description
        self.is_active = True

    def enable(self):
        self.is_active = True

    def disable(self):
        self.is_active = False

class BillItem():
    def __init__(self, product_id, quantity, price):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price must be non-negative")

        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def calculate_subtotal(self):
        return self.quantity * self.price

class Bill():
    def __init__(self, bill_id, customer_id, employee_id):
        self.bill_id = bill_id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.items = []
        self.total_amount = 0
        self.applied_point = 0

    def add_item(self, product_id, quantity, price):
        item = BillItem(product_id, quantity, price)
        self.items.append(item)
        self.calculate_amount()

    def remove_item(self, product_id):
        self.items = [
            item for item in self.items
            if item.product_id != product_id
        ]
        self.calculate_amount()

    def calculate_amount(self):
        self.total_amount = sum(
            item.quantity * item.price
            for item in self.items
        )
        return self.total_amount

    def apply_point(self, used_point):
        if used_point <= 0:
            raise ValueError("Point is not valuable")
        self.applied_point = used_point
        self.total_amount -= used_point







