from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/status')
def status():
    return {"status": "ok", "message": "Flask server running"}

if __name__ == '__main__':
    try:
        print("启动最小化Flask测试服务器...")
        print("访问地址: http://127.0.0.1:5002")
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()