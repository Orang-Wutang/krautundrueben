import mysql.connector
from pymongo import MongoClient

def get_sql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="krautundrueben"
    )


def get_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client["krautundrueben"]  # Gibt die Datenbank zurück

def get_mongo_collection(collection_name="feedbacks"):
    db = get_mongo_connection()
    return db[collection_name]