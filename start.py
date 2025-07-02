#!/usr/bin/env python3
"""
Script de démarrage simple pour APOCALIPSSI
Lance automatiquement le backend et le frontend
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Exécuter une commande de manière simple"""
    try:
        subprocess.run(command, cwd=cwd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_env():
    """Vérifier et créer le fichier .env si nécessaire"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Création du fichier .env...")
        env_content = """# Configuration de l'API Groq
GROQ_API_KEY=your_groq_api_key_here

# Configuration MongoDB (optionnel)
MONGODB_URI=mongodb://localhost:27017/apocalipssi

# Configuration Flask (optionnel)
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("Fichier .env créé")

def main():
    """Fonction principale simplifiée"""
    print("APOCALIPSSI - Démarrage automatique")
    print("=" * 40)
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("Python 3.8+ requis")
        sys.exit(1)
    print(f"Python {sys.version.split()[0]} détecté")
    
    # Vérifier et créer .env
    check_env()
    
    # Installer les dépendances backend
    print("\nInstallation des dépendances backend...")
    if not run_command("pip install -r backend/requirements.txt"):
        print("Erreur lors de l'installation des dépendances backend")
        sys.exit(1)
    print("Dépendances backend installées")
    
    # Installer les dépendances frontend
    print("\nInstallation des dépendances frontend...")
    if not run_command("npm install", cwd="frontend"):
        print("Erreur lors de l'installation des dépendances frontend")
        print("   Assurez-vous que Node.js est installé: https://nodejs.org/")
        sys.exit(1)
    print("Dépendances frontend installées")
    
    # Démarrer le backend
    print("\nDémarrage du backend...")
    backend_process = subprocess.Popen([sys.executable, "app.py"], cwd="backend")
    print("Backend démarré sur http://localhost:5000")
    
    # Attendre un peu
    time.sleep(2)
    
    # Démarrer le frontend
    print("\nDémarrage du frontend...")
    frontend_process = subprocess.Popen("npm run dev", cwd="frontend", shell=True)
    print("Frontend démarré sur http://localhost:5173")
    
    print("\n" + "=" * 40)
    print("Application APOCALIPSSI démarrée !")
    print("\n Accès:")
    print("   Frontend: http://localhost:5173")
    print("   Backend:  http://localhost:5000")
    
    try:
        # Attendre que l'un des processus se termine
        while backend_process.poll() is None and frontend_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main() 