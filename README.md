# APOCALIPSSI - Analyse de documents IA

Application web pour analyser des documents PDF avec l'intelligence artificielle.

## Démarrage rapide

### Prérequis
- Python 3.8+ (télécharger depuis (https://python.org))
- Node.js** (télécharger depuis (https://nodejs.org))

### Installation et lancement

1. Cloner le projet
   Ouvrir un terminal et taper : 
   git clone [URL_DU_REPO]
   cd APOCALIPSSI

2. Configurer l'API
   - Ouvrir le fichier `backend/.env`
   - Remplacer `your_groq_api_key_here` par votre clé API Groq
   - Obtenir une clé gratuite sur (https://console.groq.com)

3. Lancer l'application
   Ouvrir le terminal et taper : 
   python start.py

4. Accéder à l'application
   - Frontend: http://localhost:5173
   - Backend: http://localhost:5000

## Fonctionnalités

- Upload de PDF : Glissez-déposez vos documents
- Analyse IA : Résumé automatique avec Groq
- Points clés : Extraction des informations importantes
- Actions recommandées : Suggestions d'actions à entreprendre
- Authentification : Inscription et connexion utilisateurs
- Historique : Sauvegarde de vos analyses

## Structure du projet

APOCALIPSSI/
├── backend/          # Serveur Flask + API
├── frontend/         # Interface React/TypeScript
├── start.py          # Script de démarrage automatique
└── README.md         # Ce fichier

## Dépannage

### Erreur "npm non trouvé"
- Réinstallez Node.js depuis (https://nodejs.org)
- Redémarrez votre terminal

### Erreur "pip non trouvé"
- Réinstallez Python depuis (https://python.org)
- Cochez "Add Python to PATH" lors de l'installation

### Erreur API Groq
- Vérifiez votre clé API dans `backend/.env`
- Assurez-vous d'avoir des crédits sur votre compte Groq

## Support

En cas de problème, vérifiez :
1. Que Python 3.8+ et Node.js sont installés
2. Que votre clé API Groq est correcte
3. Que les ports 5000 et 5173 sont libres
# APOCALIPSSI