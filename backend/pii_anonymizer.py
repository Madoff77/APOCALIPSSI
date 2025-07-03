#!/usr/bin/env python3
"""
Module d'anonymisation PII (Personal Identifiable Information)
Détecte et anonymise les données personnelles avant l'analyse LLM
Conforme RGPD pour APOCALIPSSI
"""

import re
import hashlib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIAnonymizer:
    """Classe pour l'anonymisation des données personnelles"""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialise l'anonymiseur PII
        
        Args:
            strict_mode: Si True, anonymise de manière stricte (RGPD)
        """
        self.strict_mode = strict_mode
        self.anonymization_map = {}
        self.anonymization_log = []
        
        # Patterns pour détecter les PII
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_fr': r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}',
            'phone_international': r'\+[1-9]\d{1,14}',
            'ssn_fr': r'\b\d{1,2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b',  # Numéro de sécurité sociale
            'iban_fr': r'FR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\s?\d{2}',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'postal_code_fr': r'\b\d{5}\b',
            'date_birth': r'\b(0?[1-9]|[12]\d|3[01])[/-](0?[1-9]|1[0-2])[/-](19|20)\d{2}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'mac_address': r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'
        }
        
        # Placeholders pour l'anonymisation
        self.placeholders = {
            'email': '[EMAIL_ANONYMIZÉ]',
            'phone_fr': '[TÉLÉPHONE_ANONYMIZÉ]',
            'phone_international': '[TÉLÉPHONE_INTERNATIONAL_ANONYMIZÉ]',
            'ssn_fr': '[NUMÉRO_SÉCURITÉ_SOCIALE_ANONYMIZÉ]',
            'iban_fr': '[IBAN_ANONYMIZÉ]',
            'credit_card': '[CARTE_BANCAIRE_ANONYMIZÉ]',
            'postal_code_fr': '[CODE_POSTAL_ANONYMIZÉ]',
            'date_birth': '[DATE_NAISSANCE_ANONYMIZÉ]',
            'ip_address': '[ADRESSE_IP_ANONYMIZÉ]',
            'mac_address': '[ADRESSE_MAC_ANONYMIZÉ]',
            'person_name': '[NOM_PERSONNE_ANONYMIZÉ]',
            'company_name': '[NOM_ENTREPRISE_ANONYMIZÉ]',
            'address': '[ADRESSE_ANONYMIZÉ]'
        }
        
        # Noms français courants pour détection
        self.french_names = [
            'jean', 'pierre', 'marie', 'sophie', 'thomas', 'julie', 'nicolas', 'emilie',
            'alexandre', 'camille', 'antoine', 'laura', 'maxime', 'lisa', 'romain', 'chloe',
            'quentin', 'manon', 'adrien', 'emma', 'clement', 'lea', 'guillaume', 'juliette',
            'benjamin', 'lucie', 'hugo', 'elodie', 'arthur', 'marine', 'louis', 'audrey',
            'paul', 'melanie', 'jules', 'julie', 'gabriel', 'sarah', 'leo', 'clara'
        ]
        
        # Mots-clés pour détecter les entreprises
        self.company_keywords = [
            'sarl', 'sa', 'sas', 'eurl', 'sasu', 'sci', 'snc', 'groupe', 'entreprise',
            'société', 'compagnie', 'corporation', 'ltd', 'inc', 'corp', 'sarl', 'sa'
        ]

    def detect_person_names(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Détecte les noms de personnes dans le texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (nom_détecté, type, position)
        """
        detected_names = []
        
        # Détection basée sur les patterns de noms français
        # Pattern: Prénom + Nom (avec majuscules)
        name_pattern = r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        matches = re.finditer(name_pattern, text)
        
        for match in matches:
            full_name = match.group(0)
            first_name = match.group(1).lower()
            
            # Vérifier si c'est un prénom français courant
            if first_name in self.french_names:
                detected_names.append((full_name, 'person_name', match.start()))
        
        return detected_names

    def detect_company_names(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Détecte les noms d'entreprises dans le texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (nom_entreprise, type, position)
        """
        detected_companies = []
        
        # Pattern pour détecter les noms d'entreprises
        # Format: Nom + (SA/SARL/SAS/etc.)
        company_pattern = r'\b([A-Z][A-Za-z\s&]+)\s+(SA|SARL|SAS|SASU|EURL|SCI|SNC|Groupe|Entreprise)\b'
        matches = re.finditer(company_pattern, text)
        
        for match in matches:
            company_name = match.group(0)
            detected_companies.append((company_name, 'company_name', match.start()))
        
        return detected_companies

    def detect_addresses(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Détecte les adresses dans le texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (adresse, type, position)
        """
        detected_addresses = []
        
        # Pattern pour détecter les adresses françaises
        # Format: Numéro + Rue + Code postal + Ville
        address_pattern = r'\b\d{1,3}\s+[A-Za-zÀ-ÿ\s]+,\s*\d{5}\s+[A-Za-zÀ-ÿ\s]+\b'
        matches = re.finditer(address_pattern, text)
        
        for match in matches:
            address = match.group(0)
            detected_addresses.append((address, 'address', match.start()))
        
        return detected_addresses

    def detect_pattern_based_pii(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Détecte les PII basées sur des patterns regex
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (pii_détectée, type, position)
        """
        detected_pii = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected_pii.append((match.group(0), pii_type, match.start()))
        
        return detected_pii

    def generate_secure_hash(self, original_value: str, pii_type: str) -> str:
        """
        Génère un hash sécurisé pour tracer l'anonymisation
        
        Args:
            original_value: Valeur originale
            pii_type: Type de PII
            
        Returns:
            Hash sécurisé
        """
        salt = f"APOCALIPSSI_{pii_type}_{datetime.now().strftime('%Y%m%d')}"
        hash_input = f"{original_value}{salt}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:8]

    def anonymize_text(self, text: str) -> Tuple[str, Dict]:
        """
        Anonymise le texte en détectant et remplaçant les PII
        
        Args:
            text: Texte à anonymiser
            
        Returns:
            Tuple (texte_anonymisé, mapping_anonymisation)
        """
        logger.info("Début de l'anonymisation PII")
        
        # Réinitialiser les structures
        self.anonymization_map = {}
        self.anonymization_log = []
        
        # Détecter tous les types de PII
        all_detected = []
        
        # PII basées sur des patterns
        all_detected.extend(self.detect_pattern_based_pii(text))
        
        # Noms de personnes
        all_detected.extend(self.detect_person_names(text))
        
        # Noms d'entreprises
        all_detected.extend(self.detect_company_names(text))
        
        # Adresses
        all_detected.extend(self.detect_addresses(text))
        
        # Trier par position pour éviter les conflits
        all_detected.sort(key=lambda x: x[2], reverse=True)
        
        # Anonymiser le texte
        anonymized_text = text
        
        for original_value, pii_type, position in all_detected:
            # Générer un hash sécurisé
            secure_hash = self.generate_secure_hash(original_value, pii_type)
            
            # Créer le placeholder
            placeholder = self.placeholders.get(pii_type, f'[{pii_type.upper()}_ANONYMIZÉ]')
            
            # Ajouter au mapping
            self.anonymization_map[placeholder] = {
                'original': original_value,
                'type': pii_type,
                'hash': secure_hash,
                'position': position
            }
            
            # Ajouter au log
            self.anonymization_log.append({
                'timestamp': datetime.now().isoformat(),
                'type': pii_type,
                'hash': secure_hash,
                'position': position
            })
            
            # Remplacer dans le texte
            anonymized_text = (
                anonymized_text[:position] + 
                placeholder + 
                anonymized_text[position + len(original_value):]
            )
        
        # Statistiques
        stats = {
            'total_pii_detected': len(all_detected),
            'types_detected': list(set(item[1] for item in all_detected)),
            'anonymization_map': self.anonymization_map,
            'log': self.anonymization_log
        }
        
        logger.info(f"Anonymisation terminée: {len(all_detected)} PII détectées et anonymisées")
        
        return anonymized_text, stats

    def get_anonymization_report(self) -> Dict:
        """
        Génère un rapport d'anonymisation pour audit
        
        Returns:
            Rapport d'anonymisation
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'strict_mode': self.strict_mode,
            'total_pii_detected': len(self.anonymization_map),
            'types_detected': list(set(item['type'] for item in self.anonymization_map.values())),
            'anonymization_log': self.anonymization_log,
            'compliance_status': 'RGPD_COMPLIANT' if self.strict_mode else 'PARTIAL_ANONYMIZATION'
        }

    def save_anonymization_log(self, filename: str = None) -> str:
        """
        Sauvegarde le log d'anonymisation
        
        Args:
            filename: Nom du fichier (optionnel)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"anonymization_log_{timestamp}.json"
        
        log_data = {
            'report': self.get_anonymization_report(),
            'anonymization_map': self.anonymization_map
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Log d'anonymisation sauvegardé: {filename}")
        return filename

# Fonction utilitaire pour anonymisation rapide
def anonymize_document_text(text: str, strict_mode: bool = True) -> Tuple[str, Dict]:
    """
    Fonction utilitaire pour anonymiser rapidement un texte de document
    
    Args:
        text: Texte du document
        strict_mode: Mode d'anonymisation strict (RGPD)
        
    Returns:
        Tuple (texte_anonymisé, statistiques)
    """
    anonymizer = PIIAnonymizer(strict_mode=strict_mode)
    return anonymizer.anonymize_text(text)

# Test rapide
if __name__ == "__main__":
    # Test avec un texte contenant des PII
    test_text = """
    Bonjour, je m'appelle Jean Dupont et je travaille chez TechCorp SA.
    Mon email est jean.dupont@techcorp.fr et mon téléphone est 01 23 45 67 89.
    J'habite au 123 Rue de la Paix, 75001 Paris.
    Mon numéro de sécurité sociale est 1 85 12 34 567 890 12.
    """
    
    print("=== Test d'anonymisation PII ===")
    print("Texte original:")
    print(test_text)
    
    anonymized_text, stats = anonymize_document_text(test_text)
    
    print("\nTexte anonymisé:")
    print(anonymized_text)
    
    print(f"\nStatistiques: {stats['total_pii_detected']} PII détectées")
    print(f"Types détectés: {stats['types_detected']}") 