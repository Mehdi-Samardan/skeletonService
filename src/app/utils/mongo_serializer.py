from datetime import datetime

# from gridfs.grid_file import ObjectId


def serialize_mongo_document(document: dict) -> dict:
    """Convert a MongoDB document into a JSON-serializable dict."""
    if not document:
        return document

    document["_id"] = str(document["_id"])

    if isinstance(document.get("created_at"), datetime):
        document["created_at"] = document["created_at"].isoformat()

    return document


# MongoDB Document
# {
#   "_id": ObjectId("665f..."),        ──→  "_id": "665f..."
#   "created_at": datetime(2024,...),  ──→  "created_at": "2024-01-15T10:30:00"
#   "slides": ["a", "b"],              ──→   ✅
#   "skeleton_hash": "a3f9..."         ──→   ✅
# }
     