from pymongo import MongoClient
import os

client = None
db = None

def init_db():
    global client, db
    uri = "mongodb://localhost:27017"  # ou URI depuis MongoDB Compass
    client = MongoClient(uri)
    db = client["apocal_db"]
    print("✅ MongoDB connecté")
