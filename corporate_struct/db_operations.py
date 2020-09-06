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


def get_graph(db):
    command = "MATCH (n1)-[e:FRIENDS]-(n2) RETURN n1,n2,e;"
    relationships = db.execute_and_fetch(command)

    link_objects = []
    nodes_objects = []
    added_nodes = []
    for rel in relationships:
        e = rel['e']
        data = {"source": e.nodes[0], "target": e.nodes[1]}
        link_objects.append(data)

        n1 = rel['n1']
        if not (n1.id in added_nodes):
            data = {"id": n1.id, "name": n1.properties['name']}
            nodes_objects.append(data)
            added_nodes.append(n1.id)

        n2 = rel['n2']
        if not (n2.id in added_nodes):
            data = {"id": n2.id, "name": n2.properties['name']}
            nodes_objects.append(data)
            added_nodes.append(n2.id)
    data = {"edges": link_objects, "nodes": nodes_objects}

    return json.dumps(data)


def get_users(db):
    command = "MATCH (n:User) RETURN n;"
    users = db.execute_and_fetch(command)

    user_objects = []
    for user in users:
        u = user['n']
        data = {"id": u.properties['id'], "name": u.properties['name']}
        user_objects.append(data)

    return json.dumps(user_objects)


def get_realtionships(db):
    command = "MATCH (n1)-[e:FRIENDS]-(n2) RETURN n1,n2,e;"
    relationships = db.execute_and_fetch(command)

    relationship_objects = []
    for relationship in relationships:
        u1 = relationship['n1']
        u2 = relationship['n2']

        data = {"userOne": u1.properties['name'],
                "userTwo": u2.properties['name']}
        relationship_objects.append(data)

    return json.dumps(relationship_objects)
