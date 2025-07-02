from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from bson import ObjectId
import json

# Import des modules locaux
from pdf_utils import extract_text_from_pdf
from llm_summary import summarize_text
from auth import create_user, authenticate_user, generate_token, token_required

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client.apocal_db

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

# Route de test pour vérifier que l'API fonctionne
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API fonctionne correctement"})

# Routes d'authentification
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['email', 'password', 'firstName', 'lastName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Le champ {field} est requis"}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        firstName = data['firstName'].strip()
        lastName = data['lastName'].strip()
        
        # Validation basique
        if len(password) < 6:
            return jsonify({"error": "Le mot de passe doit contenir au moins 6 caractères"}), 400
        
        if '@' not in email:
            return jsonify({"error": "Format d'email invalide"}), 400
        
        # Créer l'utilisateur
        user_data = create_user(email, password, firstName, lastName, db)
        
        # Générer le token
        token = generate_token(str(user_data['_id']), email)
        
        # Formater la réponse
        response_data = {
            "user": {
                "id": str(user_data['_id']),
                "email": user_data['email'],
                "firstName": user_data['firstName'],
                "lastName": user_data['lastName'],
                "createdAt": user_data['createdAt'].isoformat()
            },
            "token": token
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validation des données
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email et mot de passe requis"}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Authentifier l'utilisateur
        user_data = authenticate_user(email, password, db)
        
        # Générer le token
        token = generate_token(user_data['id'], email)
        
        # Formater la réponse
        response_data = {
            "user": {
                "id": user_data['id'],
                "email": user_data['email'],
                "firstName": user_data['firstName'],
                "lastName": user_data['lastName'],
                "createdAt": user_data['createdAt'].isoformat()
            },
            "token": token
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token_route():
    """Vérifier et retourner les informations de l'utilisateur connecté"""
    try:
        user = request.current_user
        
        # Récupérer les données complètes depuis la base
        user_data = db.users.find_one({'_id': ObjectId(user['id'])})
        
        if not user_data:
            return jsonify({"error": "Utilisateur non trouvé"}), 404
        
        response_data = {
            "id": str(user_data['_id']),
            "email": user_data['email'],
            "firstName": user_data['firstName'],
            "lastName": user_data['lastName'],
            "createdAt": user_data['createdAt'].isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_profile():
    """Mettre à jour le profil de l'utilisateur"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Champs autorisés à modifier
        allowed_fields = ['firstName', 'lastName']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field].strip()
        
        if not update_data:
            return jsonify({"error": "Aucune donnée à mettre à jour"}), 400
        
        # Mettre à jour dans la base
        result = db.users.update_one(
            {'_id': ObjectId(user['id'])},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Aucune modification effectuée"}), 400
        
        # Récupérer les données mises à jour
        updated_user = db.users.find_one({'_id': ObjectId(user['id'])})
        
        response_data = {
            "id": str(updated_user['_id']),
            "email": updated_user['email'],
            "firstName": updated_user['firstName'],
            "lastName": updated_user['lastName'],
            "createdAt": updated_user['createdAt'].isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour upload et analyse de PDF
@app.route('/api/analysis/upload', methods=['POST'])
def upload_and_analyze():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Nom de fichier vide"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Seuls les fichiers PDF sont acceptés"}), 400

        # Extraire le texte du PDF
        try:
            text = extract_text_from_pdf(file)
            if not text.strip():
                return jsonify({"error": "Le PDF semble vide ou le texte n'a pas pu être extrait"}), 400
        except Exception as e:
            return jsonify({"error": f"Erreur lors de l'extraction du texte: {str(e)}"}), 400

        # Analyser avec l'IA
        try:
            analysis_result = summarize_text(text)
        except Exception as e:
            return jsonify({"error": f"Erreur lors de l'analyse IA: {str(e)}"}), 500

        # Structurer la réponse selon les attentes du frontend
        result = {
            "summary": analysis_result.get("summary", ""),
            "keyPoints": analysis_result.get("keyPoints", []),
            "actions": analysis_result.get("actions", [])
        }

        # Sauvegarder dans MongoDB
        try:
            doc = {
                "filename": file.filename,
                "summary": result["summary"],
                "keyPoints": result["keyPoints"],
                "actions": result["actions"],
                "uploadDate": datetime.utcnow(),
                "originalText": text[:1000]  # Garder juste un extrait
            }
            
            # Associer à l'utilisateur si connecté
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    from auth import verify_token
                    token = auth_header.split(" ")[1]
                    payload = verify_token(token)
                    doc["userId"] = ObjectId(payload['user_id'])
                except:
                    pass  # Si le token est invalide, on sauvegarde sans utilisateur
            
            db.analyses.insert_one(doc)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            # On continue même si la sauvegarde échoue

        return jsonify(result)

    except Exception as e:
        print(f"Erreur générale: {e}")
        return jsonify({"error": "Une erreur interne est survenue"}), 500

# Route pour récupérer l'historique des analyses
@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    try:
        # Vérifier si l'utilisateur est connecté
        auth_header = request.headers.get('Authorization')
        user_id = None
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                user_id = ObjectId(payload['user_id'])
            except:
                pass  # Token invalide, on récupère l'historique public
        
        # Construire la requête
        query = {}
        if user_id:
            query["userId"] = user_id
        
        # Récupérer les analyses
        analyses = list(db.analyses.find(query, {
            'originalText': 0  # Exclure le texte original pour alléger la réponse
        }).sort('uploadDate', -1).limit(20))
        
        # Formatter pour le frontend (correspondance exacte avec AnalysisHistory)
        formatted_analyses = []
        for analysis in analyses:
            formatted_analyses.append({
                "id": str(analysis["_id"]),
                "fileName": analysis["filename"],
                "uploadDate": analysis["uploadDate"].isoformat() if analysis.get("uploadDate") else "",
                "summary": analysis["summary"],
                "keyPoints": analysis["keyPoints"],
                "actions": analysis["actions"]
            })
        
        return jsonify(formatted_analyses)
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique: {e}")
        return jsonify([])

if __name__ == '__main__':
    print("🚀 Démarrage du serveur backend APOCALIPSSI...")
    print(f"🔗 MongoDB URI: {mongo_uri}")
    app.run(debug=True, host='0.0.0.0', port=5000)
