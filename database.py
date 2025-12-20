import mysql.connector
from mysql.connector import Error

try:
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456789',
        database='quản lý siêu thị',
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )

    mycursor = db.cursor()

    tables_to_drop = ['bill_item', 'bill', 'product', 'customer', 'employee', 'supplier', 'category']
    for table in tables_to_drop:
        mycursor.execute(f"DROP TABLE IF EXISTS {table};")

    # 1. Category
    mycursor.execute("""
        CREATE TABLE category (
            category_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            is_active TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 2. Supplier
    mycursor.execute("""
        CREATE TABLE supplier (
            supplier_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            hotline VARCHAR(20),
            manager VARCHAR(100),
            address TEXT
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 3. Customer
    mycursor.execute("""
        CREATE TABLE customer (
            customer_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(20) NOT NULL UNIQUE,
            shopping_point INT DEFAULT 0 CHECK (shopping_point >= 0),
            INDEX idx_phone (phone_number)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 4. Employee
    mycursor.execute("""
        CREATE TABLE employee (
            employee_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(20),
            birthday DATE,
            gender ENUM('Nam', 'Nữ', 'Khác'),
            identification VARCHAR(20) UNIQUE,
            title VARCHAR(100),
            is_working TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 5. Product
    mycursor.execute("""
        CREATE TABLE product (
            product_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            price DECIMAL(15,2) NOT NULL CHECK (price >= 0),
            description TEXT,
            quantity INT NOT NULL CHECK (quantity >= 0),
            category_id VARCHAR(10),
            supplier_id VARCHAR(10),
            is_active TINYINT(1) DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL,
            FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE SET NULL
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 6. Bill
    mycursor.execute("""
        CREATE TABLE bill (
            bill_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id VARCHAR(10),
            employee_id VARCHAR(10) NOT NULL,
            total_amount DECIMAL(15,2) DEFAULT 0,
            applied_point INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE SET NULL,
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE RESTRICT
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    # 7. Bill_item
    mycursor.execute("""
        CREATE TABLE bill_item (
            bill_item_id INT AUTO_INCREMENT PRIMARY KEY,
            bill_id INT NOT NULL,
            product_id VARCHAR(10) NOT NULL,
            quantity INT NOT NULL CHECK (quantity > 0),
            price DECIMAL(15,2) NOT NULL CHECK (price >= 0),
            FOREIGN KEY (bill_id) REFERENCES bill(bill_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE RESTRICT
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)

    db.commit()

    # 1. Category (DM001 - DM020)
    category_raw = [
        ('Thực phẩm khô', 'Gạo, mì gói, bột, gia vị, đồ hộp'),
        ('Thực phẩm tươi', 'Rau củ quả, thịt cá tươi sống'),
        ('Đồ uống không cồn', 'Nước ngọt, nước suối, sữa, trà đóng chai'),
        ('Bia và rượu', 'Bia hơi, bia lon, rượu vang, rượu mạnh'),
        ('Sữa và chế phẩm từ sữa', 'Sữa tươi, sữa chua, phô mai, váng sữa'),
        ('Bánh kẹo các loại', 'Bánh quy, kẹo, chocolate, snack'),
        ('Hóa mỹ phẩm', 'Dầu gội, xà phòng, kem đánh răng, mỹ phẩm'),
        ('Chăm sóc cá nhân', 'Băng vệ sinh, tã giấy, khăn giấy ướt'),
        ('Đồ gia dụng', 'Nồi niêu xoong chảo, chén dĩa, dao kéo'),
        ('Đồ điện gia dụng', 'Quạt máy, máy xay sinh tố, nồi cơm điện'),
        ('Văn phòng phẩm', 'Bút viết, sổ tay, giấy in, tập vở'),
        ('Đồ chơi trẻ em', 'Lego, búp bê, xe đồ chơi, xếp hình'),
        ('Mẹ và bé', 'Sữa bột, bình sữa, tã bỉm trẻ em'),
        ('Thực phẩm đông lạnh', 'Kem, há cảo, chả giò, xúc xích đông lạnh'),
        ('Đồ ăn vặt', 'Bim bim, mực khô, trái cây sấy'),
        ('Dầu ăn & gia vị', 'Dầu olive, nước mắm, tương ớt, hạt nêm'),
        ('Cà phê & trà', 'Cà phê hòa tan, cà phê gói, trà túi lọc'),
        ('Sản phẩm hữu cơ', 'Rau sạch, thực phẩm organic'),
        ('Vệ sinh nhà cửa', 'Nước lau sàn, nước rửa chén, túi đựng rác'),
        ('Hàng tiêu dùng khác', 'Pin, bóng đèn, vật dụng linh tinh'),
    ]
    category_data = [(f"DM{i:03d}", name, desc) for i, (name, desc) in enumerate(category_raw, 1)]
    mycursor.executemany("INSERT IGNORE INTO category (category_id, name, description) VALUES (%s, %s, %s)", category_data)
    db.commit()

    # 2. Supplier (NCC001 - NCC020)
    supplier_raw = [
        ('Công ty CP Sữa Việt Nam (Vinamilk)', '1800-156-158', 'Nguyễn Văn A', 'TP.HCM'),
        ('Coca-Cola Việt Nam', '1800-888-999', 'Trần Thị B', 'Hà Nội'),
        ('Unilever Việt Nam', '1900-555-888', 'Lê Văn C', 'TP.HCM'),
        ('Acecook Việt Nam', '1800-678-999', 'Phạm Thị D', 'Bình Dương'),
        ('Masan Consumer', '1900-636-888', 'Vũ Văn E', 'TP.HCM'),
        ('Mondelez Kinh Đô', '1800-123-456', 'Đặng Thị F', 'Bình Dương'),
        ('P&G Việt Nam', '1900-555-777', 'Bùi Văn G', 'Hà Nội'),
        ('TH True Milk', '1800-999-888', 'Hoàng Thị H', 'Nghệ An'),
        ('Sabeco (Bia Sài Gòn)', '1800-777-999', 'Ngô Văn I', 'TP.HCM'),
        ('Heineken Việt Nam', '1900-888-777', 'Đỗ Thị K', 'TP.HCM'),
        ('Nestlé Việt Nam', '1800-666-888', 'Lý Văn L', 'Đồng Nai'),
        ('PepsiCo Việt Nam', '1900-444-777', 'Hà Thị M', 'TP.HCM'),
        ('Orion Food Vina', '1800-555-666', 'Mai Văn N', 'Bắc Ninh'),
        ('Bibica', '1900-333-888', 'Trương Thị O', 'TP.HCM'),
        ('Lavie (Nestlé Waters)', '1800-222-999', 'Phan Văn P', 'Hưng Yên'),
        ('Tân Hiệp Phát', '1900-111-888', 'Huỳnh Thị Q', 'Bình Dương'),
        ('Vissan', '1800-999-777', 'Võ Văn R', 'TP.HCM'),
        ('CP Việt Nam', '1900-888-666', 'Dương Thị S', 'Đồng Nai'),
        ('Bảo Việt (Bảo hiểm)', '1800-777-888', 'Lâm Văn T', 'Hà Nội'),
        ('Nhật Bản - Rohto Mentholatum', '1900-555-999', 'Tô Thị U', 'TP.HCM'),
    ]
    supplier_data = [(f"NCC{i:03d}", *item) for i, item in enumerate(supplier_raw, 1)]
    mycursor.executemany("INSERT IGNORE INTO supplier (supplier_id, name, hotline, manager, address) VALUES (%s, %s, %s, %s, %s)", supplier_data)
    db.commit()

    # 3. Employee (NV001 - NV020)
    employee_raw = [
        ('Nguyễn Văn An', '0911111111', '1990-01-15', 'Nam', '123456789', 'Quản lý'),
        ('Trần Thị Bình', '0912222222', '1992-05-20', 'Nữ', '987654321', 'Thu ngân'),
        ('Lê Văn Cường', '0913333333', '1995-08-10', 'Nam', '111222333', 'Nhân viên kho'),
        ('Phạm Thị Dung', '0914444444', '1998-12-25', 'Nữ', '444555666', 'Thu ngân'),
        ('Vũ Văn Em', '0915555555', '1993-03-30', 'Nam', '777888999', 'Bảo vệ'),
        ('Đặng Thị Lan', '0916666666', '1996-07-18', 'Nữ', '000111222', 'Nhân viên bán hàng'),
        ('Bùi Văn Giang', '0917777777', '1991-11-05', 'Nam', '333444555', 'Nhân viên kho'),
        ('Hoàng Thị Hà', '0918888888', '1997-04-12', 'Nữ', '666777888', 'Thu ngân'),
        ('Ngô Văn Hùng', '0919999999', '1994-09-22', 'Nam', '999000111', 'Nhân viên bán hàng'),
        ('Đỗ Thị Ngọc', '0920000000', '1999-02-28', 'Nữ', '222333444', 'Thu ngân'),
        ('Lý Văn Khánh', '0921111111', '1990-06-15', 'Nam', '555666777', 'Phó quản lý'),
        ('Hà Thị Linh', '0922222222', '1995-10-08', 'Nữ', '888999000', 'Nhân viên bán hàng'),
        ('Mai Văn Minh', '0923333333', '1992-01-20', 'Nam', '123123123', 'Nhân viên kho'),
        ('Trương Thị Na', '0924444444', '1998-05-14', 'Nữ', '456456456', 'Thu ngân'),
        ('Phan Văn Quân', '0925555555', '1993-08-30', 'Nam', '789789789', 'Bảo vệ'),
        ('Huỳnh Thị Oanh', '0926666666', '1996-12-01', 'Nữ', '101101101', 'Nhân viên bán hàng'),
        ('Võ Văn Phú', '0927777777', '1991-03-17', 'Nam', '202202202', 'Nhân viên kho'),
        ('Dương Thị Quyên', '0928888888', '1997-07-25', 'Nữ', '303303303', 'Thu ngân'),
        ('Lâm Văn Sang', '0929999999', '1994-11-11', 'Nam', '404404404', 'Nhân viên bán hàng'),
        ('Tô Thị Thảo', '0930000000', '1999-09-09', 'Nữ', '505505505', 'Thu ngân'),
    ]
    employee_data = [(f"NV{i:03d}", *item) for i, item in enumerate(employee_raw, 1)]
    mycursor.executemany("""
        INSERT IGNORE INTO employee 
        (employee_id, name, phone_number, birthday, gender, identification, title, is_working)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
    """, employee_data)
    db.commit()

    # 4. Customer (KH001 - KH030)
    customer_raw = [
        ('Nguyễn Văn Tèo', '0901001001', 350), ('Trần Thị Tý', '0902002002', 120),
        ('Lê Hoàng Long', '0903003003', 0), ('Phạm Thị Mai', '0904004004', 680),
        ('Vũ Văn Hưng', '0905005005', 210), ('Đặng Thị Lan', '0906006006', 450),
        ('Bùi Văn Khôi', '0907007007', 90), ('Hoàng Thị Ngọc', '0908008008', 920),
        ('Ngô Văn Minh', '0909009009', 300), ('Đỗ Thị Thu', '0910001000', 550),
        ('Lý Văn Quang', '0911001100', 150), ('Hà Thị Kim', '0912001200', 780),
        ('Mai Văn Đức', '0913001300', 420), ('Trương Thị Bé', '0914001400', 180),
        ('Phan Văn Long', '0915001500', 610), ('Huỳnh Thị Linh', '0916001600', 290),
        ('Võ Văn Tài', '0917001700', 75), ('Dương Thị Thảo', '0918001800', 510),
        ('Lâm Văn Bảo', '0919001900', 330), ('Tô Thị Ánh', '0920002000', 850),
        ('Hồ Văn Nam', '0921002100', 220), ('Cao Thị Hương', '0922002200', 640),
        ('Đinh Văn Phong', '0923002300', 100), ('Trịnh Thị Vân', '0924002400', 470),
        ('Bạch Văn Sơn', '0925002500', 380), ('Lương Thị Hồng', '0926002600', 710),
        ('Quách Văn Thịnh', '0927002700', 160), ('Kiều Thị Nga', '0928002800', 590),
        ('Từ Văn Lộc', '0929002900', 270), ('Nghiêm Thị Yến', '0930003000', 820),
    ]
    customer_data = [(f"KH{i:03d}", name, phone, point) for i, (name, phone, point) in enumerate(customer_raw, 1)]
    mycursor.executemany("INSERT IGNORE INTO customer (customer_id, name, phone_number, shopping_point) VALUES (%s, %s, %s, %s)", customer_data)
    db.commit()

    # 5. Product (SP001 - SP050)
    product_raw = [
        ('Gạo ST25 5kg', 150000, 'Gạo ngon nhất thế giới', 50, 1, 1),
        ('Mì Hảo Hảo tôm chua cay', 4500, 'Mì ăn liền vị tôm chua cay', 200, 1, 4),
        ('Coca Cola 1.5L', 18000, 'Nước ngọt có gas', 150, 3, 2),
        ('Sữa tươi Vinamilk 1L', 32000, 'Sữa tươi không đường', 80, 5, 1),
        ('Bia Sài Gòn Special 330ml', 15000, 'Bia nội địa', 120, 4, 9),
        ('Oreo kem vani', 25000, 'Bánh quy kem vani', 100, 6, 6),
        ('Dầu gội Head & Shoulders 650ml', 145000, 'Dầu gội trị gàu', 60, 7, 7),
        ('Tã Bobby size M 50 miếng', 280000, 'Tã em bé', 40, 8, 3),
        ('Nồi cơm điện Cuckoo 1.8L', 2500000, 'Nồi cơm cao tần', 20, 10, 12),
        ('Quạt cây Senko TC1626', 850000, 'Quạt đứng cao cấp', 30, 10, 18),
        ('Bút bi Thiên Long', 5000, 'Bút bi xanh', 300, 11, None),
        ('Lego Classic 790 miếng', 1200000, 'Bộ xếp hình cơ bản', 25, 12, None),
        ('Sữa bột Enfamil A+ 900g', 850000, 'Sữa cho bé 0-6 tháng', 35, 13, 11),
        ('Kem Wall\'s hộp 500ml', 55000, 'Kem vani cao cấp', 70, 14, 11),
        ('Bim bim Lay\'s vị phô mai', 15000, 'Snack khoai tây', 180, 15, 12),
        ('Dầu ăn Simply 5L', 185000, 'Dầu ăn thực vật', 45, 16, 3),
        ('Cà phê Trung Nguyên G7 3in1', 85000, 'Hộp 20 gói', 90, 17, None),
        ('Rau cải xanh hữu cơ 500g', 25000, 'Rau sạch không thuốc', 60, 18, None),
        ('Nước lau sàn Sunlight 1L', 45000, 'Hương hoa thiên nhiên', 80, 19, 3),
        ('Pin AA Duracell vỉ 4 viên', 45000, 'Pin kiềm cao cấp', 100, 20, None),
        ('Thịt heo ba rọi 1kg', 165000, 'Thịt tươi', 30, 2, 17),
        ('Cá hồi phi lê 500g', 280000, 'Cá hồi nhập khẩu', 25, 2, None),
        ('Trà Cozy đào túi lọc', 35000, 'Hộp 25 túi', 100, 3, 16),
        ('Rượu vang đỏ Đà Lạt', 150000, 'Chai 750ml', 40, 4, None),
        ('Phô mai Con Bò Cười', 15000, 'Lát 200g', 120, 5, 1),
        ('Socola KitKat', 20000, 'Thanh 4 ngón', 150, 6, 6),
        ('Kem đánh răng Colgate', 35000, 'Tuýp 180g', 100, 7, 7),
        ('Khăn giấy ướt Bobby', 28000, 'Gói 80 miếng', 80, 8, 3),
        ('Chảo chống dính Lock&Lock 28cm', 450000, 'Chảo cao cấp', 35, 9, None),
        ('Máy xay sinh tố Philips', 1200000, 'Công suất 600W', 20, 10, None),
        ('Sổ tay A5', 25000, '100 trang', 200, 11, None),
        ('Búp bê Barbie', 550000, 'Bộ thời trang', 30, 12, None),
        ('Bình sữa Pigeon 240ml', 220000, 'Cho bé', 50, 13, None),
        ('Xúc xích CP', 45000, 'Gói 500g đông lạnh', 70, 14, 18),
        ('Mực khô loại 1', 850000, 'Kg', 15, 15, None),
        ('Nước mắm Phú Quốc 40 độ', 95000, 'Chai 500ml', 60, 16, None),
        ('Cà phê Highlands nguyên chất', 180000, 'Gói 500g', 40, 17, None),
        ('Cà rốt hữu cơ', 20000, 'Kg', 80, 18, None),
        ('Nước rửa chén Sunlight chanh', 55000, 'Túi 3.6kg', 70, 19, 3),
        ('Bóng đèn LED Philips 10W', 65000, 'Bóng tròn', 100, 20, None),
        ('Táo Gala Mỹ', 65000, 'Kg', 40, 2, None),
        ('Sữa chua Vinamilk có đường', 8000, 'Hộp 100g', 200, 5, 1),
        ('Bánh ChocoPie', 55000, 'Hộp 12 cái', 90, 6, 6),
        ('Dầu gội X-Men', 95000, 'Chai 650g', 70, 7, 3),
        ('Tã Goo.N size L', 320000, 'Gói 54 miếng', 30, 8, None),
        ('Dao bếp Zwilling', 850000, 'Dao thái cao cấp', 15, 9, None),
        ('Ấm siêu tốc Sunhouse', 450000, '1.8L', 40, 10, None),
        ('Giấy A4 Double A', 85000, 'Ream 500 tờ', 100, 11, None),
        ('Xe đồ chơi điều khiển', 750000, 'Xe địa hình', 20, 12, None),
        ('Sữa bột Abbott Grow 900g', 780000, 'Cho bé 3 tuổi', 25, 13, 11),
    ]
    product_data = []
    for i, (name, price, desc, qty, cat_index, sup_index) in enumerate(product_raw, 1):
        prod_id = f"SP{i:03d}"
        cat_id = f"DM{cat_index:03d}" if cat_index else None
        sup_id = f"NCC{sup_index:03d}" if sup_index else None
        product_data.append((prod_id, name, price, desc, qty, cat_id, sup_id))

    mycursor.executemany("""
        INSERT IGNORE INTO product (product_id, name, price, description, quantity, category_id, supplier_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, product_data)
    db.commit()

except Error as e:
    print(f"Lỗi MySQL: {e}")
    if 'db' in locals() and db.is_connected():
        db.rollback()

finally:
    if 'db' in locals() and db.is_connected():
        mycursor.close()
        db.close()