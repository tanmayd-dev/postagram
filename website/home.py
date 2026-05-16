from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, mixins
from .models import Posts, Users, Likes
from . import database

home = Blueprint("home", __name__)

@home.route("/")
def index():
    return render_template("home.html", user=current_user)

@home.route("/posts")
def posts():
    posts = Posts.query.all()
    likes = Likes.query.filter_by(userID=current_user.id).all() if current_user.is_authenticated else []
    likes = [like.postID for like in likes]
    return render_template("posts.html", posts=posts, user=current_user, likes=likes)

@home.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        disable_likes = request.form.get('disable likes')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            if disable_likes:   post = Posts(content=text, author=current_user.id, likable=False)
            else:   post = Posts(content=text, author=current_user.id, likable=True, likes=0)
            database.session.add(post)
            database.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('home.posts'))

    return render_template('makePost.html', user=current_user)

@home.route('/reply/<parentID>', methods=['GET', 'POST'])
@login_required
def reply(parentID):
    if request.method == "POST":
        text = request.form.get('text')
        disable_likes = request.form.get('disable likes')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            if disable_likes:   post = Posts(content=text, author=current_user.id, parent=parentID)
            else:   post = Posts(content=text, author=current_user.id, likes=0, parent=parentID)
            database.session.add(post)
            database.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('home.posts'))
    return render_template('makePost.html', user=current_user, parent=parentID)

@home.route('/post/<postID>')
def post(postID):
    posts = [Posts.query.filter_by(id=postID).first()]
    likes = Likes.query.filter_by(postID=postID).all()
    return render_template("posts.html", posts=posts, user=current_user, likes=likes)

@home.route('/delete/<postID>')
@login_required
def delete_post(postID):
    post = Posts.query.filter_by(id=postID).first()
    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        database.session.delete(post)
        database.session.commit()
        flash('Post deleted.', category='success')
    return redirect(url_for('home.posts'))

@home.route('/like/<postID>')
@login_required
def like(postID):
    like = Likes.query.filter_by(userID=current_user.id, postID=postID).first()
    if like:
        database.session.delete(like)
        Posts.query.filter_by(id=postID).first().likes = Posts.query.filter_by(id=postID).first().likes - 1
        database.session.commit()
    else:
        like = Likes(userID=current_user.id, postID=postID)
        database.session.add(like)
        Posts.query.filter_by(id=postID).first().likes = Posts.query.filter_by(id=postID).first().likes + 1
        database.session.commit()

    return redirect(url_for('home.posts'))
