import mysql.connector
db = mysql.connector.connect(user = 'root', password = '123456789', host = 'localhost', database = 'quản lý siêu thị')
#query
code = 'create SCHEMA `Quản lý siêu thị` ;'
customer_table = 'CREATE TABLE `quản lý siêu thị`.`customer` ( `id` VARCHAR(45) NOT NULL,`name` VARCHAR(45) NOT NULL,`phone_number` VARCHAR(45) NOT NULL,`shopping_point` INT NOT NULL,PRIMARY KEY (`id`));'
#run
mycursor = db.cursor()
mycursor.execute(customer_table)
