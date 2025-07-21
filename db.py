import pymysql
from pymongo import MongoClient

def get_connection():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="kraut_und_rueben",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
def get_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client["kraut_und_rueben"]  # Name der MongoDB-Datenbank