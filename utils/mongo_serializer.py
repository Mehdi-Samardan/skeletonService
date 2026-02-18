# Gemaakt Door AI
from bson import ObjectId
from datetime import datetime


def serialize_mongo_document(document: dict) -> dict:
    """
    Convert MongoDB document into JSON-serializable format.
    """

    if not document:
        return document

    document["_id"] = str(document["_id"])

    if isinstance(document.get("created_at"), datetime):
        document["created_at"] = document["created_at"].isoformat()

    return document
