from groq import Groq
import os
import json
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Initialiser le client Groq avec gestion d'erreur
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY non trouvée dans les variables d'environnement")
    client = Groq(api_key=api_key)
except Exception as e:
    print(f"Erreur lors de l'initialisation de Groq: {e}")
    client = None

def summarize_text(text):
    if client is None:
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

        response = client.chat.completions.create(
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
