#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion à l'API Groq
"""

import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_connection():
    """Test de connexion à l'API Groq"""
    print("🔍 Test de connexion à l'API Groq...")
    print("=" * 50)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier si la clé API est présente
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERREUR: GROQ_API_KEY non trouvée dans le fichier .env")
        print("   Assurez-vous que votre fichier .env contient: GROQ_API_KEY=votre_clé_ici")
        return False
    
    print(f"✅ Clé API trouvée: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Initialiser le client Groq
        print("🔄 Initialisation du client Groq...")
        client = Groq(api_key=api_key)
        print("✅ Client Groq initialisé avec succès")
        
        # Test simple avec un prompt court (utiliser un modèle plus récent)
        print("🧪 Test d'un appel API simple...")
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Modèle pour l'analyse de texte
            messages=[
                {"role": "system", "content": "Tu es un assistant utile."},
                {"role": "user", "content": "Dis-moi simplement 'Bonjour, l'API Groq fonctionne !' en français."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        # Afficher la réponse
        content = response.choices[0].message.content.strip()
        print(f"✅ Réponse reçue: {content}")
        
        # Test avec le modèle utilisé dans l'application
        print("\n🧪 Test avec le modèle de l'application...")
        test_text = "Ceci est un document de test pour vérifier l'analyse IA."
        
        system_prompt = """Tu es un assistant expert en analyse de documents. 
Analyse le document fourni et retourne une réponse en JSON avec exactement cette structure:
{
    "summary": "Un résumé détaillé du document en français",
    "keyPoints": ["Point clé 1", "Point clé 2", "Point clé 3"],
    "actions": ["Action recommandée 1", "Action recommandée 2", "Action recommandée 3"]
}"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Modèle pour l'analyse de texte
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyse ce document:\n\n{test_text}"}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        print(f"✅ Réponse d'analyse reçue: {content[:100]}...")
        
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("   Votre clé API Groq fonctionne parfaitement.")
        print("   L'application devrait maintenant pouvoir analyser vos PDF.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors du test: {str(e)}")
        print("\n🔧 Solutions possibles:")
        print("   1. Vérifiez que votre clé API est correcte")
        print("   2. Vérifiez votre connexion internet")
        print("   3. Vérifiez que vous avez des crédits sur votre compte Groq")
        print("   4. Essayez de régénérer votre clé API")
        return False

if __name__ == "__main__":
    test_groq_connection() 