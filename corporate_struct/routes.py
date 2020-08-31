from corporate_struct import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"