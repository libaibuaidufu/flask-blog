#coding:utf-8
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from . import login_manager
from flask import current_app,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Fenlei(db.Model):
    __tablename__='fenleis'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)

    count = db.Column(db.Integer)
    fenlei = db.relationship('Post',backref='fenlei',lazy='dynamic')

    # #给用户加角色
    # @staticmethod
    # def insert_name():
    #     names = ['python','shujuku','pacong','flask']
    #     for r in names:
    #         name = Fenlei.query.filter_by(name=r).first()
    #         print r
    #         if name is None:
    #             name = Fenlei(name=r)
    #         db.session.add(name)
    #     db.session.commit()
    #给用户加角色
    @staticmethod
    def insert_name():
        names = {'python':(True,),'数据库':(False,),'爬虫':(False,),'flask':(False,),'未分类':(False,)}
        for r in names:
            name = Fenlei.query.filter_by(name=r).first()
            if name is None:
                name = Fenlei(name=r)
            name.default = names[r][0]
            name.count = 0
            db.session.add(name)
        db.session.commit()


class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    fenlei_id = db.Column(db.Integer,db.ForeignKey('fenleis.id'))
    body_html = db.Column(db.Text)
    title = db.Column(db.String(64))
    leibie = db.Column(db.Text)
    postrejicount = db.Column(db.Integer,default=0)
    postcommentcount = db.Column(db.Integer,default=0)
    tuijian = db.Column(db.Integer,default=0)
    tuijiantime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    postcomments = db.relationship('PostComment',backref='post',lazy='dynamic')

    #渲染markdown文档
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'img','blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body,'set',Post.on_changed_body)
#用户文章评论表
class PostComment(db.Model):
    __tablename__ = 'postcomments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags= ['a','abbr','acronym','b','code','em','i','strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags=allowed_tags,strip=True))

db.event.listen(PostComment.body, 'set', PostComment.on_changed_body)
#on_changed_body 函数注册在 body 字段上，是 SQLAlchemy“set”事件的监听程序，这意
#味着只要这个类实例的 body 字段设了新值，函数就会自动被调用。
# on_changed_body 函数把 body 字段中的文本渲染成 HTML 格式，
#结果保存在 body_html 中，自动且高效地完成Markdown 文本到 HTML 的转换。

#mysql留言表
class Liuyan(db.Model):
    __tablename__='liuyans'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    liuyancoments = db.relationship('LiuyanComment',backref='liuyan',lazy='dynamic')

    #静态方法生成虚拟用户留言
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Liuyan(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                 timestamp=forgery_py.date.date(True),
                 author=u)
            db.session.add(p)
            db.session.commit()

# 关注表
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#用户留言评论表
class LiuyanComment(db.Model):
    __tablename__ = 'liuyancomments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    liuyan_id = db.Column(db.Integer,db.ForeignKey('liuyans.id'))

#角色表
class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.COMMENT|
                    Permission.FOLLOW,True),
            'Moderator':(Permission.FOLLOW |
                         Permission.COMMENT|
                         Permission.WRITE_ARTICLES|
                         Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)

#首页title
class HeadTitle(db.Model):
    __tablename__='titles'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)

#用户表
class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    liuyans = db.relationship('Liuyan',backref='author',lazy='dynamic')
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    liuyancomments = db.relationship('LiuyanComment',backref='author',lazy='dynamic')
    postcomments = db.relationship('PostComment',backref='author',lazy='dynamic')


    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    #创建虚拟用户
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(),
                    password = forgery_py.lorem_ipsum.word(),
                    confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    #密码
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    #密码散列值
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    #这个函数将原始密码作为输入，以字符串形式输出密码的散列值，输出的值可保存在用户数据库中

    #验证密码散列值
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    #这个函数的参数是从数据库中取回的密码散列值和用户输入的密码。返回值为 True 表明密码正确

    #generate_confirmation_token() 方法生成一个令牌，有效期默认为一小时
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    #confirm() 方法检验令牌，如果检验通过，则把新添加的 confirmed 属性设为 True 。
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    #重置密码的邮件过期时间
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    #重置密码
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    #更改邮箱地址的邮箱过期时间
    def generate_email_change_token(self,new_email,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id,'new_email':new_email})

    #更改邮箱地址
    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    #确认用户权限
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    #是否是管理员
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    #最后一次刷新时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    #从gravatar中获取邮箱头像
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url='https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        try:
            hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        except AttributeError:
            hash =self.avatar_hash
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
                    hash=hash,size=size,default=default,rating=rating)

    #关注
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)

    #取消关注
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    #正在关注
    def is_following(self,user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    #关注的人
    def is_followed_by(self,user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    #获取所关注用户的留言
    @property
    def followed_liuyans(self):
        return Liuyan.query.join(Follow,Follow.followed_id == Liuyan.author_id).filter(Follow.follower_id == self.id)
    #followed_posts()方法定义为属性，因此调用时无需加()

    #显示自己的留言在follow中
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


    def __repr__(self):
        return '<User {}>'.format(self.username)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户，这个函数必须返回用户对象；否则应该返回 None
