from flask import Flask,render_template
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  #使用 SQLAlchemy 操作数据库。（ORM，即对象关系映射）
import os

app = Flask(__name__)
'''Flask.config 字典用来写入和获取这些配置变量。
配置变量的名称必须使用大写，
写入配置的语句一般会放到扩展类实例化语句之前。'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')#写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app

# 创建数据库模型，，模型类中的属性称之为字段，，模型类中进行各种操作来代替写 SQL 语句
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
    '''有了模型类后打开flask shell：
>>> (env) $ flask shell
>>> from app import db
>>> db.create_all() ，，，后，根目录下会有一个数据库文件 data.db。这个文件不需要提交到 Git 仓库，我们在 .gitignore 文件最后添加一行新规则*.db'''

import click


@app.cli.command()#这是 Flask 框架中用于定义命令行命令的装饰器。Flask 内置了对 click 的支持，使得开发者可以方便地为 Flask 应用程序添加自定义的命令行命令。
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'yqh'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

@app.context_processor#模板上下文处理函数,,这样不同页面的模板用到的相同数据就不用反复调数据库
def inject_user():
    user = User.query.first()
    return dict(user=user)# # 需要返回字典，等同于 return {'user': user}


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/index')
@app.route('/home')
@app.route('/')#路由的作用就是将这些 URL 与处理这些请求的函数关联起来。  一个视图函数也可以绑定多个 URL，这通过附加多个装饰器实现
def index():
    user = User.query.first()  # 读取用户记录，，，有上下文处理函数就不用这句了
    movies = Movie.query.all()  # 读取所有电影记录
    # return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'
    return render_template('/index.html', movies=movies)#render_template() 函数可以把模板渲染出来，必须传入的参数为模板文件名（相对于 templates 根目录的文件路径），这里即 'index.html'。为了让模板正确渲染，我们还要把模板内部使用的变量通过关键字参数传入这个函数


@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'


'''视图函数的名字是自由定义的。
有一个重要的作用：作为代表某个路由的端点（endpoint），同时用来生成视图函数对应的 URL。
对于程序内的 URL，为了避免手写，Flask 提供了一个 url_for 函数来生成 URL，它接受的第一个参数就是端点值，默认为视图函数的名称'''
@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('hello'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'


