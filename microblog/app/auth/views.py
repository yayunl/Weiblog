from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_babel import _
# microblog imports
from .. import db
from ..models import User
from ..api.errors import error_response
# sub feature imports
from .forms import LoginForm, RegistrationForm, ResetPasswordConfirmationForm, ResetPasswordRequestForm
from .email import send_password_reset_email
from . import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        # The user is none or illegal
        if not user or not user.check_password(form.password.data):
            flash("Invalid username or password!")
            return redirect(url_for('auth.login'))

        # Login authentication passed
        login_user(user, remember=form.remember_me.data)

        # Redirect the user back to the original page before logon
        next_page = request.args.get('next')
        #
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('core.index')

        flash("Login successfully!")
        return redirect(next_page)

    return render_template('auth/login.html', title=_('Sign in'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = RegistrationForm()

    # Validate if the form is filled
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(password=form.password.data)

        # save to db
        db.session.add(user)
        db.session.commit()
        flash('Congrats!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',
                           title='Sign up',
                           form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = ResetPasswordRequestForm()

    # Post method
    if form.validate_on_submit():
        # verify the user
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send a password reset link to the user's email address.
            send_password_reset_email(user)
        flash("Check your email for instructions to reset your password.")
        # Back to login page
        return redirect(url_for('auth.login'))

    # Get method
    return render_template('auth/reset_password_request.html',
                           title='Reset password',
                           form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_confirmation(token):
    # Reset the password
    user = User.verify_reset_password_token(token)

    if current_user.is_authenticated or not user:
        return redirect(url_for('core.index'))

    form = ResetPasswordConfirmationForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your new password has been saved.")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_confirmation.html',
                           form=form)
