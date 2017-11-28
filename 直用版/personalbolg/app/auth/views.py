#coding:utf-8
from flask import jsonify,render_template,redirect,request,url_for,flash,session,current_app
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetForm,PasswordResetRequestForm,ChangeEmailForm
from ..models import User
from app import db
from ..email import send_email

#登录
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            session['known'] = False
            print form.remember_me.data
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('你的账户名或者密码错误')
    return render_template('auth/login.html',form=form,known = session.get('known', False))

#模态登录
@auth.route('/logins', methods=['GET', 'POST'])
def logins():
    data = dict()
    form = LoginForm()
    email = request.form.get("email")
    password= request.form.get("password")
    remember_me = request.form.get('remember_me')
    user = User.query.filter_by(email=email).first()
    if user is not None and user.verify_password(password):
        login_user(user, remember_me)
        session['known'] = False
        data['success']='true'
        return jsonify(data)
    return jsonify(data)

#退出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经退出了')
    return redirect(url_for('main.index'))

#注册主页
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'确认你的邮箱','auth/email/confirm',user=user,token=token)
        if app.config['FLASKY_ADMIN']:
            print app.config['FLASKY_ADMIN']
            send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user,token=token)
        send_email(user.email,'确认你的邮箱','auth/email/confirm',user=user,token=token)
        flash('注册成功，请进入你的邮箱确认信息')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

#确认邮箱
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('邮箱地址已经确认，感谢！')
    else:
        flash('确认链接已经过期或')
    return redirect(url_for('main.index'))

#在请求之前
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed\
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static' :
            return redirect(url_for('auth.unconfirmed'))

#邮箱未确认时显示个人
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#确认邮箱注册
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'确认你的邮箱',
               'auth/email/confirm',user=current_user,token=token)
    return redirect(url_for('main.index'))

#改密码主页
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('你的密码已经更改了')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template('auth/change_password.html',form=form)

#重置密码请求
@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,'重置密码','auth/email/reset_password',
                       user=user,token=token,
                       next= request.args.get('next'))
        flash('已经发送了一封邮件给您，请注意查看。')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

#重置密码请求后续
@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash('你的密码已经重置')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

#改邮箱请求主页
@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_token(new_email)
            send_email(new_email,'确认你的邮箱地址','auth/email/change_email',
                       user=current_user,token=token)
            flash('邮箱已经发送至你的邮箱请注意查收！')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱或者密码错误')
    return render_template('auth/change_email.html',form=form)

#改邮箱地址主页
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('你的邮箱地址已经更改成功')
    else:
        flash('请求错误')
    return redirect(url_for('main.index'))

