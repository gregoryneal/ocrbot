import sqlite3
import os

VALIDATION_TABLE_NAME = 'validation'
VISITED_LINKS_TABLE_NAME = 'visitedlinks'
dbpath = os.path.dirname(os.path.realpath(__file__))+"/db/botdata.db"

def recreateDatabase():
    #delete the database file if it exists
    try:
        os.remove(dbpath)
    except OSError:
        pass

    #now recreate it and connect with it
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    #create the validation table
    expr = 'CREATE TABLE ? (clientid TEXT, clientsecret TEXT, username TEXT, password TEXT)'
    cursor.execute(expr, (VALIDATION_TABLE_NAME,))

    #create the visitedLinks table
    expr = 'CREATE TABLE ? (postid TEXT)'
    cursor.execute(expr, (VISITED_LINKS_TABLE_NAME,))

    connection.commit()
    connection.close()

def addVisitedLink(postid):

    expr = 'INSERT INTO TABLE ? (?)'
    cursor.execute(expr, (VISITED_LINKS_TABLE_NAME, postid,))
    
    connection.commit()
    connection.close()

def linkExists(postid):
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    #check if a link exists, this statement returns either (1,) or (0,) for the id existing or not, respectively.
    expr = 'SELECT count(*) FROM ? WHERE postid = ?'
    cursor.execute(expr, (VISITED_LINKS_TABLE_NAME, postid))
    data=cursor.fetchone()[0]
    connection.close()
    if data==0:
        return False
    else:
        return True
    