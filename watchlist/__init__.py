'''包构造文件，创建程序实例'''

from flask import Flask, render_template, request, flash, redirect
# Flask 会在请求触发后把请求信息放到 request 对象里，你可以从 flask 包导入它....它在请求触发时才会包含数据，所以你只能在视图函数内部调用它。它包含请求相关的所有信息，比如请求的路径（request.path）、请求的方法（request.method）、表单数据（request.form）、查询字符串（request.args）等等
# flash提示消息发送到模板展示给用户
# 重定向响应是一类特殊的响应，它会返回一个新的 URL，浏览器在接受到这样的响应后会向这个新 URL 再次发起一个新的请求。Flask 提供了 redirect() 函数来快捷生成这种响应，传入重定向的目标 URL 作为参数，比如 redirect('http://helloflask.com')。
from markupsafe import escape
from flask import url_for
from flask_sqlalchemy import SQLAlchemy  # 使用 SQLAlchemy 操作数据库。（ORM，即对象关系映射）
import os
from werkzeug.security import generate_password_hash, check_password_hash  # Flask 的依赖 Werkzeug 内置了用于生成和验证密码散列值的函数，
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, \
    current_user  # 扩展 Flask-Login 提供了实现用户认证需要的各类功能函数，我们将使用它来实现程序的用户认证

app = Flask(__name__)
'''Flask.config 字典用来写入和获取这些配置变量。
配置变量的名称必须使用大写，
写入配置的语句一般会放到扩展类实例化语句之前。'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path,
                                                                    '../data.db')  # 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里， 在部署章节会详细介绍。
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'  # 会把用户重定向到登录页面


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from watchlist.models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.context_processor  # 模板上下文处理函数,,这样不同页面的模板用到的相同数据就不用反复调数据库
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # # 需要返回字典，等同于 return {'user': user}

from watchlist import views, errors, commands
