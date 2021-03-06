from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, current_app
from weibo import APIClient, APIError
import urllib, re

from . import auth
from ..models import User, BindMode
from .forms import LoginForm, RegistrationForm, ChangingPasswordForm, \
    ResetPasswordRequestForm, ResetPasswordForm, ChangeEmailForm
from .. import db
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


def get_code(full_path):
    # get param code by getting full path and using RE
    if 'code' in full_path:
        full_path = urllib.unquote(full_path)
        m = re.match('.*\?code=([\w\d]+).*', full_path)
        if m is not None:
            code = m.group(1)
            return code
    print 'Invalid param - code'
    return None


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(password=form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    param_next = request.args.get('next')
    return render_template('auth/login.html', form=form, param_next=param_next)


@auth.route('/login/weibo_auth', methods=['GET'])
def weibo_auth():
    app_key = current_app.config['APP_KEY']
    app_secret = current_app.config['APP_SECRET']
    callback_url = current_app.config['CALLBACK_URL']
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback_url)
    url = client.get_authorize_url()
    return redirect(url)


@auth.route('/login/weibo_login', methods=['GET'])
def weibo_login():
    app_key = current_app.config['APP_KEY']
    app_secret = current_app.config['APP_SECRET']
    callback_url = current_app.config['CALLBACK_URL']
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback_url)
    code = request.args.get('code')
    try:
        r = client.request_access_token(code)
    except APIError:
        flash('Invalid weibo code. Please Try again.')
        return redirect(request.args.get('next') or url_for('auth.login'))
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)
    uid = r.get('uid')
    if uid is None:
        flash('Not found uid of weibo')
        return redirect(request.args.get('next') or url_for('auth.login'))
    screen_name = client.statuses.user_timeline.get().get('statuses')[0].get('user').get('screen_name')
    user = User.query.filter_by(weibo_uid=uid).first()
    if user is None:
        user = User(weibo_uid=uid, username=screen_name, confirmed=True)
        user.upgrade_bind_mode()
        db.session.add(user)
        db.session.commit()
    login_user(user)  # the second argument is 'remember me'
    return redirect(request.args.get('next') or url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        user.upgrade_bind_mode()
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confiration email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/changing_password', methods=['GET', 'POST'])
@login_required
def changing_password():
    form = ChangingPasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been changed successfully.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/changing_password.html", form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_reset_password_token()
        send_email(user.email, 'Reset Your Password',
                   'auth/email/reset_password', user=user, token=token,
                   next=request.args.get('next'))
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been reset.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.new_email.data
            token = current_user.generate_changing_email_request(new_email)
            send_email(new_email, 'Change your email address',
                       'auth/email/change_email', user=current_user, token=token)
            flash('An confrimation email has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been changed.')
    else:
        flash('Invalid request')
    return redirect(url_for('main.index'))
