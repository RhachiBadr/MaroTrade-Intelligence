"""
spacy_extractor.py — NLP Service Module
Extraction d'entités nommées et dates à partir de textes réglementaires
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remplace l'extraction Claude par spaCy (modèle transformer français/anglais)
- Extraction pays (GPE)
- Extraction organisations (ORG)
- Extraction dates (DATE)
- Extraction produits personnalisés
"""

import re
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import spacy
from datetime import datetime

# ISO 3166-1 alpha-3 codes pour pays
COUNTRY_CODES = {
    "france": "FRA", "allemagne": "DEU", "espagne": "ESP", "italie": "ITA",
    "belgique": "BEL", "pays-bas": "NLD", "suisse": "CHE", "suede": "SWE",
    "états-unis": "USA", "canada": "CAN", "mexique": "MEX",
    "arabie saoudite": "SAU", "emirats": "ARE", "qatar": "QAT", "koweit": "KWT",
    "egypte": "EGY", "maroc": "MAR", "tunisie": "TUN", "algerie": "DZA",
    "japon": "JPN", "chine": "CHN", "inde": "IND",
    "royaume-uni": "GBR", "ue": "EU", "europe": "EU"
}

# Codes HS courants exportés par Maroc
HS_CODES = {
    "151590": "huile d'argan",
    "160413": "sardines en conserve",
    "080410": "dattes fraîches",
    "09102010": "safran",
    "090920": "cumin",
    "570110": "tapis berbère",
    "691010": "zellige",
    "260300": "phosphates",
    "870899": "câbles automobiles"
}


@dataclass
class ExtractedEntity:
    """Une entité extraite d'un texte réglementaire."""
    type_: str          # "COUNTRY", "ORG", "DATE", "HS_CODE", "RISK_KEYWORD"
    value: str          # Valeur trouvée
    start_char: int     # Position dans le texte
    end_char: int       # Position de fin
    confidence: float   # Confiance 0-1


