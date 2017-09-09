from app import app, models
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, IntegerField, SelectField, RadioField, SubmitField, SelectMultipleField, HiddenField, DateTimeField, widgets, DecimalField, TextField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Email, Required, InputRequired, Optional
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed, FileRequired
from flask import flash, session


class CreateForm(Form):
    fname = StringField('fname', validators=[DataRequired()])
    lname = StringField('lname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    nickname = StringField('nickname', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired(), Length(min = 4, max = 25)]) # add a unique check
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('password2', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    submit = SubmitField()

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        usere = models.User.query.filter_by(email=self.email.data).first()
        if usere != None:
            self.email.errors.append('This email is already in use. Please choose another one.')
            return False
        usern = models.User.query.filter_by(nickname=self.nickname.data).first()
        if usern != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        useru = models.User.query.filter_by(username=self.username.data).first()
        if useru != None:
            self.username.errors.append('This username is already in use. Please choose another one.')
            return False
        return True

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Length(min = 4, max = 25)])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField()

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        user_to_check = models.User.query.filter_by(username = self.username.data).first()
        if not user_to_check:
            self.username.errors.append("No user with this username exists")
            return False
        if (user_to_check and not user_to_check.check_password(self.password.data)):
            self.password.errors.append("Authentication failed")
            return False

        return True

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = models.User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class EditPostForm(Form):
    body = TextAreaField('body', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False

        return True

class PostForm(Form):
    post = TextAreaField('post', validators=[DataRequired()])

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])

class ForgotUsernameForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        usere = models.User.query.filter_by(email=self.email.data).first()
        if usere == None:
            self.email.errors.append('No such email exists in our database.')
            return False
        return True

class ForgotPasswordForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        usere = models.User.query.filter_by(email=self.email.data).first()
        if usere == None:
            self.email.errors.append('No such email exists in our database.')
            return False
        return True
