"""
summarizer.py — Génération de résumés pour alertes réglementaires
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Utilise BART / mT5 pour générer des résumés concis en français
pour les PME marocaines.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


@dataclass
class Summary:
    """Un résumé généré."""
    short: str          # 1-2 phrases (max 150 chars)
    medium: str         # 2-3 phrases (max 300 chars)
    action_items: List[str]  # Points d'action concrets


class AlertSummarizer:
    """
    Généré des résumés d'alertes réglementaires appropriés pour PME.
    
    Modèles supportés:
    - facebook/bart-large-cnn : Excellent pour anglais
    - google/mt5-base : Multilingue, peut résumer en français
    - facebook/mbart-large-cc25 : Multilingue (peut générer en FR)
    """

    def __init__(self, language: str = "en", use_gpu: bool = False):
        """
        Args:
            language: "en" ou "fr"
            use_gpu: Utiliser GPU si disponible
        """
        self.language = language
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        self.tokenizer = None
        self.model = None
        self.model_available = False

        # Chargement direct du modèle seq2seq pour éviter les changements de task pipeline
        if language == "en":
            model_name = "facebook/bart-large-cnn"
        else:
            model_name = "google/mt5-small"

        if os.getenv("MAROTRADE_USE_GENERATIVE_SUMMARY", "0").lower() not in {"1", "true", "yes"}:
            print("Summarizer generatif desactive, fallback extractif local.")
            return

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            if self.device == 0:
                self.model.to("cuda")
            self.model_available = True
        except Exception as e:
            print(f"Erreur chargement modèle: {e}")
            try:
                model_name = "t5-small"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                if self.device == 0:
                    self.model.to("cuda")
                self.model_available = True
            except Exception as fallback_error:
                print(f"Summarizer indisponible, fallback extractif local: {fallback_error}")

    def summarize(self, text: str, max_short: int = 150, max_medium: int = 300) -> Summary:
        """
        Génère des résumés de différentes longueurs.
        
        Args:
            text: Texte complet de l'alerte
            max_short: Longueur max résumé court
            max_medium: Longueur max résumé moyen
        
        Returns:
            Summary avec court/moyen résumés
        """
        # Nettoyage du texte
        text_clean = text.strip()
        if not self.model_available:
            short = self._extractive_summary(text_clean, max_short)
            medium = self._extractive_summary(text_clean, max_medium)
        elif len(text_clean) < 100:
            # Texte trop court pour résumé
            short = text_clean[:max_short]
            medium = text_clean[:max_medium]
        else:
            # Résumé avec génération seq2seq directe
            try:
                short = self._generate_summary(text_clean, max_length=min(50, len(text_clean.split()) // 2))[:max_short]
                medium = self._generate_summary(text_clean, max_length=min(100, len(text_clean.split())))[:max_medium]
            except Exception as e:
                print(f"Erreur résumé: {e}")
                short = text_clean[:max_short]
                medium = text_clean[:max_medium]
        
        # Extraire les points d'action
        action_items = self._extract_action_items(text)
        
        # Traduction en français si nécessaire
        if self.language == "fr" or self._needs_fr_translation(text):
            short = self._translate_to_french(short)
            medium = self._translate_to_french(medium)
        
        return Summary(
            short=short,
            medium=medium,
            action_items=action_items
        )

    def _extractive_summary(self, text: str, max_chars: int) -> str:
        """Fallback local sans modele distant."""
        if not text:
            return ""
        sentences = [sentence.strip() for sentence in text.replace("\n", " ").split(".") if sentence.strip()]
        summary = ". ".join(sentences[:2]) if sentences else text
        return summary[:max_chars].rstrip()

    def _generate_summary(self, text: str, max_length: int) -> str:
        """Génère un résumé via le modèle seq2seq chargé."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding="longest"
        )
        if self.device == 0:
            inputs = {k: v.cuda() for k, v in inputs.items()}

        min_length = min(5, max_length)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            min_length=min_length,
            num_beams=4,
            early_stopping=True,
        )
        decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return decoded[0].strip() if decoded else ""

    def _extract_action_items(self, text: str) -> List[str]:
        """Extrait les actions à faire du texte."""
        actions = []
        text_lower = text.lower()
        
        # Patterns d'actions en anglais
        action_patterns = [
            ("must", "Obligatoire"),
            ("shall", "Requis"),
            ("should", "Recommandé"),
            ("submitted", "À soumettre"),
            ("comply", "Conformité requise"),
            ("deadline", "Délai à respecter"),
            ("notification", "Informer/Notifier"),
            ("withdrawal", "Retrait du produit"),
            ("recall", "Recall produit"),
        ]
        
        for pattern, action_label in action_patterns:
            if pattern in text_lower:
                actions.append(action_label)
        
        return list(set(actions))[:5]  # Max 5 actions uniques

    def _needs_fr_translation(self, text: str) -> bool:
        """Détecte si le texte est en anglais et nécessite traduction FR."""
        french_words = ["le", "la", "les", "et", "de", "du", "à", "pour"]
        french_count = sum(1 for word in french_words if f" {word} " in text.lower())
        english_words = ["the", "and", "of", "to", "for", "is", "are"]
        english_count = sum(1 for word in english_words if f" {word} " in text.lower())
        
        return english_count > french_count

    def _translate_to_french(self, english_text: str) -> str:
        """Traduction simple anglais → français (peut être amélioré avec MarianMT)."""
        # Dictionnaire de traduction basique
        translations = {
            "must": "doit",
            "shall": "doit",
            "should": "devrait",
            "product": "produit",
            "recall": "rappel produit",
            "contamination": "contamination",
            "ban": "interdiction",
            "deadline": "délai",
            "compliance": "conformité",
            "exported": "exporté",
            "imported": "importé",
            "food safety": "sécurité alimentaire",
            "alert": "alerte",
            "warning": "avertissement",
        }
        
        result = english_text.lower()
        for en, fr in translations.items():
            result = result.replace(en.lower(), fr)
        
        return result.capitalize()

    def batch_summarize(self, texts: List[str]) -> List[Summary]:
        """Résume un batch de textes."""
        return [self.summarize(text) for text in texts]


