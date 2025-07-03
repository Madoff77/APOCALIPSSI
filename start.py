#!/usr/bin/env python3
"""
Script de démarrage simple pour APOCALIPSSI
Lance automatiquement le backend et le frontend avec configuration Ollama
"""

import os
import sys
import subprocess
import time
import platform
import requests
from pathlib import Path

def print_step(message):
    """Afficher une étape avec formatage"""
    print(f"\n{'='*50}")
    print(f"🔄 {message}")
    print(f"{'='*50}")

def print_success(message):
    """Afficher un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Afficher un message d'erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Afficher un message d'information"""
    print(f"ℹ️  {message}")

def run_command(command, cwd=None, shell=True, capture_output=False, timeout=300):
    """Exécuter une commande de manière simple avec timeout"""
    try:
        if capture_output:
            result = subprocess.run(command, cwd=cwd, shell=shell, check=True, 
                                  capture_output=True, text=True, timeout=timeout)
            return True, result.stdout
        else:
            subprocess.run(command, cwd=cwd, shell=shell, check=True, timeout=timeout)
            return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except subprocess.TimeoutExpired:
        return False, "Timeout - commande trop longue"

def check_ollama_installed():
    """Vérifier si Ollama est déjà installé"""
    # Essayer d'abord avec le PATH normal
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Si pas trouvé, essayer les chemins Windows courants
    import platform
    if platform.system().lower() == "windows":
        possible_paths = [
            r"C:\Program Files\Ollama\ollama.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Ollama\ollama.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama app.exe"
        ]
        
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                try:
                    result = subprocess.run([expanded_path, '--version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Ajouter au PATH pour cette session
                        ollama_dir = os.path.dirname(expanded_path)
                        os.environ['PATH'] = ollama_dir + os.pathsep + os.environ['PATH']
                        print_success(f"Ollama trouvé dans: {ollama_dir}")
                        return True
                except Exception as e:
                    print_info(f"Test du chemin {expanded_path}: {e}")
                    pass
    
    return False

def install_ollama():
    """Installer Ollama selon le système d'exploitation"""
    system = platform.system().lower()
    
    print_step("Installation d'Ollama")
    
    if system == "windows":
        print_info("Installation sur Windows...")
        # Essayer winget d'abord
        print_info("Tentative d'installation via winget (cela peut prendre quelques minutes)...")
        success, output = run_command("winget install Ollama.Ollama --accept-source-agreements --accept-package-agreements", capture_output=True)
        if success:
            print_success("Ollama installé via winget")
            return True
        else:
            print_info("Installation winget échouée ou prise trop de temps")
            print_info("Téléchargement manuel requis")
            print_info("1. Visitez: https://ollama.ai/download")
            print_info("2. Téléchargez et installez Ollama pour Windows")
            print_info("3. Redémarrez votre terminal après l'installation")
            input("Appuyez sur Entrée une fois Ollama installé...")
            return check_ollama_installed()
        
    elif system == "darwin":  # macOS
        print_info("Installation sur macOS...")
        success, _ = run_command("brew install ollama", capture_output=True)
        if success:
            print_success("Ollama installé via Homebrew")
            return True
        else:
            print_error("Erreur lors de l'installation via Homebrew")
            print_info("Téléchargez depuis: https://ollama.ai/download")
            return False
            
    elif system == "linux":
        print_info("Installation sur Linux...")
        success, _ = run_command("curl -fsSL https://ollama.ai/install.sh | sh", 
                                capture_output=True)
        if success:
            print_success("Ollama installé via le script officiel")
            return True
        else:
            print_error("Erreur lors de l'installation")
            print_info("Consultez: https://ollama.ai/download")
            return False
    
    return False

def start_ollama_service():
    """Démarrer le service Ollama"""
    print_step("Démarrage du service Ollama")
    
    try:
        # Démarrer Ollama en arrière-plan
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Attendre que le service soit prêt
        for i in range(30):  # Attendre max 30 secondes
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print_success("Service Ollama démarré avec succès")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"⏳ Attente du service Ollama... ({i+1}/30)")
        
        print_error("Timeout: Le service Ollama n'a pas démarré")
        return False
        
    except Exception as e:
        print_error(f"Erreur lors du démarrage: {e}")
        return False

def download_ollama_model(model_name="llama3.2:3b"):
    """Télécharger un modèle Ollama"""
    print_step(f"Téléchargement du modèle {model_name}")
    
    try:
        print_info("Téléchargement en cours... (cela peut prendre plusieurs minutes)")
        success, output = run_command(f"ollama pull {model_name}", capture_output=True)
        
        if success:
            print_success(f"Modèle {model_name} téléchargé avec succès")
            return True
        else:
            print_error(f"Erreur lors du téléchargement: {output}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def check_env():
    """Vérifier et créer le fichier .env si nécessaire"""
    env_file = Path(".env")
    if not env_file.exists():
        print_step("Création du fichier .env")
        env_content = """# Configuration APOCALIPSSI

# Base de données MongoDB
MONGO_URI=mongodb://localhost:27017

# API Groq (optionnel - fallback)
GROQ_API_KEY=your_groq_api_key_here

# Configuration Ollama (modèle local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
USE_LOCAL_MODEL=true

# Configuration JWT
JWT_SECRET_KEY=your_jwt_secret_key_here

# Configuration Flask (optionnel)
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print_success("Fichier .env créé avec configuration Ollama")
    else:
        # Vérifier si les configurations Ollama sont présentes
        content = env_file.read_text()
        ollama_configs = [
            "OLLAMA_BASE_URL=http://localhost:11434",
            "OLLAMA_MODEL=llama3.2:3b", 
            "USE_LOCAL_MODEL=true"
        ]
        
        missing_configs = []
        for config in ollama_configs:
            if config.split('=')[0] not in content:
                missing_configs.append(config)
        
        if missing_configs:
            print_info("Mise à jour du fichier .env avec les configurations Ollama")
            for config in missing_configs:
                content += f"\n{config}"
            env_file.write_text(content)
            print_success("Fichier .env mis à jour")

def setup_ollama():
    """Configuration complète d'Ollama"""
    print_step("Configuration d'Ollama")
    
    # Vérifier si Ollama est installé
    if not check_ollama_installed():
        print_info("Ollama n'est pas installé ou pas dans le PATH")
        print_info("Tentative d'installation...")
        if not install_ollama():
            print_error("Installation d'Ollama échouée")
            print_info("L'application continuera avec l'API externe si configurée")
            return False
        
        # Après installation, vérifier à nouveau
        if not check_ollama_installed():
            print_error("Ollama installé mais pas détecté")
            print_info("Redémarrez votre terminal et relancez le script")
            print_info("Ou ajoutez manuellement Ollama au PATH")
            print_info("L'application continuera avec l'API externe si configurée")
            return False
    else:
        print_success("Ollama est déjà installé et détecté")
    
    # Démarrer le service
    if not start_ollama_service():
        print_error("Impossible de démarrer le service Ollama")
        print_info("L'application continuera avec l'API externe si configurée")
        return False
    
    # Télécharger le modèle
    model_name = "llama3.2:3b"
    if not download_ollama_model(model_name):
        print_error("Téléchargement du modèle échoué")
        print_info("L'application continuera avec l'API externe si configurée")
        return False
    
    print_success("Configuration Ollama terminée avec succès")
    return True

def main():
    """Fonction principale simplifiée"""
    print("🚀 APOCALIPSSI - Démarrage automatique avec Ollama")
    print("=" * 60)
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ requis")
        sys.exit(1)
    print_success(f"Python {sys.version.split()[0]} détecté")
    
    # Vérifier et créer .env avec configuration Ollama
    check_env()
    
    # Configuration d'Ollama
    ollama_success = setup_ollama()
    
    # Installer les dépendances backend
    print_step("Installation des dépendances backend")
    if not run_command("pip install -r backend/requirements.txt")[0]:
        print_error("Erreur lors de l'installation des dépendances backend")
        sys.exit(1)
    print_success("Dépendances backend installées")
    
    # Installer spaCy pour l'anonymisation PII
    print_step("Configuration de l'anonymisation PII")
    try:
        import spacy
        print_success("spaCy déjà installé")
    except ImportError:
        print_info("Installation de spaCy pour l'anonymisation PII...")
        if not run_command("pip install spacy>=3.7.0")[0]:
            print_error("Erreur lors de l'installation de spaCy")
            print_info("L'anonymisation PII ne sera pas disponible")
        else:
            print_success("spaCy installé pour l'anonymisation PII")
    
    # Installer les dépendances frontend
    print_step("Installation des dépendances frontend")
    if not run_command("npm install", cwd="frontend")[0]:
        print_error("Erreur lors de l'installation des dépendances frontend")
        print_info("Assurez-vous que Node.js est installé: https://nodejs.org/")
        sys.exit(1)
    print_success("Dépendances frontend installées")
    
    # Démarrer le backend
    print_step("Démarrage du backend")
    backend_process = subprocess.Popen([sys.executable, "app.py"], cwd="backend")
    print_success("Backend démarré sur http://localhost:5000")
    
    # Attendre un peu
    time.sleep(2)
    
    # Démarrer le frontend
    print_step("Démarrage du frontend")
    frontend_process = subprocess.Popen("npm run dev", cwd="frontend", shell=True)
    print_success("Frontend démarré sur http://localhost:5173")
    
    print("\n" + "=" * 60)
    print("🎉 Application APOCALIPSSI démarrée avec succès !")
    print("\n📱 Accès:")
    print("   Frontend: http://localhost:5173")
    print("   Backend:  http://localhost:5000")
    
    if ollama_success:
        print("\n🤖 Modèle LLM local Ollama configuré et prêt")
        print("   L'application utilise maintenant un modèle local pour l'analyse")
    else:
        print("\n⚠️  Ollama non configuré")
        print("   L'application utilisera l'API externe si configurée")
    
    print("\n💡 Pour arrêter l'application, appuyez sur Ctrl+C")
    
    try:
        # Attendre que l'un des processus se termine
        while backend_process.poll() is None and frontend_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'application...")
        backend_process.terminate()
        frontend_process.terminate()
        print_success("Application arrêtée")

if __name__ == "__main__":
    main() 