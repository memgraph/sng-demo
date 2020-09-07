# Introduction
 
 
When you think about a web application, a graph database doesn’t usually spring to mind. Instead, most people just take the familiar route of using an SQL database to store information. While this is perfectly acceptable for most use cases there are sometimes those that would see tremendous benefits by using a graph database.
In this tutorial, I will show you how to make a basic web application using Flask that stores all of its information in a graph database. To be more precise we are using Memgraph DB, an in-memory database that can easily handle a lot of information and perform read/write instructions quite quickly.<br /><br />
Our use case is a Social Network Graph (in the code referred to as **SNG** for convenience) representing users and the connections between them. Usually, such a graph would contain millions of nodes and edges and the algorithms that are performed on them don’t do well with data being stored in relational databases.<br /><br />
In this tutorial, I will go through most of the code so you get a basic understanding even if you are not that familiar with some of the technologies used. You can also find all of [the code here]() if you don't want to type it as you read.
 
<br /><br />
<p align="center">
   <img src="https://upload.wikimedia.org/wikipedia/commons/9/9b/Social_Network_Analysis_Visualization.png" alt="Data Model" width="600"/>
<p/>

# Prerequisites
 
 
Because we are building a complete web application there is a number of tools that you will need to install before we begin:
* **[Poetry](https://python-poetry.org/docs/)**: a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.
* **[Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/)**: a very powerful web framework. This means flask provides you with tools, libraries and technologies that allow you to build a web application. Such an application can be as small as a single web page or a complex management interface.
* **[Docker and Compose](https://docs.docker.com/get-docker/)**: an open platform for developing, shipping, and running applications. It enables us to separate our application from our infrastructure. You also need to install Compose with Docker. If you are installing Docker on Windows, Compose will be already included but for Linux and macOS visit [this site](https://docs.docker.com/compose/install/).
* **[Memgraph DB](https://docs.memgraph.com/memgraph/quick-start)**: a native fully distributed in-memory graph database built to handle real-time use-cases at enterprise scale. **Follow the Docker Installation instructions.** While it's completely optional I encourage you to also install **[Memgraph Lab](https://memgraph.com/product/lab)** so you can execute Cypher queries on the database directly and see visualized results.
<br /><br />

# Creating a Poetry Project


Because packaging systems and dependency management in Python can sometimes be confusing for beginners we decided to go with Poetry.
Creating our project structure can easily be done by using Poetry.<br />Choose a working directory and run:
 
```
poetry new sng-demo
```
 
Now you should have a directory with the following content:

```
sng-demo
├── pyproject.toml
├── README.rst
├── sng_demo
│   └── __init__.py
└── tests
   ├── __init__.py
   └── test_poetry_demo.py
```
 
In this tutorial, we won’t use the testing functionalities so go on ahead and delete the directory `tests` as well as the file `README.rst`.
 
Now you need to add the dependencies for our project. Given that we are going to run the app inside a Docker container we don't need the dependencies installed locally, only inside the container. Copy the files `project.toml` and `poetry.lock` [from here]() and place them in the root directory of the project.<br /><br />
 
 
# Dockerizing an Application
 
 
In the root directory of the project create two files, `Dockerfile` and `docker-compose.yml`. At the beginning of the `Dockerfile`, we specify the desired version of Python and instruct the container to install CMake, poetry, mgclient and pymgclient. Poetry is necessary to manage our dependencies inside the container while CMake and mgclient are required for pymgclient, the Python driver for Memgraph DB. You don’t have to focus too much on this part just copy the code to your Dockerfile:
```
FROM python:3.7
#Install CMake
RUN apt-get update && \
  apt-get --yes install cmake
#Install poetry
RUN pip install -U pip \
  && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/root/.poetry/bin"
#Install mgclient
RUN apt-get install -y git cmake make gcc g++ libssl-dev && \
  git clone https://github.com/memgraph/mgclient.git /mgclient && \
  cd mgclient && \
  mkdir build && \
  cd build && \
  cmake .. && \
  make && \
  make install
#Install pymgclient
RUN git clone https://github.com/memgraph/pymgclient /pymgclient && \
  cd pymgclient && \
  python3 setup.py build && \
  python3 setup.py install
```
Next, we define the working directory with:
```
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
```
This command will enable us to cache the project requirements and only reinstall them when `pyproject.toml` or `poetry.lock` are changed. 
```
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi
```
We don’t need to create a virtual environment because our application is already isolated by being in a Docker container. To disable it `virtualenvs.create` needs to be set to false.<br />
The second line in the command ensures that Poetry asks us no interactive questions while installing/updating dependencies and it makes the output more log friendly.
```
COPY . /app
EXPOSE 5000
ENTRYPOINT [ "poetry", "run" ]
```
This is where we essentially create all the directories and files inside of our container. The `EXPOSE` command informs Docker that the container listens on the specified network port at runtime.
 
Next, we need to create a docker-compose.yml file. Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration. For our project, we need two services. One is the web application (`sng_demo`) and the other a database instance (`memgraph`).
 
If you followed the instructions on [how to setup Memgraph DB with Docker](https://docs.memgraph.com/memgraph/quick-start) correctly you only need to add the following code to your `docker-compose.yml` file to run the container:
```
version: '3'
services:
memgraph:
  image: "memgraph"
  ports:
    - "7687:7687"
sng_demo:
  build: .
  volumes:
    - .:/app
  ports:
    - "5000:5000"
  environment:
    MG_HOST: memgraph
    MG_PORT: 7687
  depends_on:
    - memgraph
```
There needs to be an important distinction when it comes to the `ports key` between HOST_PORT and CONTAINER_PORT. The first number in the key is the HOST_PORT and it can be used to connect from your host machine to the service (for example with Memgraph Lab). The second number specifies the HOST_PORT which is used for service-to-service communication. More precisely, our service `sng_db` can use this port to access the service `memgraph` and connect to the database.
 
With `MG_HOST` and `MG_PORT` we assign environment variables to the service’s container. They contain the address and port needed to establish a database connection.
The `depends_on` key is used to start services in dependency order because we need the database to be up and running before the web application.
 
The `build` key allows us to tell Compose where to find the build instructions as well as the files and/or folders used during the build process. By using the `volumes` key we bypass the need to constantly restart our image to load new changes to it from the host machine.
 
Finally, we have a dockerized project that utilizes Poetry! This is a wonderful way of cross-platform development because it enables developers to run their project in completely different operating systems and environments without having to worry about compatibility.
<br /><br />


# Web Development with Flask
 
 
Flask is very simple to use so why not create a **Hello World!** page to try out our Docker+Poetry setup.<br /> 
In the project root directory create a file called `app.py` with the following code:
```python
from flask import Flask
 
app = Flask(__name__)
 
 
@app.route('/')
@app.route('/index')
def index():
   return "Hello World"

```
First, we imported the Flask class and then created an instance of it. The `route()` decorator tells Flask what URL should trigger our function.
The only other thing we need to do is to tell Docker how to run our app. This can be done by creating a simple script in the project root directory. Let’s call it `start.sh`:
```
#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host 0.0.0.0
```
Setting `FLASK_ENV` to `development` will enable debug mode so Flask uses an interactive debugger and reloader while setting `FLASK_APP` to `app.py` specifies how to start the application.<br /> 
We need to tell Docker when and how to run this script so put the following code in your `Dockerfile` after the line `EXPOSE 5000` :
```
ADD start.sh /
RUN chmod +x /start.sh
```
The command `chmod +x` makes the script executable by setting the right permission.<br /> 
To execute the script add the following command after `ENTRYPOINT [ "poetry", "run" ]`:
```
CMD ["/start.sh"]
```
That’s it! Our first web page is ready so let’s start our app to make sure we don’t have any errors. In the project root directory execute:
```
docker-compose build
docker-compose up
```
The URL of our web application is http://localhost:5000/. When you open it there should be a message **Hello World!** which means that the app is up and running.<br />
Now it’s time to create a more complex web page that will contain our Social Network Graph. In the project root directory create a folder called `templates` and in it a file with the name `base.html`. This will be our base template for other sites. You can find its contents here: [base.html]().
We also need to create an HTML file for our actual landing site that utilizes this base file and an accompanying JS file. Create the HTML file in the same location with the name `index.html` and copy the following code into it:
```html
{% extends 'base.html' %} {% block content %}
<div class="container">
  Hello World!
</div>
<script src="/static/js/index.js" charset="utf-8"></script>
{% endblock %}
```
In the project root directory create a folder called `static` with one subfolder called `js` and another called `css`. The `js` folder will contain all of the needed local JavaScript files while the `css` folder will contain all the CSS stylesheets. In the `js` folder create a file called `index.js` and leave it empty for now.<br /><br />
If you want to find out more about web development with Flask I suggest you try out [this tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).
Your current project structure should like this:
```
sng-demo
├── sng_demo
│  └── __init__.py
├── templates
│  └── index.html
├── static
│  ├── css
│  │  └── style.css
│  └── js
│     ├── base.html
│     └── index.js
├── app.py
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── start.sh
```
<br />

 
# The Data Model and Database Connection
 

In the app directory `sng-demo` create a folder named database. This folder will contain all of the modules that we need to communicate with the database. You can find them [here]() and just copy their contents. They are closely related to the database driver and if you wish to examine them a bit more I suggest you look up the driver documentation [here](https://github.com/memgraph/pymgclient). 
In the app directory `sng-demo` create the module `db_operations.py`. This is where all the database related commands will be located. 
The `sng_demo` directory should look like:
 
```
sng_demo
├── db_operations.py
└── database
   ├── __init__.py
   ├── memgraph.py
   ├── connection.py
   └── models.py
``` 
We will use a very simple data model that can be easily upgraded later on.<br />
There is only one node with the label `User` and each `User` has two properties, a numerical `id` and a string `name`. Nodes are connected with edges of the type `FRIENDS`.
 
<p align="center">
<img src="https://github.com/g-despot/images/blob/master/user.png?raw=true" alt="Data Model" width="250"/>
<p/>
 
There are several methods to populate a database ([more on that here](https://docs.memgraph.com/memgraph/how-to-guides-overview/import-data)) but we will be doing it manually by executing Cypher queries so you can get a better understanding of how to communicate with the database. You will find all the necessary queries to populate our database in the file `data.txt` [here](). In the project root directory create a folder called `resources` and place the file `data.txt` in it. Now you can add an import method to your web application.<br />
In the module db_operations.py add the following imports and methods:
 
```python
from pathlib import Path
import json
def clear(db):
  command = "MATCH (node) DETACH DELETE node"
  db.execute_query(command)
def populate_database(db, path):
  file = open(path)
  lines = file.readlines()
  file.close()
  for line in lines:
      if len(line.strip()) != 0 and line[0] != '/':
          db.execute_query(line)
```
The method `clear()` deletes any data that could have been left in the database before populating it.<br />
The method `populate_database()` reads all of the Cypher queries in the specified file and executes them.<br /> 
In the module `app.py` change the method `index()` to:
 
```python
@app.route('/')
@app.route('/index')
def index():
  db = Memgraph()
  db_operations.clear(db)
  db_operations.populate_database(db, "resources/data.txt")
  return render_template('index.html')
```
Every time we refresh our index page the database is cleared and repopulated with new data. While this is not suitable for the production stage it is highly usefull during development because it will enable us to make changes in the data without having to restart the whole application or working directly on the database.<br />
If you want to examine the graph before proceeding I suggest you open Memgraph Lab and run the query `MATCH (n1)-[e:FRIENDS]-(n2) RETURN n1,n2,e;`.<br />
The result should be:

<br />
<p align="center">
   <img src="https://github.com/g-despot/images/blob/master/sng_lab.png?raw=true" alt="Data Model" width="900"/>
<p/>
<br />

We also need a method in our app to fetch all the relevant data from the database when a client requests it.<br />
Let’s call it `get_graph()` and place it in the `db_operations.py` module:
 
```python
def get_graph(db):
   command = "MATCH (n1)-[e:FRIENDS]-(n2) RETURN n1,n2,e;"
   relationships = db.execute_and_fetch(command)
 
   link_objects = []
   node_objects = []
   added_nodes = []
   for relationship in relationships:
       e = relationship['e']
       data = {"source": e.nodes[0], "target": e.nodes[1]}
       link_objects.append(data)
 
       n1 = rel['n1']
       if not (n1.id in added_nodes):
           data = {"id": n1.id, "name": n1.properties['name']}
           node_objects.append(data)
           added_nodes.append(n1.id)
 
       n2 = rel['n2']
       if not (n2.id in added_nodes):
           data = {"id": n2.id, "name": n2.properties['name']}
           node_objects.append(data)
           added_nodes.append(n2.id)
   data = {"links": link_objects, "nodes": nodes_objects}
 
   return json.dumps(data)
```
 
First, we need to execute the Cypher query `MATCH (n1)-[e:FRIENDS]-(n2) RETURN n1,n2,e;` and return its results from the database. These results will contain all the edges in the graph as well as all the nodes that are connected to those edges. Nodes that don't have connections will not be returned and that's ok for now.<br /><br />
The results (the object `relationships`) are in the form of a generator which we can iterate over and access its contents by using the node/edge names specified in our initial query (`n1`,`n2` and `e`).<br />
We also need to check if a node has already been appended to the `node_objects` list because multiple edges can contain (point to or from) the same node. All of the objects are stored in key-value pairs suitable for later JSON conversion.<br />
The final result is a JSON array containing two objects: 
* `links`: contains all the relationships that are in the graph as pairs of `source` and `target` id properties,
* `nodes`: contains all the nodes from the graph that form relationships with other nodes. 
 
In your `app.py` module add the following method:

```python
@app.route("/get-graph", methods=["POST"])
def get_graph():
   db = Memgraph()
   response = make_response(
       jsonify(db_operations.get_graph(db)), 200)
   return response
```

This method is responsible for responding to POST requests from the client. It returns the graph data that we fetched from the server in the previous method.<br /><br />
Now let's do something with this data! Copy the contents of the `index.js` file that you created earlier [from here](). I don't want to go into much detail about how to use **D3.js** so if you want to find out more I encourage you to visit [their website](https://d3js.org/).<br />
I short, we fetch all the nodes and edges from the database and add them to an SVG element. The visual representation of the graph is made by simulating how physical forces act on particles (charge and gravity). You can drag & drop the nodes and hover over them to see the value of their name property.<br /><br />


<p align="center">
   <img src="https://github.com/g-despot/images/blob/master/sng_d3.png?raw=true" alt="Data Model" width="600"/>
<p/>
<br />
 

# Additional Functionalities
 
 
Go ahead and copy the file `query.js` to `/static/js/` and `query.html` to `/templates/`. In your `base.html` file add an additional navbar item:
 
```html
<li class="nav-item">
   <a class="nav-link" href="{{ url_for('query')}}">Query Database</a>
</li>
```
This page with its queries will make your life easier if you want to debug the data being fetched from the server. It will return all the nodes and all the edges and show them in a JSON highlighted format.<br />
Your current project structure should like this:
```
sng-demo
├── sng_demo
│  ├── db_operations.py
│  └── database
│     ├── __init__.py
│     ├── memgraph.py
│     ├── connection.py
│     └── models.py
├── templates
│  ├── base.html
│  ├── index.html
│  └── query.html
├── static
│   ├── css
│   │  └── style.css
│   └── js
│      ├── index.js
│      └── query.js
├── app.py
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── start.sh
```
<br />


# Conclusion


Even though graph databases have been around for a long time they are still not a mainstream tool in software development. This is a shame given that many problems could be much easier tackled with their help. A lot of data in the modern world is better suited for graph representation and graph databases offer built-in algorithms which are highly efficient on such datasets in comparison to the standard relational paradigm.<br />
I hope that this tutorial can demonstrate how easy it is to use graph databases in conjuncture with other technologies.  