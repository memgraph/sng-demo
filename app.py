from flask import Flask, render_template, request, jsonify, make_response
from corporate_struct.database import Memgraph
from corporate_struct import db_operations

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    db = Memgraph()
    #db_operations.clear(db)
    #db_operations.import_data(db)

    return render_template('index.html')

@app.route("/get-graph", methods=["POST"])
def create_entry():
    db = Memgraph()
    
    req = request.get_json()
    
    print(db_operations.fetch_roles(db))
    
    res = make_response(jsonify(db_operations.fetch_relationships(db)), 200)

    return res
