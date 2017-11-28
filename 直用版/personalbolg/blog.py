#coding:utf-8
from flask import Flask,request,make_response,redirect,abort,render_template,url_for,session,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_wtf import FlaskForm
from flask_mail import Mail,Message
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from datetime import datetime
from threading import Thread
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

#app.config字典可用来存储框架、扩展和程序本身的配置变量。
#SECRET_KEY 配置通过密钥

#跨站请求保护 设置一个密钥。flask-wtf使用这个密钥生成加密令牌。
#在用令牌验证请求中表单数据的真伪。下面就是设置密钥
app.config['SECRET_KEY'] = 'hard to guess string'
#配置数据库链接  mysql
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:950916@localhost:3306/test?charset=utf8'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#配置邮箱
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] ='Flasky admin <13981963073@163.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

manager =Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)


#这里的stringField 就是一个字符串文本域 后面跟着的就是验证方法
#后面还会有很多类似的
#SubmitField 就是提交表单
class NameForm(FlaskForm):
    name = StringField('你的名字是？',validators=[Required()])
    submit = SubmitField('提交')

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User', backref='role',lazy='dynamic')
    def __repr__(self):
        return '<Role {}>'.format(self.name)

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User {}>'.format(self.username)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_eamil(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+' '+ subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html',**kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

#创建一个回调函数，加入shell命令时，直接把配置都加入进去，
# 就可以直接调用而不用从blog。py中导入
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@app.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    # 提交表单后，通过了validate..函数的认证validate_on_submit返回True
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username =form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN'] :
                send_eamil(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data

        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('你的名字改变了')
        # session['name'] = form.name.data
        return redirect(url_for('index'))
        #如果刷新最后一个请求是post 就会受到警告，因此使用session 请求上下文中的变量，像python字典一样。
        #redirect是一个辅助函数，用来生成HTTP重定向响应。参数url
        #urlfor就是生成url
    return render_template('app/templates/index.html', current_time= datetime.utcnow(), form=form, name=session.get('name'), known = session.get('known', False))
    # return redirect('https://www.baidu.com')

    # response = make_response('<h1>This document carries a cookie!</h1>')
    # response.set_cookie('answer','42')
    # return response

   # user_agent = request.headers.get('User-Agent')
   # return '<p>Your browser is {}</p>'.format(user_agent)

# @app.route('/user/<id>')
# def get_uesr(id):
#     user = load_user(id)
#     if not user:
#         abort(404)
#     return '<h1>Hello,{}'.format(user.name)

@app.route('/user/<name>')
def usr(name):
    return render_template('app/templates/user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('app/templates/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('app/templates/500.html'), 500


if __name__ == '__main__':
    manager.run()
