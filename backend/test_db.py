#!/usr/bin/env python3
"""
Script de test pour vérifier l'enregistrement et la lecture en base de données
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

def test_database():
    """Test de l'enregistrement et de la lecture en base"""
    
    # Connexion MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client.apocal_db
    
    print("🔍 Test de la base de données MongoDB...")
    
    # Test 1: Vérifier la connexion
    try:
        client.admin.command('ping')
        print("✅ Connexion MongoDB réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return
    
    # Test 2: Test d'enregistrement d'un utilisateur
    print("\n📝 Test d'enregistrement utilisateur...")
    try:
        test_user = {
            "email": "test@example.com",
            "password": "hashed_password",
            "firstName": "Test",
            "lastName": "User",
            "createdAt": datetime.utcnow()
        }
        
        result = db.users.insert_one(test_user)
        print(f"✅ Utilisateur enregistré avec l'ID: {result.inserted_id}")
        
        # Test 3: Test de lecture utilisateur
        user = db.users.find_one({"_id": result.inserted_id})
        if user:
            print(f"✅ Utilisateur lu: {user['email']}")
        else:
            print("❌ Impossible de lire l'utilisateur")
        
        # Nettoyer le test
        db.users.delete_one({"_id": result.inserted_id})
        print("🧹 Utilisateur de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test utilisateur: {e}")
    
    # Test 4: Test d'enregistrement d'une analyse
    print("\n📄 Test d'enregistrement analyse...")
    try:
        test_analysis = {
            "filename": "test_document.pdf",
            "summary": "Ceci est un résumé de test",
            "keyPoints": ["Point 1", "Point 2", "Point 3"],
            "actions": ["Action 1", "Action 2"],
            "uploadDate": datetime.utcnow(),
            "originalText": "Texte original de test"
        }
        
        result = db.analyses.insert_one(test_analysis)
        print(f"✅ Analyse enregistrée avec l'ID: {result.inserted_id}")
        
        # Test 5: Test de lecture analyse
        analysis = db.analyses.find_one({"_id": result.inserted_id})
        if analysis:
            print(f"✅ Analyse lue: {analysis['filename']}")
            print(f"   - Résumé: {analysis['summary'][:50]}...")
            print(f"   - Points clés: {len(analysis['keyPoints'])}")
            print(f"   - Actions: {len(analysis['actions'])}")
        else:
            print("❌ Impossible de lire l'analyse")
        
        # Nettoyer le test
        db.analyses.delete_one({"_id": result.inserted_id})
        print("🧹 Analyse de test supprimée")
        
    except Exception as e:
        print(f"❌ Erreur lors du test analyse: {e}")
    
    # Test 6: Test de requête avec filtre utilisateur
    print("\n🔍 Test de requête avec filtre utilisateur...")
    try:
        # Créer un utilisateur de test
        test_user = {
            "email": "filter@example.com",
            "password": "hashed_password",
            "firstName": "Filter",
            "lastName": "User",
            "createdAt": datetime.utcnow()
        }
        user_result = db.users.insert_one(test_user)
        user_id = user_result.inserted_id
        
        # Créer des analyses avec et sans utilisateur
        analysis_with_user = {
            "filename": "user_document.pdf",
            "summary": "Document utilisateur",
            "keyPoints": ["Point utilisateur"],
            "actions": ["Action utilisateur"],
            "uploadDate": datetime.utcnow(),
            "userId": user_id
        }
        
        analysis_without_user = {
            "filename": "public_document.pdf",
            "summary": "Document public",
            "keyPoints": ["Point public"],
            "actions": ["Action public"],
            "uploadDate": datetime.utcnow()
        }
        
        db.analyses.insert_one(analysis_with_user)
        db.analyses.insert_one(analysis_without_user)
        
        # Tester la requête avec filtre utilisateur
        user_analyses = list(db.analyses.find({"userId": user_id}))
        print(f"✅ Analyses de l'utilisateur: {len(user_analyses)} trouvées")
        
        # Tester la requête sans filtre (analyses publiques)
        public_analyses = list(db.analyses.find({"userId": {"$exists": False}}))
        print(f"✅ Analyses publiques: {len(public_analyses)} trouvées")
        
        # Nettoyer
        db.users.delete_one({"_id": user_id})
        db.analyses.delete_many({"userId": user_id})
        db.analyses.delete_many({"filename": "public_document.pdf"})
        print("🧹 Données de test supprimées")
        
    except Exception as e:
        print(f"❌ Erreur lors du test de filtrage: {e}")
    
    print("\n🎉 Tests terminés !")
    client.close()

if __name__ == "__main__":
    test_database() 