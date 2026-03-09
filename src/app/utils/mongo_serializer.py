from datetime import datetime


def serialize_mongo_document(document: dict) -> dict:
    """Convert a MongoDB document into a JSON-serializable dict."""
    if not document:
        return document

    document["_id"] = str(document["_id"])

    if isinstance(document.get("created_at"), datetime):
        document["created_at"] = document["created_at"].isoformat()

    return document
