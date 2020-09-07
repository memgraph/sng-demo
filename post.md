# Introduction


When you think about a web application, a Graph Database doesn’t usually spring to mind. Instead, most people just take the familiar route of using an SQL database to store information. While this is perfectly acceptable for most use cases there are sometimes those that would see tremendous benefits by using a graph database. 
In this tutorial, I will show you how to make a basic web application using Flask that stores all of its information in a graph database. To be more precise we are using Memgraph DB, an in-memory database that can easily handle a lot of information and perform read/write instructions quite quickly.<br /><br />

Our use case is a Social Network Graph (later on referred to as SNG) representing users and the connections between them. Usually such a graph would contain millions of nodes and edges and the algorithms that are performed on them don’t do well with data being stored in relational databases. 

<br /><br />
<p align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/9/9b/Social_Network_Analysis_Visualization.png" alt="Data Model" width="600"/>
<p/>


# Prerequisites


Because we are building a complete web application there is a number of tools that you will need to install before we begin: 
* Poetry - [How to install Poetry](https://python-poetry.org/docs/)<br />Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.
* Flask - [How to install Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/)<br />Flask is a web framework. This means flask provides you with tools, libraries and technologies that allow you to build a web application. Such an application can be as small as a single web page or a complex management interface.
* Docker - [How to install Docker](https://docs.docker.com/get-docker/)<br />Docker is an open platform for developing, shipping, and running applications. It enables us to separate our application from our infrastructure.

Creating a Poetry Project
To create our project structure we are going to use Poetry. Position yourself where you want to create the project and run:

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

In this tutorial, we won’t use the testing functionalities so go on ahead and delete the directory tests. 

Now you need to add the dependencies using Poetry by running:
```
poetry add pymgclient
poetry add flask
```
We need to specify which version of python will be used in the Docker container so edit the line python = "^3.8" in the file project.toml and run:
```
poetry lock
```
This will update the poetry.lock file and all the dependencies for the project.<br /><br />


# Dockerizing an Application


In the root directory of the project create two files, Dockerfile and docker-compose.yml. At the beginning of the Dockerfile, we specify the desired version of Python and instruct the container to install CMake, poetry, mgclient and pymgclient. Poetry is necessary to manage our dependencies inside the container while CMake and mgclient are needed to run pymgclient, the Python driver for Memgraph DB. You don’t have to focus too much on this part just copy the code to your Dockerfile:
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
This command will enable us to cache the project requirements and only reinstall them when pyproject.toml or poetry.lock are changed.  
```
RUN poetry config virtualenvs.create false && \
   poetry install --no-interaction --no-ansi
```
We don’t need to create a virtual environment because our application is already isolated by being in a Docker container. To disable it virtualenvs.create needs to be set to false. 
The second line in the command ensures that Poetry asks us no interactive questions while installing/updating dependencies and it makes the output more log friendly. 
```
COPY . /app
EXPOSE 5000
ENTRYPOINT [ "poetry", "run" ]
```
This is where we essentially create all the directories and files inside of our container. The `EXPOSE` command informs Docker that the container listens on the specified network port at runtime.

Next, we need to create a docker-compose.yml file. Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration. For our project, we need two services. One is the web application (`sng_demo`) and the other a database instance (`memgraph`). 

If you followed the instructions on how to setup Memgraph DB with Docker correctly you only need to add the following code to your docker-compose.yml file to run the container:
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
You need to be aware of an important distinction between HOST_PORT and CONTAINER_PORT. The first number is the HOST_PORT and it can be used to connect from your host machine to the service  (for example with Memgraph Lab). The second number specifies the HOST_PORT which is used for service-to-service communication. More precisely, our service sng_db can use this port to access the service memgraph and connect to the database. 

With `MG_HOST` and `MG_PORT` we assign environment variables to the service’s container. They contain the address and port needed to establish a database connection.
The `depends_on` key is used to start services in dependency order because we need the database to be up and running before the web application.

The `build` key allows us to tell Compose where to find the build instructions as well as the files and/or folders used during the build process. By using the volumes key we bypass the need to constantly restart our image to load new changes to it from the host machine.

Finally, we have a dockerized project that utilizes Poetry! This is a wonderful way of cross-platform development because it enables developers to run this in completely different operating systems and environments without having to worry about compatibility.<br /><br />


# Web Page with Flask


Flask is unbelievably simple to use so why not create a Hello World page to try out our Docker+Poetry setup. In the project root directory create a file named app.py with the following code:
```
from flask import Flask
 
app = Flask(__name__)
 
@app.route('/')
@app.route('/index')
def index():
  return "Hello World"
```
The only other thing we need to do is to tell Docker how to run our app. This can be done by creating a simple script in the project root directory. Let’s call it start.sh:
```
#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host 0.0.0.0
```
In your Dockerfile after the line `EXPOSE 5000` put the following code:
```
ADD start.sh /
RUN chmod +x /start.sh
```
And after `ENTRYPOINT [ "poetry", "run" ]` add:
```
CMD ["/start.sh"]
```
That’s it! Our first web page is ready so let’s start our app to make sure we don’t have any errors. First, run:
```
docker-compose build
docker-compose up
```
The URL for our web application is http://localhost:5000/. When you open it you should see the message Hello World! which means that the app is up and running.
Now it’s time to create a more complex web page. In the project root directory create a folder called templates and in it a file with the name base.html. This will be our base template for other sites. You can find its contents here: base.html.
We also need to create an HTML file for our actual landing site that utilizes this base file and an accompanying JS file. Create the HTML file in the same location with the name index.html. Copy the following code into it:
```
{% extends 'base.html' %} {% block content %}
<div class="container">
   Hello World!
</div>
<script src="/static/js/index.js" charset="utf-8"></script>
{% endblock %}
```
In the project root directory create a folder called static with one subfolder called js and another one called css. The js folder will contain all of the needed local JS files while the css folder will contain all the stylesheets. In the js folder create a file named index.js and leave it empty for now.<br /><br /> 


# Connecting to the Database


In the app directory sng-demo make a folder named database. This folder will contain all of the modules that we need to communicate with the database. You can find them here and just copy their contents. They are closely related to the database driver and if you wish to examine them a bit more I suggest you look up the driver documentation here.
In the app directory sng-demo create the module db_operations.py. This is where all the methods with database queries will be placed. This is how the app directory should look like:

```
sng_demo
├── db_operations.py
└── database
    ├── __init__.py
    ├── memgraph.py
    ├── connection.py
    └── models.py
``` 
<br /><br />

# The Data Model


We will use a very simple data model that can be easily upgraded later on. There is only one node type and it is labeled `User`. Each `User` has two properties, a numerical `id` and a string `name`. Nodes are connected with edges of type `FRIENDS`.


<img src="https://github.com/g-despot/images/blob/master/Screenshot%20from%202020-09-06%2019-00-09.png?raw=true" alt="Data Model" width="200"/>

There are several methods to populate a database ([more on that here](https://docs.memgraph.com/memgraph/how-to-guides-overview/import-data)) but we will be doing it manually by executing Cypher queries. You can find the queries for the upper graph here. In the project root directory create a folder called resources and place the file data.txt in it. Now you can add an import method to your web application. In the module db_operations.py add the following imports and methods:<br /><br />

<p align="center">
    <img src="https://github.com/g-despot/images/blob/master/Screenshot%20from%202020-09-06%2019-04-29.png?raw=true" alt="Data Model" width="600"/>
<p/>

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
With the method clear() we will delete all the data in the database before importing our new. I The method populate_database() reads all the Cypher queries in the specified file and executes them. In the module app.py change the method index() to:

```python
@app.route('/')
@app.route('/index')
def index():
   db = Memgraph()
   db_operations.clear(db)
   db_operations.populate_database(db, "resources/data.txt")
   return render_template('index.html')
```

Now let's do something with this data! Here you can find the content for the `index.js` file. I am not going to go into much detail about how to use D3.js so if you want to find out more I encourage you to visit [their site](https://d3js.org/).
 
We fetch all the nodes and edges from the database and add them to an SVG element. The graph that we generate is made by simulating how physical forces act on particles. You can drag & drop the nodes and hover over them to see the value of their name property. 

Additional Functionalities
Go ahead and copy the file `query.js` to `/static/js/` and `query.html` to `/templates/`. In your `base.html` file add an additional navbar item:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('query')}}">Query Database</a>
</li>
```
This will make your life easier if you want to debug the data being fetched from the server. 
