import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

from utils.logger import logger


# Global variables
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection.
    Called once at application startup.
    """

    global _client, _database

    # 1️⃣ Load environment variables
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("DATABASE_NAME")

    if not mongo_uri:
        logger.critical("MONGO_URI not found in environment variables.")
        raise RuntimeError("MONGO_URI is not configured.")

    if not database_name:
        logger.critical("DATABASE_NAME not found in environment variables.")
        raise RuntimeError("DATABASE_NAME is not configured.")

    try:
        # 2️⃣ Create MongoClient
        _client = MongoClient(mongo_uri)

        # 3️⃣ Connect to database
        _database = _client[database_name]

        # 4️⃣ Test connection with ping
        _client.admin.command("ping")

        logger.info("Successfully connected to MongoDB Atlas.")

    except Exception as e:
        logger.critical(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise RuntimeError("Database connection failed.") from e


def get_database() -> Database:
    """
    Retrieve active database instance.
    """

    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")

    return _database


def close_mongo_connection() -> None:
    """
    Close MongoDB connection on application shutdown.
    """

    global _client

    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")
