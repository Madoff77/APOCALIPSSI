# Configuration du Frontend APOCALIPSSI

## Prérequis

- Node.js 18+ et npm
- Backend APOCALIPSSI démarré sur le port 5000

## Installation

1. **Installer les dépendances :**
   ```bash
   cd frontend
   npm install
   ```

2. **Configuration de l'environnement :**
   
   Créez un fichier `.env` dans le dossier `frontend/` :
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   VITE_APP_ENV=development
   ```

3. **Démarrer le serveur de développement :**
   ```bash
   npm run dev
   ```

L'application sera accessible sur http://localhost:5173

## Fonctionnalités disponibles

### Mode sans authentification
- Upload et analyse de documents PDF
- Affichage des résultats d'analyse (résumé, points clés, actions)
- Interface moderne avec thème sombre/clair
- Historique des analyses (partagé entre tous les utilisateurs)

### Interface utilisateur
- Design responsive avec Tailwind CSS
- Composants React TypeScript modernes
- Gestion d'état avec Context API
- Notifications d'erreur et de succès

## Structure du projet

```
frontend/src/
├── components/          # Composants React réutilisables
├── contexts/           # Contextes React (Auth, Theme)
├── hooks/              # Hooks personnalisés
├── services/           # Services API
├── types/              # Types TypeScript
├── config/             # Configuration de l'application
└── App.tsx             # Composant principal
```

## Configuration avancée

### Variables d'environnement disponibles

- `VITE_API_BASE_URL` : URL de base de l'API backend (défaut: http://localhost:5000/api)
- `VITE_APP_ENV` : Environnement de l'application (development/production)

### Personnalisation du thème

Le thème est configuré dans `tailwind.config.js` et peut être personnalisé selon vos besoins.

## Dépannage

1. **Erreur de connexion API :** Vérifiez que le backend est démarré sur le port 5000
2. **Erreur CORS :** Le backend Flask-CORS est configuré pour accepter toutes les origines en développement
3. **Erreur de build :** Vérifiez que toutes les dépendances sont installées avec `npm install`

## Développement

Pour contribuer au projet :

1. Utiliser TypeScript strict
2. Suivre les conventions ESLint configurées
3. Tester les composants avant de les committer
4. Utiliser les types définis dans `src/types/` 