class FrenchContentGenerator:
    """
    Génère du contenu français ciblé pour PME marocaines.
    Offre des templates et formulations adaptés.
    """

    @staticmethod
    def generate_impact_summary(
        alert_title: str,
        countries: List[str],
        risk_level: str,
        products: List[str]
    ) -> str:
        """
        Génère un résumé d'impact personnalisé en français.
        """
        
        if risk_level == "CRITIQUE":
            template = f"""
🔴 ALERTE CRITIQUE: {alert_title}

Marchés affectés: {', '.join(countries) if countries else 'Internationaux'}
Produits concernés: {', '.join(products) if products else 'Tous les produits'}

ACTION IMMÉDIATE REQUISE:
- Vérifier la conformité de vos expéditions
- Contacter vos clients avant envoi
- Mettre en place des mesures correctives
            """
        elif risk_level == "ATTENTION":
            template = f"""
🟡 ALERTE ATTENTION: {alert_title}

Marchés affectés: {', '.join(countries) if countries else 'À vérifier'}
Produits concernés: {', '.join(products) if products else 'À vérifier'}

ACTION RECOMMANDÉE (délai 30 jours):
- Étudier les nouvelles exigences
- Préparer votre conformité
- Mettre à jour votre documentation
            """
        else:
            template = f"""
🟢 INFORMATION: {alert_title}

Marchés affectés: {', '.join(countries) if countries else 'Information générale'}
Produits concernés: {', '.join(products) if products else 'Information générale'}

À SUIVRE:
- Rester informé des développements
- Mettre à jour votre veille réglementaire
            """
        
        return template.strip()

    @staticmethod
    def generate_action_plan(products: List[str], countries: List[str]) -> str:
        """Génère un plan d'action personnalisé."""
        
        plan = """
PLAN D'ACTION EXPORT

1. VÉRIFICATION DOCUMENTAIRE
   ☐ Vérifier les certificats de conformité
   ☐ Mettre à jour les fiches techniques
   ☐ Collecter les autorisations nécessaires

2. CONTRÔLE DE QUALITÉ
   ☐ Tester les produits selon nouvelles normes
   ☐ Documentez les résultats
   ☐ Conservez les traces d'étiquetage

3. COMMUNICATION
   ☐ Informer les clients/importateurs
   ☐ Préparer les réponses aux questions
   ☐ Synchroniser avec les autorités (ONSSA, douanes)

4. LOGISTIQUE
   ☐ Adapter les délais d'expédition
   ☐ Pra-déclarations douanière si nécessaire
   ☐ Assurance et couverture adaptées
        """
        
        return plan.strip()


# Test
if __name__ == "__main__":
    summarizer = AlertSummarizer(language="en", use_gpu=False)
    
    test_text = """
    The FDA has issued a new alert regarding sardine products from Morocco. 
    All manufacturers and exporters must ensure compliance with the updated 
    food safety standards by June 1, 2026. Non-compliance will result in 
    product seizure at US ports. Immediate actions must be taken to verify 
    product safety certifications and conduct internal testing.
    """
    
    summary = summarizer.summarize(test_text)
    print("Résumé court:", summary.short)
    print("Résumé moyen:", summary.medium)
    print("Actions:", summary.action_items)
    
    # Test French content
    french_content = FrenchContentGenerator.generate_impact_summary(
        "Alerte sardines Maroc",
        ["USA", "FRA"],
        "CRITIQUE",
        ["160413"]
    )
    print("\nContenu French:")
    print(french_content)
