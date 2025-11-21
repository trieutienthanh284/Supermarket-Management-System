# coding: utf-8

class Stakeholder():
    def __init__(self, id, name, address, phone_number):
        self.id = id
        self.name = name
        self.address = address
        self.phone_number = phone_number

    def show_information(self):
        print(f'ID: {self.id} \nTên: {self.name}\nĐịa chỉ: {self.address}\nSố điện thoại: {self.phone_number}')

    def set_id(self, new_id):
        self.id = new_id
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

    def delete_information(self):
        pass

class Employee(Stakeholder):
    def __init__(self, id, name, address, phone_number, gender):
        self.gender = gender
        super().__init__(id, name, address, phone_number)

    def show_information(self):
        super().show_information()
        print(f'Giới tính: {self.gender}')

    def set_gender(self, new_gender):
        self.gender = new_gender
    def get_gender(self):
        return self.gender

class Customer(Stakeholder):
    def __init__(self, id, name, address, phone_number, shopping_point = 0):
        self.shopping_point = shopping_point
        super().__init__(id, name, address, phone_number)

    def checkout(self, amount):
        if amount > 50000:
            self.shopping_point += 1
            print(f'Số điểm hiện tại : {self.shopping_point}')
        else :
            print('Không đủ điều kiện cộng điểm')

    def show_information(self):
        super().show_information()
        print(f'Số điểm khách hàng: {self.shopping_point}')

class Supplier(Stakeholder):
    def __init__(self, id, name, address, phone_number, manager_contact, email, note):
        super().__init__(id, name, address, phone_number)
        self.manager_contact = manager_contact
        self.email = email
        self.note = note

    def show_information(self):
        super().show_information()
        print(f'Thông tin người quản lý: {self.manager_contact}\nEmail: {self.email}\nGhi chú: {self.note}')

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

# bên dưới là để test nhé
nv = Employee("000", "Thành", "Hà Nội", "09999848783", "nam")
nv.show_information()
