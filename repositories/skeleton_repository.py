# 1.	skeleton_repository.py oluşturmak
# 2.	get_database() üzerinden DB almak
# 3.	skeleton_layouts collection referansını tanımlamak

from pymongo.collection import Collection
from database import get_database
from utils.logger import logger


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

            return document

        except Exception as e:
            logger.error(f"Database error during get_by_hash: {e}", exc_info=True)
            raise
