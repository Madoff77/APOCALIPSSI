# Installation et Configuration du Backend APOCALIPSSI

## Prérequis

- Python 3.8 ou supérieur
- MongoDB (local ou Atlas)
- Clé API Groq (gratuite)

## Installation

1. **Installer les dépendances Python :**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configurer les variables d'environnement :**
   
   Créez un fichier `.env` dans le dossier `backend/` avec le contenu suivant :
   ```
   # Configuration MongoDB
   MONGO_URI=mongodb://localhost:27017
   
   # Clé API Groq (remplacez par votre vraie clé)
   GROQ_API_KEY=gsk-your-groq-api-key-here
   
   # Configuration Flask
   FLASK_ENV=development
   FLASK_DEBUG=True
   
   # Port du serveur
   PORT=5000
   ```

3. **Démarrer MongoDB :**
   - Si vous utilisez MongoDB local, démarrez le service MongoDB
   - Si vous utilisez MongoDB Atlas, utilisez l'URI de connexion Atlas dans `MONGO_URI`

4. **Obtenir une clé API Groq :**
   - Allez sur https://console.groq.com/
   - Créez un compte gratuit
   - Générez une clé API dans la section "API Keys"
   - Remplacez `gsk-your-groq-api-key-here` par votre vraie clé dans le fichier `.env`

## Démarrage

```bash
cd backend
python app.py
```

Le serveur démarrera sur http://localhost:5000

## Routes API disponibles

- `GET /api/health` - Test de fonctionnement de l'API
- `POST /api/analysis/upload` - Upload et analyse d'un PDF
- `GET /api/analysis/history` - Récupération de l'historique des analyses

## Structure des données

### Upload de PDF
**Request:** FormData avec un champ 'file' contenant le PDF

**Response:**
```json
{
  "summary": "Résumé du document...",
  "keyPoints": ["Point 1", "Point 2", "Point 3"],
  "actions": ["Action 1", "Action 2", "Action 3"]
}
```

### Historique des analyses
**Response:**
```json
[
  {
    "id": "unique_id",
    "fileName": "document.pdf",
    "summary": "Résumé...",
    "keyPoints": [...],
    "actions": [...],
    "date": "2024-01-01T00:00:00Z"
  }
]
```

## Dépannage

1. **Erreur MongoDB :** Vérifiez que MongoDB est démarré et accessible
2. **Erreur Groq :** Vérifiez que votre clé API est valide et que vous respectez les limites de taux
3. **Erreur PDF :** Assurez-vous que le fichier est un PDF valide et contient du texte extractible

## Avantages de Groq

- **Gratuit** : Quota généreux sans carte de crédit requise
- **Ultra rapide** : Inférence beaucoup plus rapide qu'OpenAI
- **Modèles performants** : Llama-3.1-70B, Mixtral-8x7B, etc.
- **API simple** : Compatible avec l'API OpenAI 