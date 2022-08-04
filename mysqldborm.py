from flask import Flask
from flask_sqlalchemy import SQLAlchemy



class Config(object):
    pass


class ProdConfig(object):
    pass


class DevORMConfig(object):
    username = "root"
    password = "root"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://" + username + ":" + password + "@localhost:3306/us_election"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/us_election"
    DEBUG = True
