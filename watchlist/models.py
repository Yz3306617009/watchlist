'''模型类'''

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import app, db
# 创建数据库模型，，模型类中的属性称之为字段，，模型类中进行各种操作来代替写 SQL 语句
class User(db.Model,UserMixin):#还要继承 Flask-Login 提供的 UserMixin 类
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
    '''有了模型类后打开flask shell：
>>> (env) $ flask shell
>>> from app import db
>>> db.create_all() ，，，后，根目录下会有一个数据库文件 data.db。这个文件不需要提交到 Git 仓库，我们在 .gitignore 文件最后添加一行新规则*.db
也可以用后面写的命令行函数initdb'''
