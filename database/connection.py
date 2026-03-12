import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="Bob_Family_Tree"
    )