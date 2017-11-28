#coding:utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #配置密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #配置默认数据库链接数据
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #配置邮箱
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[随风潜入夜]'
    FLASKY_MAIL_SENDER = 'DFK admin <13981963073@163.com>'
    FLASKY_ADMIN = os.environ.get('DFK_ADMIN')
    FLASKY_LIUYANS_PER_PAGE = 20
    FLASKY_POSTS_PER_PAGE = 8
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    UPLOAD_FOLDER = r'C:\Users\dfk\PycharmProjects\personalbolg\app\static\img'
    UPLOAD_FOLDER_POSTS = r'C:\Users\dfk\PycharmProjects\personalbolg\app\static\posts'
    UPLOAD_FOLDER_HEADIMAGE = r'C:\Users\dfk\PycharmProjects\personalbolg\app\static\headimage'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    @staticmethod
    def init_app(app):
        #配置类可以定义init_app()类方法，其参数是程序实例
        #初始化所有
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}