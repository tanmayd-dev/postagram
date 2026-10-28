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
    user_likes = Likes.query.filter_by(userID=current_user.id).all() if current_user.is_authenticated else []
    likes = [like.postID for like in user_likes]
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
    parent_post = Posts.query.filter_by(id=parentID).first()
    if not parent_post:
        flash("Post you are replying to does not exist.", category='error')
        return redirect(url_for('home.posts'))

    if request.method == "POST":
        text = request.form.get('text')
        disable_likes = request.form.get('disable likes')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            if disable_likes:
                post = Posts(content=text, author=current_user.id, parent=parentID, likable=False, likes=0)
            else:
                post = Posts(content=text, author=current_user.id, parent=parentID, likable=True, likes=0)
            database.session.add(post)
            database.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('home.posts'))
    return render_template('makePost.html', user=current_user, parent=parentID)

@home.route('/post/<postID>')
def post(postID):
    main_post = Posts.query.filter_by(id=postID).first()
    if not main_post:
        flash("Post does not exist.", category='error')
        return redirect(url_for('home.posts'))

    replies = Posts.query.filter_by(parent=postID).all()
    posts = [main_post] + replies
    user_likes = Likes.query.filter_by(userID=current_user.id).all() if current_user.is_authenticated else []
    likes = [like.postID for like in user_likes]
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
        Likes.query.filter_by(postID=postID).delete()
        child_replies = Posts.query.filter_by(parent=postID).all()
        for child in child_replies:
            Likes.query.filter_by(postID=child.id).delete()
            database.session.delete(child)
        database.session.delete(post)
        database.session.commit()
        flash('Post deleted.', category='success')
    return redirect(url_for('home.posts'))

@home.route('/like/<postID>')
@login_required
def like(postID):
    post = Posts.query.filter_by(id=postID).first()
    if not post:
        flash("Post does not exist.", category='error')
        return redirect(url_for('home.posts'))

    if not post.likable:
        flash("Likes are disabled for this post.", category='error')
        return redirect(request.referrer or url_for('home.posts'))

    like = Likes.query.filter_by(userID=current_user.id, postID=postID).first()
    if like:
        database.session.delete(like)
        post.likes = max(0, (post.likes or 0) - 1)
        database.session.commit()
    else:
        like = Likes(userID=current_user.id, postID=postID)
        database.session.add(like)
        post.likes = (post.likes or 0) + 1
        database.session.commit()

    return redirect(request.referrer or url_for('home.posts'))
