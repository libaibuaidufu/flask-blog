#!/usr/bin/env python
#coding:utf-8

import os,sys
from app import create_app,db
from app.models import User,Role,Liuyan,Post,Follow,Fenlei
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

reload(sys)
sys.setdefaultencoding('utf-8')

app = create_app(os.getenv('DFK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,Liuyan=Liuyan,Fenlei=Fenlei,Post=Post,Follow=Follow)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == "__main__":
    manager.run()