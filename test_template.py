from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def test_template():
    # 创建一个简化的模板来测试
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>模板测试</title>
    </head>
    <body>
        <h1>模板测试页面</h1>
        <script>
            // 测试简单的JavaScript
            console.log('测试成功');
            // 设置一些默认值
            const element = document.createElement('div');
            element.textContent = '动态内容';
            document.body.appendChild(element);
        </script>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    print("启动测试服务器在 http://127.0.0.1:5000/")
    app.run(debug=True)