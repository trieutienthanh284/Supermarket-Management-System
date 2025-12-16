class Employee():
    def __init__(self, employee_id, name, phone_number,birthday, gender, identification, title):
        self.identification = identification
        self.gender = gender
        self.title = title
        self.birthday = birthday
        super().__init__(id, name, phone_number)
        self.is_working = True

    def resign(self):
        self.is_working = False

    def is_active(self):
        return self.is_working

class Customer():
    def __init__(self, customer_id, name, phone_number):
        super().__init__(id, name, phone_number)
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

class Product():
    def __init__(self, product_id, name, price, description, quantity, category_id):
        self.id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.quantity = quantity
        self.category_id = category_id
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
        if self.quantity == 0:
            print("Product is out of stock")

    def enable(self):
        self.is_active = True

    def disable(self):
        self.is_active = False

class Category():
    def __init__(self, category_id, name, description = ""):
        self.id = category_id
        self.name = name
        self.description = description
        self.is_active = True

    def enable(self):
        self.is_active = True

    def disable(self):
        self.is_active = False

class Bill():
    def __init__(self, bill_id, customer_id, employee_id):
        self.id = bill_id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.items = []
        self.total_amount = 0
        self.applied_point = 0

    def add_item(self, product_id, quantity, price):
        if quantity <= 0:
            raise ValueError("Quantity cannot be zero")
        self.items.append(Product({'Product_id': product_id,
                                   'Quantity': quantity,
                                   'Price': price})

    def remove_item(self, product_id):