class SpacyExtractor:
    """
    Extracteur d'entités NLP basé sur spaCy + modèles transformers.
    
    Modèles utilisés :
    - "en_core_web_trf" pour anglais/multi
    - "fr_dep_news_trf" pour français (optionnel)
    """

    def __init__(self, lang: str = "en", use_transformers: bool = True):
        """
        Args:
            lang: 'en' ou 'fr' (commencer par 'en' si French model pas dispo)
            use_transformers: Utiliser le modèle transformer (plus robuste mais lent)
        """
        self.lang = lang
        self.use_transformers = use_transformers
        
        # Charger le modèle spaCy (fallback si indisponible)
        try:
            if lang == "fr" and use_transformers:
                # Note : ce modèle doit être téléchargé avec :
                # python -m spacy download fr_dep_news_trf
                self.nlp = spacy.load("fr_dep_news_trf")
            elif lang == "en" and use_transformers:
                # python -m spacy download en_core_web_trf
                self.nlp = spacy.load("en_core_web_trf")
            else:
                # Fallback sur modèles classiques
                model_name = "fr_core_news_sm" if lang == "fr" else "en_core_web_sm"
                self.nlp = spacy.load(model_name)
        except OSError:
            # Télécharger automatiquement si absent
            import subprocess
            model = "en_core_web_sm"  # Fallback par défaut
            print(f"Modèle spaCy manquant. Téléchargement de {model}...")
            subprocess.run([
                sys.executable, "-m", "spacy", "download", model
            ], check=True)
            self.nlp = spacy.load(model)

        # Mots-clés de risque pour classification
        self.risk_keywords = {
            "blocage|blocage douanier|interdit|interdiction|bannir": "CRITICAL",
            "recall|rappel produit|retrait|retraite": "CRITICAL",
            "suspension|suspecté|pathogène|contaminé": "CRITICAL",
            "nouveau règlement|nouvelle norme|obligation|doit|doivent être": "WARNING",
            "conforms|conformité requise|délai": "WARNING",
            "informations|mise à jour|clarification": "INFO",
        }

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """
        Extrait les entités nommées du texte.
        
        Returns:
            Liste d'ExtractedEntity
        """
        entities = []
        
        # Traitement spaCy NER
        doc = self.nlp(text)
        
        # Extraction entités reconnaissables par spaCy
        for ent in doc.ents:
            entity_type = None
            confidence = 0.85
            
            # Mapping spaCy NER → nos types
            if ent.label_ in ("GPE", "LOC"):
                country_name = ent.text.lower().strip()
                if country_name in COUNTRY_CODES:
                    entity_type = "COUNTRY"
                    entity_value = COUNTRY_CODES[country_name]
                else:
                    entity_type = "COUNTRY"
                    entity_value = ent.text
                    confidence = 0.6
                    
            elif ent.label_ == "ORG":
                entity_type = "ORG"
                entity_value = ent.text
                confidence = 0.8
                
            elif ent.label_ == "DATE":
                entity_type = "DATE"
                entity_value = ent.text
                confidence = 0.9
            
            if entity_type:
                entities.append(ExtractedEntity(
                    type_=entity_type,
                    value=entity_value,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                    confidence=confidence
                ))
        
        # Extraction codes HS personnalisés
        for code, product in HS_CODES.items():
            pattern = rf"\b{re.escape(code)}\b"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    type_="HS_CODE",
                    value=code,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.95
                ))
        
        # Extraction mots-clés de risque
        for pattern, risk_level in self.risk_keywords.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    type_="RISK_KEYWORD",
                    value=match.group(),
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.75
                ))
        
        # Trier par position
        entities.sort(key=lambda e: e.start_char)
        return entities

    def extract_countries(self, text: str) -> List[str]:
        """Extrait les codes ISO3 des pays mentions."""
        entities = self.extract_entities(text)
        countries = [e.value for e in entities if e.type_ == "COUNTRY"]
        return list(set(countries))  # Unique

    def extract_dates(self, text: str) -> List[str]:
        """Extrait les dates mentionnées."""
        entities = self.extract_entities(text)
        dates = [e.value for e in entities if e.type_ == "DATE"]
        return dates

    def extract_hs_codes(self, text: str) -> List[str]:
        """Extrait les codes HS mentionnés."""
        entities = self.extract_entities(text)
        codes = [e.value for e in entities if e.type_ == "HS_CODE"]
        return list(set(codes))

    def extract_risk_level_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extrait les mots-clés par niveau de risque."""
        result = {"CRITICAL": [], "WARNING": [], "INFO": []}
        entities = self.extract_entities(text)
        
        for e in entities:
            if e.type_ == "RISK_KEYWORD":
                # Retrouver le niveau de risque
                for pattern, level in self.risk_keywords.items():
                    if re.search(pattern, e.value, re.IGNORECASE):
                        result[level].append(e.value)
                        break
        
        return result

    def analyze_text_structure(self, text: str) -> Dict:
        """Analyse la structure/complexité du texte."""
        doc = self.nlp(text)
        
        return {
            "words": len([t for t in doc if not t.is_punct]),
            "sentences": len(list(doc.sents)),
            "entities_count": len(doc.ents),
            "named_entities": [(ent.text, ent.label_) for ent in doc.ents],
        }


# Pour tester et télécharger les modèles spaCy au démarrage
if __name__ == "__main__":
    import subprocess
    
    # Télécharger les modèles si absent
    try:
        extractor = SpacyExtractor(lang="en", use_transformers=False)
        
        # Test simple
        test_text = """
        La FDA rappelle les sardines de marque XYZ du Maroc (160413) 
        en raison d'une contamination. Les exportateurs doivent se conformer 
        avant le 15 juin 2026. Contact: USA Trade Commission.
        """
        
        entities = extractor.extract_entities(test_text)
        print("Entités extraites :")
        for e in entities:
            print(f"  {e.type_}: {e.value} (confiance: {e.confidence})")
        
        print("\nPays:", extractor.extract_countries(test_text))
        print("Dates:", extractor.extract_dates(test_text))
        print("Codes HS:", extractor.extract_hs_codes(test_text))
        
    except Exception as e:
        print(f"Erreur : {e}")
