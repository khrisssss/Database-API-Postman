import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="khris",
        password="cute",
        database="Bob_Family_Tree"
    )