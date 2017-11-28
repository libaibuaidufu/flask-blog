#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,BooleanField,PasswordField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

#登录表单
class LoginForm(FlaskForm):
    email = StringField('邮箱',validators=[Required(),Length(1,64),
                                            Email()])
    password = PasswordField('密码',validators=[Required()])
    remember_me = BooleanField('记住我')
    # BooleanField 类表示复选框
    submit = SubmitField('登录')

#注册表单
class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    username = StringField('用户名',validators=[Required(),Length(1,64),
                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                   '用户必须使用数字和字母或者下划线')])
    password = PasswordField('密码', validators=[Required(),
                EqualTo('password2',message='密码必须一样')])
    password2 =PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('注册')

    #如果表单类中定义了以validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_eamil(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')

#忘记密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码',validators=[Required()])
    password = PasswordField('新密码',validators=[Required(),
                    EqualTo('password2',message='请确保密码一致')])
    password2 = PasswordField('确认新密码',validators=[Required()])
    submit = SubmitField('更新密码')

#密码重置请求表单
class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    submit = SubmitField('密码重置')

#密码重置表单
class PasswordResetForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    password = PasswordField('密码', validators=[Required(),
                    EqualTo('password2', message='密码必须一样')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('密码重置')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('无效邮箱地址')

#改邮箱表单
class ChangeEmailForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                         Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('更改邮箱')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')