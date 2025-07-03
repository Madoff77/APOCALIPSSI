from groq import Groq
import os
import json
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv(dotenv_path='../.env')

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

# Initialiser le client Groq avec gestion d'erreur
try:
    if not GROQ_API_KEY:
        print("GROQ_API_KEY non trouvée dans les variables d'environnement")
        groq_client = None
    else:
        groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Erreur lors de l'initialisation de Groq: {e}")
    groq_client = None

def check_ollama_available():
    """Vérifier si Ollama est disponible localement"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def summarize_with_ollama(text):
    """Utiliser Ollama pour la synthèse de texte"""
    try:
        # Limiter le texte pour éviter de dépasser les limites
        max_chars = 12000  # Modèles locaux ont généralement moins de tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        system_prompt = """Tu es un assistant expert en analyse de documents. 
Analyse le document fourni et retourne une réponse en JSON avec exactement cette structure:
{
    "summary": "Un résumé détaillé du document en français",
    "keyPoints": ["Point clé 1", "Point clé 2", "Point clé 3"],
    "actions": ["Action recommandée 1", "Action recommandée 2", "Action recommandée 3"]
}

Assure-toi que:
- Le résumé soit complet et informatif (200-300 mots)
- Les points clés soient les éléments les plus importants du document
- Les actions soient des recommandations concrètes et réalisables
- La réponse soit uniquement en JSON valide, sans autre texte"""

        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyse ce document:\n\n{text}"}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1500
            }
        }

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Erreur Ollama: {response.status_code}")

        result = response.json()
        content = result['message']['content'].strip()
        
        try:
            # Nettoyer le contenu des backticks et du markdown
            cleaned_content = content.strip()
            
            # Enlever les backticks et le label json si présents
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]  # Enlever ```json
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]  # Enlever ```
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]  # Enlever ```
            
            cleaned_content = cleaned_content.strip()
            
            # Essayer de parser le JSON
            parsed_result = json.loads(cleaned_content)
            
            # Valider la structure
            if not all(key in parsed_result for key in ["summary", "keyPoints", "actions"]):
                raise ValueError("Structure JSON incomplète")
                
            return parsed_result
            
        except json.JSONDecodeError as e:
            # Si le parsing JSON échoue, essayer d'extraire le contenu utile
            print(f"Erreur de parsing JSON Ollama: {e}")
            print(f"Contenu reçu: {content}")
            
            # Essayer d'extraire le JSON même s'il y a du texte autour
            import re
            json_pattern = r'\{.*"summary".*"keyPoints".*"actions".*\}'
            json_match = re.search(json_pattern, content, re.DOTALL)
            
            if json_match:
                try:
                    extracted_json = json_match.group(0)
                    parsed_result = json.loads(extracted_json)
                    if all(key in parsed_result for key in ["summary", "keyPoints", "actions"]):
                        print("JSON extrait avec succès malgré le formatage")
                        return parsed_result
                except:
                    pass
            
            # Si tout échoue, créer une structure par défaut
            return {
                "summary": content if content else "Résumé non disponible (Ollama)",
                "keyPoints": ["Analyse en cours...", "Points clés à identifier", "Données en traitement"],
                "actions": ["Vérifier le document", "Réessayer l'analyse", "Contacter le support si nécessaire"]
            }
    
    except Exception as e:
        print(f"Erreur lors de l'appel à Ollama: {e}")
        return {
            "summary": f"Erreur lors de l'analyse (Ollama): {str(e)}",
            "keyPoints": ["Document reçu", "Erreur technique rencontrée", "Analyse interrompue"],
            "actions": ["Vérifier qu'Ollama est installé et en cours d'exécution", "Réessayer dans quelques minutes", "Basculer vers l'API externe"]
        }

def summarize_text(text):
    """Fonction principale de synthèse avec fallback automatique"""
    
    # Si on a configuré l'utilisation du modèle local et qu'Ollama est disponible
    if USE_LOCAL_MODEL and check_ollama_available():
        print("Utilisation du modèle local Ollama")
        return summarize_with_ollama(text)
    
    # Fallback vers Groq si disponible
    if groq_client is not None:
        print("Utilisation de l'API Groq externe")
        return summarize_with_groq(text)
    
    # Si aucun service n'est disponible
    return {
        "summary": "Erreur: Aucun service LLM disponible",
        "keyPoints": ["Configuration requise", "Vérifier Ollama ou Groq", "Vérifiez .env"],
        "actions": ["Installer Ollama localement", "Configurer GROQ_API_KEY", "Redémarrer l'application"]
    }

def summarize_with_groq(text):
    """Utiliser Groq pour la synthèse de texte (fonction existante)"""
    if groq_client is None:
        return {
            "summary": "Erreur: Client Groq non initialisé",
            "keyPoints": ["Configuration requise", "Clé API manquante", "Vérifiez .env"],
            "actions": ["Vérifier GROQ_API_KEY dans .env", "Redémarrer l'application", "Contacter le support"]
        }
    
    try:
        # Limiter le texte pour éviter de dépasser les limites de tokens
        max_chars = 15000  # Groq peut gérer plus de texte
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        # Prompt structuré pour obtenir le format attendu par le frontend
        system_prompt = """Tu es un assistant expert en analyse de documents. 
Analyse le document fourni et retourne une réponse en JSON avec exactement cette structure:
{
    "summary": "Un résumé détaillé du document en français",
    "keyPoints": ["Point clé 1", "Point clé 2", "Point clé 3"],
    "actions": ["Action recommandée 1", "Action recommandée 2", "Action recommandée 3"]
}

Assure-toi que:
- Le résumé soit complet et informatif (200-300 mots)
- Les points clés soient les éléments les plus importants du document
- Les actions soient des recommandations concrètes et réalisables
- La réponse soit uniquement en JSON valide, sans autre texte"""

        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # Modèle Groq pour l'analyse de texte
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyse ce document:\n\n{text}"}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        # Extraire et parser la réponse JSON
        content = response.choices[0].message.content.strip()
        
        try:
            # Essayer de parser le JSON directement
            result = json.loads(content)
            
            # Valider la structure
            if not all(key in result for key in ["summary", "keyPoints", "actions"]):
                raise ValueError("Structure JSON incomplète")
                
            return result
            
        except json.JSONDecodeError:
            # Si le parsing JSON échoue, créer une structure par défaut
            print(f"Erreur de parsing JSON. Contenu reçu: {content}")
            return {
                "summary": content if content else "Résumé non disponible",
                "keyPoints": ["Analyse en cours...", "Points clés à identifier", "Données en traitement"],
                "actions": ["Vérifier le document", "Réessayer l'analyse", "Contacter le support si nécessaire"]
            }
    
    except Exception as e:
        print(f"Erreur lors de l'appel à Groq: {e}")
        # Retourner une structure par défaut en cas d'erreur
        return {
            "summary": f"Erreur lors de l'analyse: {str(e)}",
            "keyPoints": ["Document reçu", "Erreur technique rencontrée", "Analyse interrompue"],
            "actions": ["Vérifier votre clé API Groq", "Réessayer dans quelques minutes", "Contacter le support technique"]
        }
