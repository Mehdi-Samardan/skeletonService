from pymongo.collection import Collection
from database import get_database
from utils.logger import logger
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from utils.mongo_serializer import serialize_mongo_document


class SkeletonRepository:
    def __init__(self) -> None:
        """
        Initialize repository with Mongo collection reference.
        """

        database = get_database()
        self.collection: Collection = database["skeleton_layouts"]

        logger.info(
            "SkeletonRepository initialized successfully. (skeleton_repository.py)"
        )

    def get_by_hash(self, hash_value: str) -> dict | None:
        """
        Retrieve a skeleton document by its hash.

        :param hash_value: Deterministic hash of layout combination
        :return: Document if found, otherwise None
        """

        try:
            document = self.collection.find_one({"hash": hash_value})

            if document:
                logger.info(f"Skeleton found for hash: {hash_value}")
            else:
                logger.info(f"No skeleton found for hash: {hash_value}")

            return serialize_mongo_document(document) if document else None

        except Exception as e:
            logger.error(f"Database error during get_by_hash: {e}", exc_info=True)
            raise

    def insert_layout(self, document: dict) -> dict:
        """
        Insert a new skeleton document into MongoDB.
        If a document with the same hash already exists,
        return the existing document (idempotent behavior).
        """

        try:
            # Timestamp ekle
            document["created_at"] = datetime.utcnow()

            # Insert dene
            result = self.collection.insert_one(document)

            logger.info(f"Skeleton inserted with id: {result.inserted_id}")

            return serialize_mongo_document(document)

        except DuplicateKeyError:
            logger.warning(
                f"Duplicate detected for hash: {document.get('hash')}. Fetching existing document."
            )

            # Duplicate varsa mevcut kaydı getir
            existing = self.collection.find_one({"hash": document.get("hash")})

            if existing is None:
                return document
            return serialize_mongo_document(existing)

        except Exception as e:
            logger.error(f"Database error during insert_layout: {e}", exc_info=True)
            raise

    # Optional: Method to retrieve all layouts for testing purposes
    def get_all_layouts(self) -> list[dict]:
        """
        Retrieve all saved layout documents.

        :return: List of layout documents
        """
        try:
            layouts = list(self.collection.find())
            logger.info(f"Retrieved {len(layouts)} layouts from database.")
            return layouts

        except Exception as e:
            logger.error(f"Database error during get_all_layouts: {e}", exc_info=True)
            raise
