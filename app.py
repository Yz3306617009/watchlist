from flask import Flask
from markupsafe import escape
from flask import url_for

app = Flask(__name__)
@app.route('/index')
@app.route('/home')
@app.route('/')#路由的作用就是将这些 URL 与处理这些请求的函数关联起来。  一个视图函数也可以绑定多个 URL，这通过附加多个装饰器实现
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


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