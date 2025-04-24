from flask import Flask, render_template, request, flash, redirect
# Flask 会在请求触发后把请求信息放到 request 对象里，你可以从 flask 包导入它....它在请求触发时才会包含数据，所以你只能在视图函数内部调用它。它包含请求相关的所有信息，比如请求的路径（request.path）、请求的方法（request.method）、表单数据（request.form）、查询字符串（request.args）等等
# flash提示消息发送到模板展示给用户
# 重定向响应是一类特殊的响应，它会返回一个新的 URL，浏览器在接受到这样的响应后会向这个新 URL 再次发起一个新的请求。Flask 提供了 redirect() 函数来快捷生成这种响应，传入重定向的目标 URL 作为参数，比如 redirect('http://helloflask.com')。
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  #使用 SQLAlchemy 操作数据库。（ORM，即对象关系映射）
import os
from werkzeug.security import generate_password_hash, check_password_hash  # Flask 的依赖 Werkzeug 内置了用于生成和验证密码散列值的函数，
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, \
    current_user  # 扩展 Flask-Login 提供了实现用户认证需要的各类功能函数，我们将使用它来实现程序的用户认证



app = Flask(__name__)
'''Flask.config 字典用来写入和获取这些配置变量。
配置变量的名称必须使用大写，
写入配置的语句一般会放到扩展类实例化语句之前。'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')#写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里， 在部署章节会详细介绍。
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'#会把用户重定向到登录页面
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

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


import click


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库')  # 输出提示信息

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


@app.route('/login', methods=['GET', 'POST'])
def login():#用于显示登录页面和处理登录表单提交请求的视图函数
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/index')
@app.route('/home')
# 两种方法的请求有不同的处理逻辑：对于 GET 请求，返回渲染后的页面；对于 POST 请求，则获取提交的表单数据并保存。为了在函数内加以区分，我们添加一个 if 判断：
@app.route('/', methods=['GET', 'POST'])#路由的作用就是将这些 URL 与处理这些请求的函数关联起来。  一个视图函数也可以绑定多个 URL，这通过附加多个装饰器实现
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('无效的输入')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('成功创建')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页

    user = User.query.first()  # 读取用户记录，，，有上下文处理函数就不用这句了
    movies = Movie.query.all()  # 读取所有电影记录
    # return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'
    return render_template('/index.html', movies=movies)#render_template() 函数可以把模板渲染出来，必须传入的参数为模板文件名（相对于 templates 根目录的文件路径），这里即 'index.html'。为了让模板正确渲染，我们还要把模板内部使用的变量通过关键字参数传入这个函数


# 创建一个用于显示编辑页面和处理编辑表单提交请求的视图函数：
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
# @login_required  # 登录保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

# 删除表单
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required  # 登录保护   #对于不允许未登录用户访问的视图，只需要为视图函数附加一个 login_required 装饰器就可以将未登录用户拒之门外。以删除条目视图为例：
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('删除成功')
    return redirect(url_for('index'))  # 重定向回主页

from flask_login import login_required, current_user

# ...

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')



# 因为程序只允许一个人使用，没有必要编写一个注册页面。我们可以编写一个命令来创建管理员账户，下面是实现这个功能的 admin() 函数：
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('更新用户...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('创建用户...')
        user = User(username=username)
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')

#
# @app.route('/user/<name>')
# def user_page(name):
#     return f'User: {escape(name)}'
#
#
# '''视图函数的名字是自由定义的。
# 有一个重要的作用：作为代表某个路由的端点（endpoint），同时用来生成视图函数对应的 URL。
# 对于程序内的 URL，为了避免手写，Flask 提供了一个 url_for 函数来生成 URL，它接受的第一个参数就是端点值，默认为视图函数的名称'''
# @app.route('/test')
# def test_url_for():
#     # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
#     print(url_for('hello'))  # 生成 hello 视图函数对应的 URL，将会输出：/
#     # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
#     print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
#     print(url_for('user_page', name='peter'))  # 输出：/user/peter
#     print(url_for('test_url_for'))  # 输出：/test
#     # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
#     print(url_for('test_url_for', num=2))  # 输出：/test?num=2
#     return 'Test page'
#
#
