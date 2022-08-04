from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configurations for using Raw SQL queries
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'us_election'

# Create Mysql object
mysql = MySQL(app)
