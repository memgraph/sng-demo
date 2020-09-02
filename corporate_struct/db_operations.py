from pathlib import Path


def clear(db):
    command = "MATCH (node) DETACH DELETE node"
    db.execute_query(command)


def import_data(db):
    file = open("resources/data.txt")
    lines = file.readlines()
    file.close()
    for line in lines:
        if len(line.strip()) != 0 and line[0] != '/':
            print(line)
            db.execute_query(line)
