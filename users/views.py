# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request
from datetime import datetime
from app import db, requires_roles
from users.forms import RegisterForm, LoginForm
from flask import session, Markup
from models import User
from flask_login import login_user, logout_user, login_required, current_user
import pyotp, bcrypt, logging
# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]',form.email.data, request.remote_addr)
        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()


    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()

        if not user\
            or not bcrypt.checkpw(form.password.data.encode('utf-8'), user.password)\
            or not pyotp.TOTP(user.pinkey).verify(form.pin.data):

            logging.warning('SECURITY - Invaild Login Attempt [%s,%s]', form.username.data, request.remote_addr)

            if session.get('authentication_attempts') >= 3:
                flash(Markup('Number of incorrect login attempts exceeded.Please click <a href="/reset">here</a> to reset.'))
                return render_template('users/login.html')

            flash('Please check your login details and try again'
                  '{} login attempts remaining '.format(3 - session.get('authentication_attempts')))

            session['authentication_attempts'] += 1

            return render_template('users/login.html', form=form)

        else:
            login_user(user)
            user.last_login = user.current_login
            user.current_login = datetime.now()

            db.session.add(user)
            db.session.commit()

            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id,current_user.email,request.remote_addr)
            if current_user.role == 'admin':
                return render_template('admin/admin.html')
            else:
                return render_template('users/profile.html', form=form)
    return render_template('users/login.html', form=form)


@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))

@users_blueprint.route('/logout')
#there has to be an account logged in to be able to log out
@login_required
def logout():
    logging.warning('SECURITY - Logout [%s, %s, %s]',current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))


# view user profile
@users_blueprint.route('/profile')
@login_required
#the view profile page can only be viewed when only user account is logged in
@requires_roles('user')
def profile():
    return render_template('users/profile.html', name="PLACEHOLDER FOR FIRSTNAME")


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")


