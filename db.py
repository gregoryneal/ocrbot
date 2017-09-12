import sqlite3
import os

VALIDATION_TABLE_NAME = 'validation'
VISITED_LINKS_TABLE_NAME = 'visitedlinks'
dbname = 'botdata.db'
dbpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), dbname)

def recreateDatabase(clientid, clientsecret, username, password):
    print("Recreating database: will destroy existing database file in " + dbpath)
    #delete the database file if it exists
    try:
        os.remove(dbname)
        print("Removed old database...")
    except OSError:
        print("oserror when removing database file")
        pass

    #now recreate it and connect with it
    connection = sqlite3.connect(dbname)
    print("Connected to server: " + dbname)
    cursor = connection.cursor()

    #create the validation table and populate it
    expr = 'CREATE TABLE {} (clientid TEXT, clientsecret TEXT, username TEXT, password TEXT)'.format(VALIDATION_TABLE_NAME)
    cursor.execute(expr)
    print("Created validation table...")

    expr = 'INSERT INTO {} VALUES (?,?,?,?)'.format(VALIDATION_TABLE_NAME)
    args = (str(clientid), str(clientsecret), str(username), str(password),)
    cursor.execute(expr, args)
    print("Initialized validation table...")

    #create the visitedLinks table
    expr = 'CREATE TABLE {} (postid TEXT)'.format(VISITED_LINKS_TABLE_NAME)
    cursor.execute(expr)
    print("Created visitedlinks table...")

    connection.commit()
    connection.close()
    print("Finished recreating database!")

def addVisitedLink(postid):
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    expr = 'INSERT INTO {} VALUES (?)'.format(VISITED_LINKS_TABLE_NAME)
    cursor.execute(expr, (postid,))
    
    connection.commit()
    connection.close()

def linkExists(postid):
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    #check if a link exists, this statement returns either (1,) or (0,) for the id existing or not, respectively.
    expr = 'SELECT count(*) FROM {} WHERE postid = ?'.format(VISITED_LINKS_TABLE_NAME)
    cursor.execute(expr, (postid,))
    data = cursor.fetchone()[0]
    connection.close()
    if data == 0:
        return False
    else:
        return True

def addLinksFromFile(filepath):
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()
    lines = []
    with open(filepath, 'r') as file:
        lines = [(x.replace("\n",""),) for x in file.readlines()] #[(id1),(id2),...]

    print(lines[0])
    cursor.executemany('INSERT INTO {} VALUES (?)'.format(VISITED_LINKS_TABLE_NAME), lines)
    connection.commit()
    connection.close()

def getLastLink():
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM {} ORDER BY ROWID DESC LIMIT 1'.format(VISITED_LINKS_TABLE_NAME))
    data = cursor.fetchone()[0]
    connection.commit()
    connection.close()
    return data

def getCredentials():    
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    expr = 'SELECT * FROM {} LIMIT 1'.format(VALIDATION_TABLE_NAME)

    cursor.execute(expr)
    data = cursor.fetchone()
    connection.close()

    return data

def runStatement(expression, arguments):
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()
    cursor.execute(expression, arguments)
    connection.commit()
    connection.close()