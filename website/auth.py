from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import database
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(id=username).first()
        if not user:    user = Users.query.filter_by(email=username).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('home.posts'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_exists = Users.query.filter_by(email=email).first()
        username_exists = Users.query.filter_by(id=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = Users(email=email, id=username, password=generate_password_hash(password1))
            database.session.add(new_user)
            database.session.commit()
            flash('User created!')
            return redirect(url_for('home.posts'))

    return render_template("signup.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.index"))
