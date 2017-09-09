from flask_mail import Message
from threading import Thread
from app import mail, app
from flask import render_template
from config import ADMINS
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def follower_notification(followed, follower):
    send_email("[microblog] %s is now following you!" % follower.nickname,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt", 
                               user=followed, follower=follower),
               render_template("follower_email.html", 
                               user=followed, follower=follower))

def create_notification(user):
    send_email("You have successfully created a PremiumAir account!",
               ADMINS[0],
               [user.email],
               render_template("create_email.txt", 
                               user=user),
               render_template("create_email.html", 
                               user=user))

def username_notification(user):
    send_email("Your PremiumAir username: %s" % user.username,
               ADMINS[0],
               [user.email],
               render_template("username_email.txt", 
                               user=user),
               render_template("username_email.html", 
                               user=user))

def password_notification(user, pd):
    send_email("Your new PremiumAir password: %s" % pd,
               ADMINS[0],
               [user.email],
               render_template("password_email.txt", 
                               user=user, pd=pd),
               render_template("password_email.html", 
                               user=user, pd=pd))
