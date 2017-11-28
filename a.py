from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DETABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64))
    count =db.Column(db.integer, default=1)
    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return '<Category %r>' %self.tag

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 时间戳

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Post.title %r>' %self.title
