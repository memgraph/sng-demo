from pathlib import Path
import json
from collections import namedtuple


def clear(db):
    command = "MATCH (node) DETACH DELETE node"
    db.execute_query(command)


def import_data(db):
    file = open("resources/data.txt")
    lines = file.readlines()
    file.close()
    for line in lines:
        if len(line.strip()) != 0 and line[0] != '/':
            db.execute_query(line)


def fetch_tasks(db):
    task_objects = []
    command = "MATCH (n:Task) RETURN n;"
    tasks = db.execute_and_fetch(command)
    
    for task in tasks:
        tasksDictByName = {}
        t = task['n']
        tasksDictByName['name'] = t.properties['name']
        task_objects.append(tasksDictByName)
    json_data = json.dumps(task_objects)
    print(json_data)
    return task_objects

def fetch_roles(db):
    role_objects = []
    Role = namedtuple("Role", "name description")

    command = "MATCH (n:Role) RETURN n;"
    roles = db.execute_and_fetch(command)

    for role in roles:
        r = role['n']
        role_object = Role(
            name=r.properties['name'], description="")
        role_objects.append(role_object)

    print(role_objects)
    return role_objects

def fetch_relationships(db):
    command = "MATCH (n1)-[e]-(n2) RETURN n1,n2,e;"
    relationships = db.execute_and_fetch(command)

    link_objects = []
    nodes_objects = []
    added_nodes = []
    for rel in relationships:
        nodeDictByName = {}
        linkDictByName = {}
        e = rel['e']
        linkDictByName['source'] = e.nodes[0]
        linkDictByName['target'] = e.nodes[1]
        link_objects.append(linkDictByName)

        n1 = rel['n1']
        if not (n1.id in added_nodes):
            nodeDictByName['id'] = n1.id
            nodeDictByName['name'] = n1.properties['name']
            nodes_objects.append(nodeDictByName)
            added_nodes.append(n1.id)

        nodeDictByName = {}

        n2 = rel['n2']
        if not (n2.id in added_nodes):
            nodeDictByName['id'] = n2.id
            nodeDictByName['name'] = n2.properties['name']
            nodes_objects.append(nodeDictByName)
            added_nodes.append(n2.id)

    data = {"edges": link_objects, "nodes": nodes_objects}
    return json.dumps(data)