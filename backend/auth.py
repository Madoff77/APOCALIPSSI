import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Configuration JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24 * 60 * 60  # 24 heures en secondes

def hash_password(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe avec bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id: str, email: str) -> str:
    """Générer un token JWT"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Vérifier et décoder un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expiré")
    except jwt.InvalidTokenError:
        raise Exception("Token invalide")

def token_required(f):
    """Décorateur pour protéger les routes avec authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token depuis les headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token manquant'}), 401
        
        if not token:
            return jsonify({'message': 'Token requis'}), 401
        
        try:
            # Vérifier le token
            payload = verify_token(token)
            current_user_id = payload['user_id']
            
            # Récupérer l'utilisateur depuis la base de données
            from app import db
            user = db.users.find_one({'_id': ObjectId(current_user_id)})
            
            if not user:
                return jsonify({'message': 'Utilisateur non trouvé'}), 401
            
            # Ajouter l'utilisateur à la requête
            request.current_user = {
                'id': str(user['_id']),
                'email': user['email'],
                'firstName': user['firstName'],
                'lastName': user['lastName']
            }
            
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def create_user(email: str, password: str, firstName: str, lastName: str, db):
    """Créer un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = db.users.find_one({'email': email})
    if existing_user:
        raise Exception("Un utilisateur avec cet email existe déjà")
    
    # Hasher le mot de passe
    hashed_password = hash_password(password)
    
    # Créer l'utilisateur
    user_data = {
        'email': email,
        'password': hashed_password,
        'firstName': firstName,
        'lastName': lastName,
        'createdAt': datetime.utcnow()
    }
    
    result = db.users.insert_one(user_data)
    
    # Retourner l'utilisateur sans le mot de passe
    user_data['_id'] = result.inserted_id
    user_data.pop('password', None)
    
    return user_data

def authenticate_user(email: str, password: str, db):
    """Authentifier un utilisateur"""
    # Trouver l'utilisateur par email
    user = db.users.find_one({'email': email})
    if not user:
        raise Exception("Email ou mot de passe incorrect")
    
    # Vérifier le mot de passe
    if not verify_password(password, user['password']):
        raise Exception("Email ou mot de passe incorrect")
    
    # Retourner l'utilisateur sans le mot de passe
    user_data = {
        'id': str(user['_id']),
        'email': user['email'],
        'firstName': user['firstName'],
        'lastName': user['lastName'],
        'createdAt': user['createdAt']
    }
    
    return user_data 