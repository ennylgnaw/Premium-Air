from flask import render_template, flash, redirect, session, url_for, request, g
from .forms import CreateForm, LoginForm, EditForm, PostForm, SearchForm, EditPostForm, ForgotUsernameForm, ForgotPasswordForm
from .models import User, Post
from authenticate import *
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from .emails import follower_notification, create_notification, username_notification, password_notification
import math
import random
import string

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/<int:page>', methods=['GET', 'POST'])
def login(page=1):
    user = None
    login_form = LoginForm()
    form = PostForm()
    if user == None:
        posts = models.Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
        
    if login_form.validate_on_submit():
        session['username'] = login_form.username.data
        if models.User.query.filter_by(username = login_form.username.data).first().admin:
            session['admin'] = 'true'
        else:
            session['admin'] = 'false'
        flash('Logged in')

        return redirect('/index')

    return render_template("login.html", title = "Login", login_form = login_form, posts=posts)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    user = None
    form = PostForm()
    search_form = SearchForm()
    if (authenticate_usr_without_flash()):
        user = models.User.query.filter_by(username = session['username']).first()
        user.last_seen = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        search_form = SearchForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    if user:
        if session['admin']=='true':
            posts = models.Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
        else:
            posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    if user == None:
        flash("You must log in!!!")
        return redirect(url_for('login'))
    return render_template('index.html',
                           title='Home',
                           user=user,
                           form=form,
                           search_form=search_form,
                           posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    create_form = CreateForm()
    
    if create_form.validate_on_submit():
        session['username'] = create_form.username.data
        new_user = models.User(username = create_form.username.data,
                                     fname = create_form.fname.data,
                                     lname = create_form.lname.data,
                                     email = create_form.email.data,
                                     nickname = create_form.nickname.data,
                                     admin = False,
                                     password_length = len(create_form.password.data))
        new_user.set_password(create_form.password.data)
        db.session.add(new_user)
        db.session.commit()
        db.session.add(new_user.follow(new_user))
        db.session.commit()
        session['admin'] = 'false'
        flash('Welcome %s!' % (create_form.fname.data))
        create_notification(new_user)
        return redirect('/index')
    
    return render_template('create.html', 
                           title='Create Account',
                           create_form=create_form)

@app.route('/logout', methods=['GET'])
@general_authenticate
def logout():
    session.pop('username', None)
    
    flash('You have been logged out')
    
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@general_authenticate
def user(nickname, page=1):
    user = models.User.query.filter_by(username = session['username']).first()
    fuser = User.query.filter_by(nickname=nickname).first()
    search_form = SearchForm()
    if fuser == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = fuser.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    return render_template('user.html',
                           fuser=fuser,
                           user=user,
                           search_form=search_form,
                           posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@general_authenticate
def edit():
    search_form = SearchForm()
    user = models.User.query.filter_by(username = session['username']).first()
    form = EditForm(user.nickname)
    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = user.nickname
        form.about_me.data = user.about_me
    return render_template('edit.html', form=form, user=user, search_form=search_form)

@app.route('/post/<id>')
@general_authenticate
def post_page(id):
    user = models.User.query.filter_by(username = session['username']).first()
    post = Post.query.filter_by(id=id).first()
    search_form = SearchForm()
    if post == None:
        flash('Post %s not found.' % id)
        return redirect(url_for('index'))

    return render_template('post_page.html',
                           user=user,
                           search_form=search_form,
                           post=post)

@app.route('/edit_post/<id>', methods=['GET', 'POST'])
@general_authenticate
def edit_post(id):
    search_form = SearchForm()
    user = models.User.query.filter_by(username = session['username']).first()
    post = Post.query.filter_by(id=id).first()
    form = EditPostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    else:
        form.body.data = post.body
    return render_template('edit_post.html', form=form, user=user, search_form=search_form, post=post)

@app.route('/delete_user/<nickname>', methods=['GET', 'POST'])
@general_authenticate
@administrator_authenticate
def delete_user(nickname):
    user = models.User.query.filter_by(nickname=nickname).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user_list', nickname=nickname))

@app.route('/delete_post/<id>', methods=['GET', 'POST'])
@general_authenticate
@administrator_authenticate
def delete_post(id):
    post = models.Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index', id=id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/follow/<nickname>')
@general_authenticate
def follow(nickname):
    user = models.User.query.filter_by(username = session['username']).first()
    fuser = User.query.filter_by(nickname=nickname).first()
    if fuser is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if fuser == user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = user.follow(fuser)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    follower_notification(fuser, user)
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@general_authenticate
def unfollow(nickname):
    user = models.User.query.filter_by(username = session['username']).first()
    fuser = User.query.filter_by(nickname=nickname).first()
    if fuser is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if fuser == user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = user.unfollow(fuser)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

@app.route('/search', methods=['POST'])
@general_authenticate
def search():
    search_form = SearchForm()
    if not search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=search_form.search.data, search_form=search_form))

@app.route('/search_results/<query>')
@general_authenticate
def search_results(query):
    search_form = SearchForm()
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results,
                           search_form=search_form)

@app.route('/user_list', methods=['GET'])
@general_authenticate
def user_list():
    user = models.User.query.filter_by(username = session['username']).first()
    search_form = SearchForm()
    users = models.User.query.order_by(models.User.nickname).all()
    return render_template('user_list.html',
                           search_form=search_form,
                           users = users,
                           user=user
                           )

@app.route('/switch', methods=['GET'])
@general_authenticate
@administrator_authenticate
def switch():
    if session['admin']=='true':
        session['admin']='false'
    else:
        session['admin']='true'
    return redirect(url_for('index'))

@app.route('/statistics', methods=['GET'])
@administrator_authenticate
def statistics():
    user = models.User.query.filter_by(username = session['username']).first()
    search_form = SearchForm()
    users = models.User.query.all()
    posts = models.Post.query.all()

    num_users = 0
    num_posts = 0

    for u in users:
        num_users += 1

    for p in posts:
        num_posts += 1

    return render_template('statistics.html', user = user, search_form = search_form, num_users = num_users, num_posts = num_posts)

@app.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    form = ForgotUsernameForm()
    user = models.User.query.filter_by(email = form.email.data).first()
    if form.validate_on_submit():
        flash('Your username has been emailed to you.')
        username_notification(user)
        return redirect('/login')
        
    return render_template('forgot_username.html',
                           form=form,
                           user=user
                           )

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    user = models.User.query.filter_by(email = form.email.data).first()
    pd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    if form.validate_on_submit():
        password_notification(user, pd)
        user.set_password(pd)
        db.session.add(user)
        db.session.commit()
        flash('Your new password has been emailed to you.')
        
        return redirect('/login')
        
    return render_template('forgot_password.html',
                           form=form,
                           user=user,
                           pd=pd
                           )
