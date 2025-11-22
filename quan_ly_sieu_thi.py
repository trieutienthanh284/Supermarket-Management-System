# coding: utf-8

class Stakeholder():
    def __init__(self, id, name, address, phone_number):
        self.id = id
        self.name = name
        self.address = address
        self.phone_number = phone_number

    def show_information(self):
        print(f'ID: {self.id} \nTên: {self.name}\nĐịa chỉ: {self.address}\nSố điện thoại: {self.phone_number}', flush = True)

    def get_id(self):
        return self.id
    def set_name(self, new_name):
        self.name = new_name
    def get_name(self):
        return self.name
    def set_address(self, new_address):
        self.address = new_address
    def get_address(self):
        return self.address
    def set_phone_number(self, new_phone_number):
        self.phone_number = new_phone_number
    def get_phone_number(self):
        return self.phone_number

class Employee(Stakeholder):
    active_employee = 0
    total_employee = []

    def __init__(self, id, name, address, phone_number, gender, identification, title):
        self.identification = identification
        self.gender = gender
        self.title = title
        super().__init__(id, name, address, phone_number)
        self.is_active_employee = True
        if not any(emp.id == id for emp in Employee.total_employee):
            Employee.total_employee.append(self)
            Employee.active_employee += 1

    def resign(self):
        if self.is_active_employee:
            self.is_active_employee = False
            Employee.active_employee -= 1
            print(f"Nhân viên {self.name} (ID: {self.id}) đã nghỉ việc.")
        else:
            print(f"Nhân viên {self.name} đã nghỉ.")

    def show_information(self):
        super().show_information()
        print(f'Giới tính: {self.gender}')
        print(f'Số CCCD: {self.identification}')
        print(f'Chức vụ: {self.title}')
        print(f'Trạng thái: {"Đang làm việc" if self.is_active_employee else "Đã nghỉ việc"}')
        print(f'Tổng nhân viên đang làm việc: {Employee.active_employee}\n')

    def set_gender(self, new_gender):
        self.gender = new_gender
    def get_gender(self):
        return self.gender
    def set_title(self, new_title):
        self.title = new_title
    def get_title(self):
        return self.title
    def set_identification(self, new_identification):
        self.identification = new_identification
    def get_identification(self):
        return self.identification

class Customer(Stakeholder):
    count_customer = 0
    id_list = []
    def __init__(self, id, name=None, address=None, phone_number=None, shopping_point=0):
        existing_customer = None
        for cus in Customer.id_list:
            if cus.id == id:
                existing_customer = cus
                break
        if existing_customer:
            print(f"Khách hàng ID {id} đã tồn tại")
            if name: existing_customer.set_name(name)
            if address: existing_customer.set_address(address)
            if phone_number: existing_customer.set_phone_number(phone_number)
            self.__dict__ = existing_customer.__dict__
            return
        self.shopping_point = shopping_point
        super().__init__(id, name, address, phone_number)
        Customer.count_customer += 1
        Customer.id_list.append(self)
        print(f'Nhập thành công khách hàng {self.id}')
        print(f'Tổng khách hàng: {Customer.count_customer}')

    def checkout(self, amount):
        if amount > 50000:
            points = amount // 50000
            self.shopping_point += points
            print(f'Điểm tích lũy của khách hàng {self.id}: {self.shopping_point}\n')
        else :
            print('Không đủ điều kiện cộng điểm')

    def show_information(self):
        super().show_information()

