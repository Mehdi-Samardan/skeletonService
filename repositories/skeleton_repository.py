from database import get_database


class SkeletonRepository:
    def __init__(self):
        self.collection = get_database()["skeletons"]

    def _serialize(self, document):
        if not document:
            return None
        document["_id"] = str(document["_id"])
        return document

    def find_by_hash(self, skeleton_hash: str):
        doc = self.collection.find_one({"skeleton_hash": skeleton_hash})
        return self._serialize(doc)

    def insert(self, data: dict):
        result = self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data
