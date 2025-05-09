from flask import Blueprint, render_template, request, redirect, url_for
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from ... import db

views = Blueprint("views", __name__)

# Define a blacklist of words for usernames and post descriptions
USERNAME_BLACKLIST = ["admin", "root", "sysadmin", "moderator", "support", "fuck", "shit", "cunt", "pussy", "bitch", "nigger", "nigga", "retard", "dick", "penis", "vagina", "clitorous", "blackguy"]
DESCRIPTION_BLACKLIST = ["spam", "advertisement", "fake", "scam", "fuck", "shit", "cunt", "pussy", "bitch", "nigger", "nigga", "retard", "dick", "penis", "vagina", "clitorous", "blackguy"]

def is_username_blacklisted(username):
    return any(blacklisted_word in username.lower() for blacklisted_word in USERNAME_BLACKLIST)

def is_description_blacklisted(description):
    return any(blacklisted_word in description.lower() for blacklisted_word in DESCRIPTION_BLACKLIST)

@views.route('/')
@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                print('Logged in')
                return redirect(url_for('views.posts'))
            else:
                print('Wrong password')
        else:
            print('Username does not exist')
    return render_template("login.html")

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        username_exists = Users.query.filter_by(username=username).first()
        email_exists = Users.query.filter_by(email=email).first()
        if is_username_blacklisted(username):
            print('Username contains a blacklisted word')
        elif password1 != password2:
            print('Passwords don\'t match')
        elif username_exists or email_exists:
            print('User already exists')
        elif len(password1) < 6 or len(username) < 6:
            print('Length of username or password is too short')
        else:
            new_user = Users(username=username, email=email, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('views.posts'))
    return render_template("register.html")