class Supplier(Stakeholder):
    def __init__(self, id, name, address, phone_number, manager_contact, email, note):
        super().__init__(id, name, address, phone_number)
        self.manager_contact = manager_contact
        self.email = email
        self.note = note
        self.goods = []

    def supply(self, product):
        self.goods.append(product)

    def not_provided(self, product):
        self.goods.remove(product)

    def show_information(self):
        super().show_information()
        print(f'Thông tin người quản lý: {self.manager_contact}\nEmail: {self.email}\nGhi chú: {self.note}')
        if len(self.goods) == 0: print("Chưa có hàng hóa cung cấp\n")
        else:
            print("Sản phẩm cung cấp: ")
            for product in self.goods:
                print(f'- {product}')

    def set_manager_contact(self, new_manager_contact):
        self.manager_contact = new_manager_contact
    def get_manager_contact(self):
        return self.manager_contact
    def set_email(self, new_email):
        self.email = new_email
    def get_email(self):
        return self.email
    def set_note(self, new_note):
        self.note = new_note
    def get_note(self):
        return self.note

class Category():
    def __init__(self, id, name, description, manufacture_date, expiration_date):
        self.id = id
        self.name = name
        self.description = description
        self.manufacture_date = manufacture_date
        self.expiration_date = expiration_date
        self.product_list = []

    def append_products(self, product):
        self.product_list.append(product)

    def remove_products(self, product):
        self.product_list.remove(product)

    def total_products(self):
        return print(f'Số sản phẩm trong danh mục "{self.name}": {len(self.product_list)}')

    def get_id(self):
        return self.id
    def set_name(self, new_name):
        self.name = new_name
    def get_name(self):
        return self.name
    def set_description(self, new_description):
        self.description = new_description
    def get_description(self):
        return self.description
    def set_manufacture_date(self, new_manufacture_date):
        self.manufacture_date = new_manufacture_date
    def get_manufacture_date(self):
        return self.manufacture_date
    def set_expiration_date(self, new_expiration_date):
        self.expiration_date = new_expiration_date
    def get_expiration_date(self):
        return self.expiration_date

    def show_information(self):
        print(f'Mã danh mục: {self.id}\n Tên danh mục: {self.name}\n Mô tả: {self.description}\nNgày sản xuất: {self.manufacture_date}\nHạn sử dụng: {self.expiration_date}')
        if len(self.product_list) == 0: print("Danh mục chưa có sản phẩm\n")
        else:
            print("Sản phẩm cung cấp: ")
            for product in self.product_list:
                print(f'- {product}')

class Product():
    def __init__(self, id, name, category, cost, selling_price, stock, status, supplier):
        self.id = id
        self.name = name
        self.category = category
        self.cost = cost
        self.selling_price = selling_price
        self.stock = stock
        self.status = status
        self.supplier = supplier

    def show_information(self):
        print(f"ID: {self.id}")
        print(f"Tên: {self.name}")
        print(f"Danh mục: {self.category.name if hasattr(self.category, 'name') else self.category}")
        print(f"Giá vốn: {self.cost}")
        print(f"Giá bán: {self.selling_price}")
        print(f"Tồn kho: {self.stock}")
        print(f"Trạng thái: {self.status}")
        print(f"Nhà cung cấp: {self.supplier.name if hasattr(self.supplier, 'name') else self.supplier}")

    def update_stock(self, amount):
        self.stock += amount
        if self.stock <= 0:
            self.status = "Hết hàng"
            self.stock = 0
        else:
            self.status = "Có sẵn"

    def update_price(self, new_price):
        self.selling_price = new_price




# bên dưới là để test nhé
nv = Employee("NV001", "Thành", "Hà Nội", "09999848783", "nam", "001205034918","Nhân viên bán hàng")
kh = Customer("KH001", "Thành", "HN", "0987654321", 0)
ncc = Supplier("NCC001", "Thành", "HN", "0987654321", "Thành - 0987654321", "trieutienthanh@gmail.com", "Chưa cung cấp")
dm = Category("DM001", "Nước tăng lực", "Uống cho khỏe", "1-1-2025", "1-1-2030")

c2 = Customer("KH001", "Nguyễn Văn A", "Hà Nội", "0901234567", 5)
c3 = Customer("KH002", "Nguyễn Văn A", "Hà Nội", "0901234567", 5)
c2.checkout(400000)
