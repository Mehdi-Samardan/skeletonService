from pymongo.errors import DuplicateKeyError

from app.core.database import get_database
from app.utils.logger import logger
from app.utils.mongo_serializer import serialize_mongo_document

# Repository for managing skeleton PPTX metadata in MongoDB. 
# Provides methods to find existing skeletons by content hash or slide hashes, and to insert new skeleton records.
class SkeletonRepository:
    def __init__(self) -> None:
        self.collection = get_database()["skeletons"]
        logger.info("SkeletonRepository initialized.")
        logger.info("MongoDB collection 'skeletons' ready for queries.")

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

    def find_by_slide_hashes(
        self, slides: list[str], slide_hashes: dict[str, str]
    ) -> dict | None:
        """Return the skeleton document matching the exact slide order and per-slide hashes, or None."""
        query: dict = {
            "slides": slides,
            **{f"slide_hashes.{name}": h for name, h in slide_hashes.items()},
        }
        doc = self.collection.find_one(query)
        if doc:
            logger.info(f"[Repo] cache hit for slide_hashes: {list(slide_hashes.keys())}")
        else:
            logger.info(f"[Repo] no record for slide_hashes: {list(slide_hashes.keys())}")
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
            existing = self.collection.find_one(
                {"skeleton_hash": data.get("skeleton_hash")}
            )
            return self._serialize(existing) or data
