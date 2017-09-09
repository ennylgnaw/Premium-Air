from flask import render_template, flash, redirect, request, session, url_for, get_flashed_messages
from app import app, db, models
from functools import wraps

def general_authenticate(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect('index')
        if session['username'] == 'username':
            user = models.User.query.filter_by(username = session['username']).first()
            if not user:
                flash("Authentication did not check out")
                return redirect('index')

        return func(*args, **kwargs)

    return check_user

def authenticate_usr_without_flash():
    if not 'username' in session:
        return False
    if session['username'] == 'username':
        user = models.User.query.filter_by(username = session['username']).first()
        if not user:
            return False

    return True

def administrator_authenticate(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not 'username' in session:
            flash("You are not logged in")
            return redirect('index')
        user = models.User.query.filter_by(username = session['username']).first()
        if not user:
            flash("Authentication did not check out")
            return redirect('index')
        if not user.admin:
            flash("You must be an administrator to view this page")
            return redirect('index')
        return func(*args, **kwargs)
    return check_user
