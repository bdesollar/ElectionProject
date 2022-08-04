from mysqldb import mysql
from models import database
import pymysql
import cryptography

def create_tables():
    
    cursor = mysql.connection.cursor()
    
    statements = ["CREATE TABLE IF NOT EXISTS admin(id int NOT NULL PRIMARY KEY AUTO_INCREMENT, first_name VARCHAR(30),"
                  " last_name VARCHAR(30), user_id VARCHAR(30) NOT NULL, password varchar(255) NOT NULL, "
                  "email varchar(100) NOT NULL)",

                  "CREATE TABLE IF NOT EXISTS voter(id int NOT NULL PRIMARY KEY AUTO_INCREMENT, first_name VARCHAR(30),"
                  " last_name VARCHAR(30), user_id VARCHAR(30) NOT NULL, password varchar(255) NOT NULL, "
                  "email varchar(100) NOT NULL)",

                  "CREATE TABLE IF NOT EXISTS poll_manager(id int NOT NULL PRIMARY KEY AUTO_INCREMENT, "
                  "first_name VARCHAR(30), last_name VARCHAR(30), user_id VARCHAR(30) NOT NULL, "
                  "password varchar(255) NOT NULL, email varchar(100) NOT NULL)",
                  ]

    for statement in statements:
        cursor.execute(statement)
        mysql.connection.commit()
        cursor.close()


if __name__ == '__main__':
    database.create_all()
