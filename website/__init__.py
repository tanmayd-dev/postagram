from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import mysql.connector

database = SQLAlchemy()
connector = mysql.connector.connect(host='localhost', user='root', password='root')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "asdf"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/postagram'
    database.init_app(app)

    from .home import home
    app.register_blueprint(home, url_prefix="/")

    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")

    from .models import Users, Posts

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(username):
        return Users.query.get(username)

    return app

def create_database(app):
    cursor = connector.cursor()
    cursor.execute('show databases')
    if 'postagram' not in [i[0] for i in cursor]:
        cursor.execute('create database postagram')
        with app.app_context():
            database.create_all()

