from . import database
from flask_login import UserMixin
from sqlalchemy import Text

class Users(database.Model, UserMixin):
    id = database.Column(database.String(150), primary_key=True)
    email = database.Column(database.String(254), unique=True)  # Max email length
    password = database.Column(database.String(255))  # For hashed passwords

class Posts(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    author = database.Column(database.String(150), database.ForeignKey('users.id'), nullable=False)
    parent = database.Column(database.Integer)
    content = database.Column(Text)  # Unlimited length for post content
    likable = database.Column(database.Boolean, default=True)
    likes = database.Column(database.Integer, default=0)

class Likes(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    userID = database.Column(database.String(150), database.ForeignKey('users.id'), nullable=False)
    postID = database.Column(database.Integer, database.ForeignKey('posts.id'), nullable=False)
