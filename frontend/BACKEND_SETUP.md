# Configuration Backend - ComplySummarize

Ce document décrit comment configurer l'application frontend pour fonctionner avec un backend réel.

## Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration de l'API Backend
VITE_API_BASE_URL=http://localhost:3001/api

# Configuration de développement  
VITE_APP_ENV=development
```

## Endpoints API requis

Le backend doit implémenter les endpoints suivants :

### Authentification

#### POST `/auth/login`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Réponse attendue :
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com", 
    "firstName": "John",
    "lastName": "Doe",
    "createdAt": "2024-01-01T00:00:00.000Z"
  },
  "token": "jwt_token_here"
}
```

#### POST `/auth/register`
```json
{
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John", 
  "lastName": "Doe"
}
```

Réponse attendue : même format que `/auth/login`

#### GET `/auth/verify`
Headers : `Authorization: Bearer <token>`

Réponse attendue :
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "firstName": "John", 
  "lastName": "Doe",
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

#### PUT `/auth/profile`
Headers : `Authorization: Bearer <token>`
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "newemail@example.com"
}
```

Réponse attendue : objet utilisateur mis à jour

### Analyse de documents

#### POST `/analysis/upload`
Headers : `Authorization: Bearer <token>` (optionnel)
Body : FormData avec le fichier PDF

Réponse attendue :
```json
{
  "summary": "Résumé du document...",
  "keyPoints": [
    "Point clé 1",
    "Point clé 2"
  ],
  "actions": [
    "Action recommandée 1", 
    "Action recommandée 2"
  ]
}
```

#### GET `/analysis/history`
Headers : `Authorization: Bearer <token>`

Réponse attendue :
```json
[
  {
    "id": "analysis_id",
    "fileName": "document.pdf",
    "uploadDate": "2024-01-01T00:00:00.000Z",
    "summary": "Résumé...",
    "keyPoints": ["Point 1"],
    "actions": ["Action 1"]
  }
]
```

#### DELETE `/analysis/:id`
Headers : `Authorization: Bearer <token>`

Réponse attendue : 204 No Content

## Gestion des erreurs

Toutes les réponses d'erreur doivent suivre ce format :
```json
{
  "message": "Description de l'erreur",
  "code": "ERROR_CODE", // optionnel
  "details": {} // optionnel
}
```

## CORS

Le backend doit être configuré pour accepter les requêtes CORS depuis l'origine du frontend (par exemple `http://localhost:5173` en développement).

## Authentification

L'application utilise l'authentification JWT. Les tokens sont stockés dans le localStorage du navigateur et envoyés dans l'en-tête `Authorization: Bearer <token>`.

## Démarrage

1. Configurez les variables d'environnement
2. Démarrez votre backend sur le port configuré (3001 par défaut)
3. Démarrez l'application frontend avec `npm run dev`

L'application tentera automatiquement de se connecter au backend. Si le backend n'est pas disponible, les appels API échoueront avec des messages d'erreur appropriés. 