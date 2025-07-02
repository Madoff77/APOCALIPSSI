import fitz  # PyMuPDF
import io

def extract_text_from_pdf(file):
    """
    Extrait le texte d'un fichier PDF téléchargé.
    
    Args:
        file: Objet fichier Flask (FileStorage)
    
    Returns:
        str: Texte extrait du PDF
    
    Raises:
        Exception: Si l'extraction échoue
    """
    try:
        # Lire le contenu du fichier
        file_content = file.read()
        
        # Réinitialiser le pointeur de fichier au cas où il serait utilisé ailleurs
        file.seek(0)
        
        # Ouvrir le PDF avec PyMuPDF
        doc = fitz.open(stream=file_content, filetype="pdf")
        
        # Extraire le texte de toutes les pages
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Nettoyer le texte (supprimer les lignes vides multiples)
            cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            
            if cleaned_text:
                text_parts.append(f"--- Page {page_num + 1} ---\n{cleaned_text}")
        
        # Fermer le document
        doc.close()
        
        # Joindre tout le texte
        full_text = '\n\n'.join(text_parts)
        
        if not full_text.strip():
            raise Exception("Aucun texte extractible trouvé dans le PDF")
        
        return full_text
        
    except Exception as e:
        print(f"Erreur lors de l'extraction PDF: {e}")
        raise Exception(f"Impossible d'extraire le texte du PDF: {str(e)}")
