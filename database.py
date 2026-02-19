import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

from utils.logger import logger


_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection.
    Called once at application startup.
    """

    global _client, _database

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
        _client = MongoClient(mongo_uri)
        _database = _client[database_name]
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


def get_server_information() -> dict:
    """
    Retrieve MongoDB server information.
    Useful for debugging connection issues.
    """

    if _client is None:
        logger.warning("MongoDB client not initialized. Cannot get server info.")
        return {}

    try:
        info = _client.server_info()
        logger.info("MongoDB server information retrieved successfully.")
        return info

    except Exception as e:
        logger.error(
            f"Failed to retrieve MongoDB server information: {e}", exc_info=True
        )
        return {}
