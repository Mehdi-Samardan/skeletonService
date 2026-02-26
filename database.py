# database.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = None
database = None


def connect_to_mongo():
    global client, database

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DATABASE_NAME")

    if not mongo_uri or not db_name:
        raise RuntimeError("Missing MongoDB ENV variables")

    client = MongoClient(mongo_uri)
    database = client[db_name]

    print(f"Connected to MongoDB: {db_name}")


def get_database():
    if database is None:
        raise RuntimeError("Database not initialized")
    return database
