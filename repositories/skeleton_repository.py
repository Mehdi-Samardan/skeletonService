from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from database import get_database
from utils.logger import logger
from utils.mongo_serializer import serialize_mongo_document


class SkeletonRepository:
    def __init__(self) -> None:
        self.collection = get_database()["skeletons"]
        logger.info("SkeletonRepository initialized.")

    def _serialize(self, document: dict | None) -> dict | None:
        return serialize_mongo_document(document) if document else None

    def find_by_hash(self, skeleton_hash: str) -> dict | None:
        """Return the skeleton document for the given hash, or None."""
        doc = self.collection.find_one({"skeleton_hash": skeleton_hash})
        if doc:
            logger.info(f"[Repo] cache hit for hash: {skeleton_hash[:16]}…")
        else:
            logger.info(f"[Repo] no record for hash: {skeleton_hash[:16]}…")
        return self._serialize(doc)

    def insert(self, data: dict) -> dict:
        """Insert a new skeleton record. Returns the inserted document."""
        try:
            result = self.collection.insert_one(data)
            data["_id"] = str(result.inserted_id)
            logger.info(f"[Repo] inserted skeleton: {result.inserted_id}")
            return data
        except DuplicateKeyError:
            logger.warning("[Repo] duplicate key — fetching existing record.")
            existing = self.collection.find_one({"skeleton_hash": data.get("skeleton_hash")})
            return self._serialize(existing) or data
