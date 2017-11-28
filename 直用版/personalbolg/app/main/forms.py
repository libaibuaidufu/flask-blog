#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,IntegerField,BooleanField,SelectField
from wtforms.validators import Required,Length,EqualTo,Email,Regexp
from wtforms import ValidationError
from ..models import Role,User,Fenlei
from flask_pagedown.fields import PageDownField

#以前的name表单
class NameForm(FlaskForm):
    name = StringField('你的名字是？',validators=[Required()])
    submit = SubmitField('提交')

#编辑个人资料表单
class EditProfileForm(FlaskForm):
    name = StringField('你的真实名字',validators=[Length(1,64)])
    location =StringField('地址',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('提交')

#编辑管理员资料表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    username = StringField('用户名', validators=[Required(), Length(1, 64),
                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                            '用户必须使用数字和字母或者下划线')])
    confirmed = BooleanField('确认')
    role = SelectField('权限',coerce=int)
    name = StringField('你的真实名字', validators=[Length(1, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('提交')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name)
                           for role in Role.query.order_by(Role.name).all()]
        self.user = user


    def validate_eamil(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self,field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')

#首页标题
class HeadtitleForm(FlaskForm):
    title = StringField("标题",validators=[Required()])
    body = TextAreaField('内容',validators=[Required()])
    submit = SubmitField("发送")

#留言板表单
class LiuyanForm(FlaskForm):
    body = TextAreaField('留言板',validators=[Required()])
    submit = SubmitField('发送')

class FenleiForm(FlaskForm):
    count = IntegerField('计数',validators=[Required()])

#文章编辑表单
class PostForm(FlaskForm):
    leibie = SelectField('分类2')
    #fenlei = SelectField('分类',coerce=int)
    title = StringField('标题',validators=[Required()])
    body = PageDownField('文章编辑',validators=[Required()])
    sumbit = SubmitField('发表')


    def __init__(self,*args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.leibie.choices = [('weifenlei','未分类'),('python','python'),('shujuku','数据库'),('flask','flask'),('pacong','爬虫')]
        #self.fenlei.choices = [(fenlei.name, fenlei.name) for fenlei in Fenlei.query.order_by(Fenlei.name).all()]

#留言评论输入表
class LiuyanCommentForm(FlaskForm):
    body = StringField('',validators=[Required()])
    submit = SubmitField('评论')

#文章评论输入表
class PostCommentForm(FlaskForm):
    body = StringField('',validators=[Required()])
    submit = SubmitField('评论')