import random

names = ["Jon", "Monica", "Carl", "Ron", "Anna", "Lucy", "Eddy", "Eva", "Tom", "Harry", "Donna", "Jessica", "Peter", "Ritta", "Sarah", "Rodney", "Phyllis", "Meredith", "Angela",
         "Kelly", "Armando", "Kindra", "Monty", "Jona", "Val", "Lenny", "Bruce", "Simon", "Hector", "Laura", "Oleta", "Drucilla", "Rick", "Morty", "Jerry", "Beth", "Summer", "Eric", "Kenny"]

number_of_nodes = 300

f = open("data.txt", "w+")

for i in range(number_of_nodes):
    row = "CREATE (n:User { id:" + str(i) + ", name: '" + \
        str(random.choice(names)) + "'});\n"
    f.write(row)

for _ in range(2):
    for i in range(number_of_nodes):
        row = "MATCH (a:User),(b:User) WHERE a.id = " + str(i) + " AND b.id = " + str(random.randrange(
            number_of_nodes)) + " CREATE (a)-[r:FRIENDS]->(b);\n"
        f.write(row)

f.close()
