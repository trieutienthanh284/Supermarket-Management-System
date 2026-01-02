# Hệ thống quản lý siêu thị mini

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)

Dự án **Hệ thống quản lý siêu thị mini** được xây dựng bằng Python, sử dụng giao diện Tkinter và cơ sở dữ liệu MySQL. Hệ thống phù hợp với các cửa hàng bán lẻ quy mô nhỏ (siêu thị tiện lợi, minimart kiểu WinMart+, Bách Hóa Xanh, Circle K...).

## Tính năng chính

- **Bán hàng nhanh chóng**:
  - Tìm kiếm sản phẩm theo tên
  - Thêm vào giỏ hàng (double-click)
  - Áp dụng điểm tích lũy giảm giá
  - Thanh toán, tự động trừ kho, tích điểm mới
  - In hóa đơn chi tiết ngay sau thanh toán

- **Quản lý sản phẩm**:
  - Thêm / sửa / ngừng bán sản phẩm
  - Nhập kho (tăng tồn kho)
  - Hiển thị danh mục và nhà cung cấp

- **Quản lý khách hàng**:
  - Tìm kiếm theo SĐT/tên
  - Tạo khách mới ngay khi bán hàng
  - Chỉnh điểm tích lũy thủ công

- **Quản lý nhân viên**:
  - Phân quyền rõ ràng: Quản lý / Phó quản lý / Thu ngân
  - Thêm / sửa / cho nghỉ việc nhân viên

- **Báo cáo doanh thu**:
  - Doanh thu hôm nay
  - Top sản phẩm bán chạy
  - Cảnh báo sản phẩm sắp hết hàng
  - Biểu đồ doanh thu 7 ngày gần nhất (matplotlib)

## Công nghệ sử dụng

- **Ngôn ngữ**: Python 3.11+
- **Giao diện**: Tkinter (GUI native)
- **Cơ sở dữ liệu**: MySQL
- **Thư viện**:
  - mysql-connector-python
  - matplotlib (biểu đồ báo cáo)

## Cấu trúc thư mục
ProjectOOP/
├── main.py
├── models.py
├── services.py
├── interface/
│   ├── main_dashboard.py
│   ├── login_dashboard.py
│   ├── tab_for_sales.py
│   ├── tab_for_product.py
│   ├── tab_for_customer.py
│   ├── tab_for_employee.py
│   └── tab_for_report.py
├── database.sql
├── README.md
└── .gitignore



