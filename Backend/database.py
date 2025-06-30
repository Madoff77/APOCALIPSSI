import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

from bson import ObjectId
from passlib.hash import bcrypt
from pymongo import MongoClient, ReturnDocument

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client[os.getenv("MONGODB_DB", "docbot")]
users_col = db["users"]
docs_col = db["documents"]

# ---------------------------- USERS ---------------------------------------

def create_user(email: str, password: str) -> Tuple[bool, str]:
    if users_col.find_one({"email": email}):
        return False, "email already registered"
    hash_ = bcrypt.hash(password)
    users_col.insert_one({
        "email": email,
        "password_hash": hash_,
        "created_at": datetime.utcnow(),
    })
    return True, "created"


def authenticate_user(email: str, password: str):
    user = users_col.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["password_hash"]):
        return None
    return user

# ------------------------- DOCUMENTS --------------------------------------

def insert_document(doc: Dict[str, Any]):
    result = docs_col.insert_one(doc)
    return result.inserted_id


def get_document(doc_id: ObjectId):
    return docs_col.find_one({"_id": doc_id})


def list_documents(user_id: ObjectId, page: int, limit: int) -> List[Dict[str, Any]]:
    skip = (page - 1) * limit
    cursor = (
        docs_col.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)