import logging
import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

logger = logging.getLogger("skeleton_service")

_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def connect_to_mongo() -> None:
    global _client, _database

    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DATABASE_NAME")

    if not mongo_uri or not db_name:
        raise RuntimeError("Missing MONGO_URI or DATABASE_NAME env variables. (Check .env file)")

    _client = MongoClient(mongo_uri)
    _database = _client[db_name]
    _client.admin.command("ping")
    # _client.server_info()  # Force connection to check if it's successful

    logger.info(f"Connected to MongoDB: {db_name}")


def get_database() -> Database:
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return _database


def close_mongo_connection() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed. (This may take a few seconds.)")
