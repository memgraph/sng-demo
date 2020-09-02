from corporate_struct.database import Memgraph
from corporate_struct import db_operations
from corporate_struct import app

@app.route('/')
@app.route('/index')
def index():
    db = Memgraph()
    db_operations.clear(db)
    db_operations.import_data(db)
    return "Hello, World!"

