"""
regulatory_watch.py — Module C02 · Veille Réglementaire
MaroTrade Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sources connectées :
  ① EUR-Lex API      — Règlements et directives UE (gratuit)
  ② RASFF RSS        — Alertes sanitaires et alimentaires UE (gratuit)
  ③ WTO API          — Mesures tarifaires et non-tarifaires (gratuit)
  ④ FDA RSS          — Alertes alimentaires USA (gratuit)
  ⑤ Base locale      — Réglementations clés encodées (fallback)
"""

import feedparser
import requests
import json
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

from services.watch.sources import RASFFStructuredClient


logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CACHE_DIR = Path(".cache_c02")
CACHE_DIR.mkdir(exist_ok=True)

# Niveaux d'alerte
LEVEL_CRITICAL  = "CRITIQUE"    # Blocage imminent, action urgente
LEVEL_WARNING   = "ATTENTION"   # Changement à surveiller sous 30 jours
LEVEL_INFO      = "INFO"        # Mise à jour mineure, à noter

# Couleurs par niveau
LEVEL_COLORS = {
    LEVEL_CRITICAL: "#E24B4A",
    LEVEL_WARNING:  "#BA7517",
    LEVEL_INFO:     "#1D9E75",
}

GENERIC_PRODUCT_TERMS = {
    "fresh",
    "food",
    "foods",
    "alimentaire",
    "produit",
    "produits",
    "export",
    "import",
}


def _product_keywords(hs_code: str, product_name: str = "") -> list:
    keywords = list(HS_KEYWORDS.get(hs_code, []))
    for token in re.findall(r"\w{3,}", (product_name or "").lower()):
        if token not in GENERIC_PRODUCT_TERMS:
            keywords.append(token)
    return list(dict.fromkeys(keywords))


def _matches_product(alert: dict, hs_code: str, product_name: str = "") -> bool:
    keywords = _product_keywords(hs_code, product_name)
    if not keywords:
        return True

    alert_text = " ".join(
        str(alert.get(field, "") or "")
        for field in ["titre", "resume", "category", "classification", "origin", "produits"]
    ).lower()
    alert_tokens = set(re.findall(r"\w{3,}", alert_text))
    for keyword in keywords:
        normalized_keyword = keyword.lower().strip()
        if not normalized_keyword:
            continue
        if " " in normalized_keyword:
            if normalized_keyword in alert_text:
                return True
        elif len(normalized_keyword) <= 4:
            if normalized_keyword in alert_tokens:
                return True
        elif normalized_keyword in alert_text:
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════

@dataclass
class RegulatoryAlert:
    """Une alerte réglementaire générée par le moteur."""
    id:           str
    titre:        str
    niveau:       str           # CRITIQUE / ATTENTION / INFO
    source:       str           # EUR-Lex, RASFF, WTO, FDA...
    pays:         str           # Code ISO3 du pays concerné
    pays_nom:     str
    produits:     list          # Codes HS ou catégories concernés
    date:         str           # Date de publication
    resume:       str           # Résumé en français
    impact:       str           # Description de l'impact sur l'export
    action:       str           # Action recommandée
    url:          str           # Lien vers la source officielle
    score_impact: float         # 0–100 (100 = impact maximal)
    delai_jours:  Optional[int] # Délai avant entrée en vigueur


# ═══════════════════════════════════════════════════════════════
# BASE DE CONNAISSANCES RÉGLEMENTAIRE
# Réglementations importantes déjà en vigueur — référence statique
# ═══════════════════════════════════════════════════════════════

REGLEMENTATIONS_BASE = [
    # ─── Union Européenne ───────────────────────────────────────
    {
        "id": "EU-2023-CBAM",
        "titre": "Mécanisme d'ajustement carbone aux frontières (CBAM)",
        "niveau": LEVEL_WARNING,
        "source": "EUR-Lex",
        "pays": "EU",
        "pays_nom": "Union Européenne",
        "produits": ["acier", "aluminium", "engrais", "ciment", "électricité"],
        "date": "2023-10-01",
        "resume": "L'UE impose un prix carbone sur les importations de certains secteurs industriels à partir d'octobre 2023 (phase transitoire). Phase définitive en 2026.",
        "impact": "Coût supplémentaire sur les produits concernés. Hors agroalimentaire pour l'instant.",
        "action": "Vérifier si vos produits entrent dans le périmètre CBAM. Préparer les déclarations d'émissions.",
        "url": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32023R0956",
        "score_impact": 65.0,
        "delai_jours": None,
    },
    {
        "id": "EU-2024-DEFORESTATION",
        "titre": "Règlement UE anti-déforestation (EUDR)",
        "niveau": LEVEL_CRITICAL,
        "source": "EUR-Lex",
        "pays": "EU",
        "pays_nom": "Union Européenne",
        "produits": ["080410", "café", "cacao", "soja", "huile de palme", "bois", "caoutchouc"],
        "date": "2024-01-01",
        "resume": "Tout produit lié à des terres déboisées après 2020 est interdit à l'importation dans l'UE. Obligation de traçabilité géographique complète.",
        "impact": "Blocage total à la frontière UE si absence de preuve de non-déforestation. Applicable aux dattes, huiles végétales.",
        "action": "Préparer la documentation de traçabilité. Géolocalisation des parcelles de production obligatoire.",
        "url": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32023R1115",
        "score_impact": 90.0,
        "delai_jours": 60,
    },
    {
        "id": "EU-2026-ETIQUETAGE-CARBONE",
        "titre": "Étiquetage empreinte carbone sur huiles alimentaires",
        "niveau": LEVEL_WARNING,
        "source": "EUR-Lex",
        "pays": "EU",
        "pays_nom": "Union Européenne",
        "produits": ["151590", "150910", "huile"],
        "date": "2026-01-01",
        "resume": "À partir de janvier 2026, l'UE exige l'affichage de l'empreinte carbone sur les emballages des huiles alimentaires importées.",
        "impact": "Coût de mise en conformité (audit carbone, re-étiquetage). Délai 6 mois accordé.",
        "action": "Réaliser un bilan carbone du produit. Prévoir la refonte des étiquettes avant fin 2025.",
        "url": "https://ec.europa.eu/food/safety/labelling_nutrition",
        "score_impact": 70.0,
        "delai_jours": 180,
    },
    {
        "id": "EU-RASFF-RESIDUS",
        "titre": "Limites maximales de résidus (LMR) pesticides",
        "niveau": LEVEL_INFO,
        "source": "RASFF",
        "pays": "EU",
        "pays_nom": "Union Européenne",
        "produits": ["070200", "080410", "agroalimentaire"],
        "date": "2023-06-01",
        "resume": "L'EFSA a révisé les LMR pour 50 substances actives. Durcissement notable pour les tomates et les produits frais méditerranéens.",
        "impact": "Risque de blocage au contrôle phytosanitaire si dépassement des nouvelles limites.",
        "action": "Mettre à jour les protocoles de traitement phytosanitaire. Tester avant expédition.",
        "url": "https://www.efsa.europa.eu/fr/topics/topic/pesticides",
        "score_impact": 55.0,
        "delai_jours": None,
    },
    # ─── États-Unis ─────────────────────────────────────────────
    {
        "id": "USA-FDA-FSMA",
        "titre": "FSMA — Food Safety Modernization Act (règles import)",
        "niveau": LEVEL_WARNING,
        "source": "FDA",
        "pays": "USA",
        "pays_nom": "États-Unis",
        "produits": ["160413", "151590", "080410", "agroalimentaire"],
        "date": "2023-01-01",
        "resume": "La FDA exige que les importateurs américains vérifient que leurs fournisseurs étrangers appliquent des mesures préventives conformes au FSMA. Contrôles renforcés sur les huiles et conserves.",
        "impact": "Obligation de s'enregistrer auprès de la FDA. Contrôle documentaire systématique à l'entrée.",
        "action": "S'enregistrer sur le portail FDA (gratuit). Préparer le plan HACCP conforme FSMA.",
        "url": "https://www.fda.gov/food/food-safety-modernization-act-fsma",
        "score_impact": 75.0,
        "delai_jours": None,
    },
    {
        "id": "USA-CUSTOMS-CBP",
        "titre": "Droits compensateurs sur huiles végétales marocaines",
        "niveau": LEVEL_INFO,
        "source": "US Customs",
        "pays": "USA",
        "pays_nom": "États-Unis",
        "produits": ["151590"],
        "date": "2022-05-01",
        "resume": "Le Maroc bénéficie de l'accord de libre-échange avec les USA — droits à 0% sur l'huile d'argan. Aucune mesure compensatrice en vigueur.",
        "impact": "Positif — avantage tarifaire confirmé par rapport aux concurrents tunisiens et algériens.",
        "action": "Joindre le certificat d'origine Form A à chaque expédition pour bénéficier du taux préférentiel.",
        "url": "https://www.cbp.gov/trade/free-trade-agreements/morocco",
        "score_impact": 20.0,
        "delai_jours": None,
    },
    # ─── Japon ───────────────────────────────────────────────────
    {
        "id": "JPN-FOOD-SANITATION",
        "titre": "Loi japonaise sur l'hygiène alimentaire — révision 2024",
        "niveau": LEVEL_WARNING,
        "source": "METI Japon",
        "pays": "JPN",
        "pays_nom": "Japon",
        "produits": ["151590", "160413", "agroalimentaire"],
        "date": "2024-06-01",
        "resume": "Le Japon a durci les contrôles sur les contaminants dans les huiles importées. Nouvelles limites pour mycotoxines et métaux lourds.",
        "impact": "Contrôles plus fréquents à l'entrée au Japon. Risque de blocage si absence de certificat d'analyse.",
        "action": "Joindre systématiquement un certificat d'analyse (COA) par lot. Tester avant expédition.",
        "url": "https://www.mhlw.go.jp/english/topics/foodsafety/",
        "score_impact": 60.0,
        "delai_jours": None,
    },
    # ─── Canada ──────────────────────────────────────────────────
    {
        "id": "CAN-CFIA-ORGANIC",
        "titre": "Certification biologique Canada — équivalence Maroc",
        "niveau": LEVEL_INFO,
        "source": "CFIA Canada",
        "pays": "CAN",
        "pays_nom": "Canada",
        "produits": ["151590", "080410"],
        "date": "2023-01-01",
        "resume": "Le Canada reconnaît les certifications bio marocaines (ONSSA) comme équivalentes à la norme biologique canadienne. Facilitation pour les produits certifiés.",
        "impact": "Positif — plus besoin de double certification pour les produits bio ONSSA.",
        "action": "Conserver et joindre le certificat ONSSA. Mentionner l'accord d'équivalence sur la documentation douanière.",
        "url": "https://inspection.canada.ca/organic-products/",
        "score_impact": 15.0,
        "delai_jours": None,
    },
    # ─── Arabie Saoudite / Golfe ─────────────────────────────────
    {
        "id": "SAU-SFDA-HALAL",
        "titre": "Certification Halal obligatoire — SFDA Arabie Saoudite",
        "niveau": LEVEL_CRITICAL,
        "source": "SFDA",
        "pays": "SAU",
        "pays_nom": "Arabie Saoudite",
        "produits": ["160413", "agroalimentaire"],
        "date": "2023-01-01",
        "resume": "L'Arabie Saoudite exige une certification Halal reconnue par la SFDA pour tous les produits alimentaires importés. La certification doit être émise par un organisme accrédité par l'OIC.",
        "impact": "Blocage total à la douane saoudienne sans certificat Halal valide.",
        "action": "Obtenir la certification Halal auprès d'un organisme reconnu par l'IOAS (ex: ONSSA Maroc). Renouvellement annuel.",
        "url": "https://www.sfda.gov.sa/en",
        "score_impact": 95.0,
        "delai_jours": None,
    },
]


# ═══════════════════════════════════════════════════════════════
# SOURCES RSS — FLUX EN TEMPS RÉEL
# ═══════════════════════════════════════════════════════════════

RSS_SOURCES = {
    "RASFF": {
        "url":  "https://webgate.ec.europa.eu/rasff-window/backend/public/consumer/rss",
        "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL", "GBR"],
        "desc": "Alertes sanitaires UE — Rapid Alert System for Food and Feed",
    },
    "FDA": {
        "url":  "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-safety-recalls/rss.xml",
        "pays": ["USA"],
        "desc": "Alertes et rappels alimentaires FDA — États-Unis",
    },
    "EUR-LEX-NEW": {
        "url":  "https://eur-lex.europa.eu/tools/rss/eu-law-updates.xml",
        "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL"],
        "desc": "Nouvelles publications Journal Officiel UE",
    },
}

# Mots-clés pour filtrer les articles pertinents pour l'export marocain
KEYWORDS_PERTINENTS = [
    "import", "export", "alimentaire", "food", "huile", "oil", "sardine",
    "datte", "date", "argan", "organic", "bio", "halal", "pesticide",
    "résidu", "residue", "contaminant", "étiquetage", "labelling",
    "douane", "customs", "tarifaire", "tariff", "sanitaire", "sanitary",
    "phytosanitaire", "phytosanitary", "certification", "conformité",
    "compliance", "recall", "rappel", "alert", "alerte", "restriction",
    "interdiction", "ban", "règlement", "regulation",
]

# Codes HS marocains courants → mots-clés associés
HS_KEYWORDS = {
    "151590": ["argan", "huile végétale", "vegetable oil", "huile"],
    "160413": ["sardine", "thon", "conserve", "canned fish", "poisson"],
    "080410": ["datte", "dattes", "dates", "palm fruit"],
    "070200": ["tomate", "tomato"],
    "520811": ["textile", "coton", "cotton"],
}


# ═══════════════════════════════════════════════════════════════
# MOTEUR DE COLLECTE RSS
# ═══════════════════════════════════════════════════════════════

def fetch_rss_alerts(source_name: str, source_config: dict) -> list:
    """
    Récupère et parse un flux RSS réglementaire.
    Filtre les articles pertinents pour l'export marocain.
    """
    cache_key = f"rss_{source_name}_{datetime.now().strftime('%Y%m%d')}"
    cache_path = CACHE_DIR / f"{cache_key}.json"

    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    alerts = []
    try:
        response = requests.get(
            source_config["url"],
            timeout=15,
            headers={"User-Agent": "MaroTrade-Intelligence/1.0"},
        )
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        for entry in feed.entries[:20]:  # Max 20 derniers articles
            title   = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link    = entry.get("link", "")
            date    = entry.get("published", datetime.now().isoformat())

            # Filtrer par pertinence
            text = (title + " " + summary).lower()
            if not any(kw in text for kw in KEYWORDS_PERTINENTS):
                continue

            # Déterminer le niveau d'alerte
            niveau = _detect_level(text)

            # Générer un ID unique
            alert_id = hashlib.md5(f"{source_name}{title}{date}".encode()).hexdigest()[:8]

            alerts.append({
                "id":         f"{source_name}-{alert_id}",
                "titre":      title[:120],
                "niveau":     niveau,
                "source":     source_name,
                "pays":       source_config["pays"],
                "date":       date[:10],
                "resume":     summary[:300] if summary else title,
                "url":        link,
                "score_impact": _estimate_impact_score(text),
                "live":       True,
            })

    except Exception as e:
        pass  # Fallback silencieux

    if alerts:
        with open(cache_path, "w") as f:
            json.dump(alerts, f)

    return alerts

def _detect_level(text: str) -> str:
    """Détecte le niveau d'alerte depuis le texte."""
    critical_kw = ["recall", "rappel", "ban", "interdit", "suspension", "withdrawal",
                   "urgent", "immediate", "serious", "grave", "danger", "bloqu"]
    warning_kw  = ["warning", "avertissement", "change", "modification", "nouveau",
                   "new regulation", "updated", "révisé", "revised", "amended"]

    text_lower = text.lower()
    if any(kw in text_lower for kw in critical_kw):
        return LEVEL_CRITICAL
    if any(kw in text_lower for kw in warning_kw):
        return LEVEL_WARNING
    return LEVEL_INFO

def _estimate_impact_score(text: str) -> float:
    """Estime le score d'impact de 0 à 100."""
    score = 30.0  # Base
    high_impact  = ["interdit", "ban", "recall", "rappel", "blocage", "suspended"]
    mid_impact   = ["nouveau", "new", "modification", "revised", "updated", "change"]
    product_hits = ["argan", "sardine", "datte", "huile", "oil", "food", "alimentaire"]

    text_lower = text.lower()
    for kw in high_impact:
        if kw in text_lower:
            score += 25
    for kw in mid_impact:
        if kw in text_lower:
            score += 10
    for kw in product_hits:
        if kw in text_lower:
            score += 15

    return min(score, 100.0)


# ═══════════════════════════════════════════════════════════════
# MOTEUR DE SCORING ET FILTRAGE
# ═══════════════════════════════════════════════════════════════

def score_relevance(alert: dict, hs_code: str, target_countries: list, product_name: str = "") -> float:
    """
    Calcule la pertinence d'une alerte pour un produit et des marchés cibles.

    Args:
        alert:            Alerte brute
        hs_code:          Code HS du produit de l'utilisateur
        target_countries: Liste des pays cibles de l'utilisateur

    Returns:
        Score de pertinence 0–100
    """
    score = alert.get("score_impact", 30.0)

    # Bonus si le pays de l'alerte est dans les marchés cibles
    alert_pays = alert.get("pays", [])
    if isinstance(alert_pays, list):
        if any(p in target_countries for p in alert_pays):
            score *= 1.4
    elif alert_pays in target_countries:
        score *= 1.4

    # Bonus si le produit est explicitement mentionné
    product_match = _matches_product(alert, hs_code, product_name)
    alert["product_match"] = bool(product_match)
    if product_match:
        score *= 1.3
    elif alert.get("live") or alert.get("structured"):
        score *= 0.45
    else:
        score *= 0.75

    # Bonus urgence : alertes récentes
    try:
        alert_date = datetime.strptime(alert.get("date", "")[:10], "%Y-%m-%d")
        days_old = (datetime.now() - alert_date).days
        if days_old < 30:
            score *= 1.2
        elif days_old < 90:
            score *= 1.1
    except Exception:
        pass

    if not product_match and (alert.get("live") or alert.get("structured")):
        score = min(score, 44.0)

    return min(score, 100.0)


# ═══════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class RegulatoryWatchEngine:
    """
    Moteur de veille réglementaire pour MaroTrade Intelligence.
    Collecte, filtre et classe les alertes réglementaires
    pertinentes pour un produit et des marchés cibles donnés.
    """

    def __init__(self, use_nlp: bool = True):
        self.use_nlp = use_nlp
        self.nlp_analyzer = None
        self.rasff_client = RASFFStructuredClient()

        if not self.use_nlp:
            return

        try:
            from services.nlp import NLPAnalyzer

            self.nlp_analyzer = NLPAnalyzer(use_models=True)
        except Exception as exc:
            logger.exception("NLPAnalyzer initialization failed: %s", exc)
            self.nlp_analyzer = None

    @staticmethod
    def _as_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item)
        return str(value)

    def _normalize_alert(self, alert: dict) -> dict:
        normalized = dict(alert or {})

        titre = self._as_text(normalized.get("titre") or normalized.get("title"))
        resume = self._as_text(normalized.get("resume") or normalized.get("summary"))
        niveau = normalized.get("niveau") or normalized.get("level") or LEVEL_INFO
        pays = normalized.get("pays", "")
        pays_nom = normalized.get("pays_nom") or self._as_text(pays)
        origin = normalized.get("origin", self._as_text(pays))
        confidence = normalized.get("confidence", normalized.get("confiance", 0.0))
        impact_score = normalized.get(
            "impact_score",
            normalized.get("score_impact", normalized.get("relevance", 0.0)),
        )

        normalized.setdefault(
            "id",
            hashlib.md5(f"{titre}|{resume}|{normalized.get('source', '')}".encode()).hexdigest()[:12],
        )
        normalized["titre"] = titre
        normalized["titre_fr"] = normalized.get("titre_fr") or titre
        normalized["niveau"] = niveau
        normalized["level"] = normalized.get("level") or niveau
        normalized["source"] = normalized.get("source", "")
        normalized["pays"] = pays
        normalized["pays_nom"] = pays_nom
        normalized["date"] = normalized.get("date") or datetime.now().strftime("%Y-%m-%d")
        normalized["resume"] = resume
        normalized["resume_fr"] = normalized.get("resume_fr") or resume
        normalized["summary"] = normalized.get("summary") or resume
        normalized["action"] = normalized.get("action") or normalized.get("action_requise", "")
        normalized["url"] = normalized.get("url", "")
        normalized["score_impact"] = impact_score
        normalized["impact_score"] = impact_score
        normalized["confidence"] = confidence
        normalized["confiance"] = normalized.get("confiance", confidence)
        normalized["entities"] = normalized.get("entities") or {}
        normalized["keywords"] = normalized.get("keywords") or []
        normalized["reasoning"] = normalized.get("reasoning", "")
        normalized["category"] = normalized.get("category", "")
        normalized["classification"] = normalized.get("classification", "")
        normalized["origin"] = origin
        normalized["maroc_relevant"] = normalized.get("maroc_relevant", None)
        normalized.setdefault("nlp_enhanced", False)
        normalized.setdefault("llm_enhanced", False)

        return normalized

    def _calibrate_alert_level(
        self,
        alert: dict,
        predicted_level: str,
        confidence: float,
        impact_score: float,
    ) -> tuple[str, str]:
        """Combine NLP output with source metadata and export relevance."""
        original_level = alert.get("niveau") or alert.get("level") or LEVEL_INFO
        classification = self._as_text(alert.get("classification")).lower()
        relevance = float(alert.get("relevance", alert.get("score_impact", 0)) or 0)
        source = self._as_text(alert.get("source")).upper()
        text = f"{alert.get('titre', '')} {alert.get('resume', '')}".lower()
        product_match = alert.get("product_match")
        live_alert = bool(alert.get("live") or alert.get("structured"))

        severe_hazard = any(
            keyword in text
            for keyword in [
                "salmonella",
                "listeria",
                "aflatoxin",
                "botulinum",
                "e. coli",
                "mercury",
                "cadmium",
            ]
        )
        formal_block = any(
            keyword in classification
            for keyword in ["border rejection", "alert notification", "recall", "withdrawal"]
        )
        informational = any(
            keyword in classification
            for keyword in ["information notification", "follow-up", "attention"]
        )

        calibrated = predicted_level or original_level
        reasons = [
            f"NLP={predicted_level}",
            f"source={source or 'N/A'}",
            f"relevance={relevance:.0f}",
            f"confidence={confidence:.2f}",
        ]

        if relevance < 30:
            calibrated = LEVEL_INFO
            reasons.append("downgraded: faible pertinence produit/marche")
        elif product_match is False and live_alert and calibrated == LEVEL_CRITICAL:
            calibrated = LEVEL_WARNING
            reasons.append("downgraded: alerte temps reel hors produit")
        elif relevance < 55 and calibrated == LEVEL_CRITICAL and not alert.get("maroc_relevant"):
            calibrated = LEVEL_WARNING
            reasons.append("downgraded: critique NLP mais pertinence export moderee")

        if informational and calibrated == LEVEL_CRITICAL and not (severe_hazard and relevance >= 55):
            calibrated = LEVEL_WARNING
            reasons.append("downgraded: notification informative RASFF")

        if formal_block and severe_hazard and relevance >= 55 and confidence >= 0.70:
            calibrated = LEVEL_CRITICAL
            reasons.append("confirmed: danger sanitaire + action frontiere/rappel")
        elif impact_score < 45 and calibrated == LEVEL_CRITICAL:
            calibrated = LEVEL_WARNING
            reasons.append("downgraded: impact calcule sous seuil critique")

        return calibrated, "; ".join(reasons)

    def _enrich_alerts_with_nlp(
        self,
        alerts: list,
        hs_code: str,
        target_countries: list,
    ) -> list:
        logger.info("RegulatoryWatchEngine enriching alerts with NLPAnalyzer")

        if not self.nlp_analyzer:
            calibrated_alerts = []
            for alert in alerts:
                normalized = self._normalize_alert(alert)
                confidence = normalized.get("confidence") or 0.35
                impact_score = normalized.get("impact_score") or normalized.get("score_impact") or 0.0
                raw_level = normalized.get("niveau", LEVEL_INFO)
                level, calibration_reason = self._calibrate_alert_level(
                    normalized,
                    raw_level,
                    confidence,
                    impact_score,
                )
                normalized.update(
                    {
                        "niveau": level,
                        "level": level,
                        "raw_nlp_level": raw_level,
                        "calibration_reason": calibration_reason,
                        "confidence": confidence,
                        "confiance": confidence,
                        "reasoning": calibration_reason,
                    }
                )
                calibrated_alerts.append(normalized)
            return calibrated_alerts

        enriched_alerts = []
        for alert in alerts:
            normalized = self._normalize_alert(alert)
            alert_id = normalized.get("id")

            try:
                text = " ".join(
                    part for part in [normalized.get("titre", ""), normalized.get("resume", "")]
                    if part
                ).strip()
                category = normalized.get("category", "")
                classification = normalized.get("classification", "")
                origin = normalized.get("origin", normalized.get("pays", ""))
                maroc_relevant = normalized.get("maroc_relevant", None)

                result = self.nlp_analyzer.analyze(
                    text=text,
                    category=category,
                    classification=classification,
                    origin=self._as_text(origin),
                    maroc_relevant=maroc_relevant,
                    hs_code=hs_code,
                    target_countries=target_countries,
                )

                raw_niveau = result.get("niveau", normalized.get("niveau", LEVEL_INFO))
                confidence = result.get("confidence", result.get("confiance", normalized.get("confidence", 0.0)))
                impact_score = result.get("impact_score", normalized.get("impact_score", 0.0))
                niveau, calibration_reason = self._calibrate_alert_level(
                    normalized,
                    raw_niveau,
                    confidence,
                    impact_score,
                )
                reasoning = result.get("reasoning") or normalized.get("reasoning", "")
                if calibration_reason:
                    reasoning = f"{reasoning} Calibration: {calibration_reason}".strip()

                normalized.update(
                    {
                        "niveau": niveau,
                        "level": niveau,
                        "raw_nlp_level": raw_niveau,
                        "calibration_reason": calibration_reason,
                        "confidence": confidence,
                        "confiance": result.get("confiance", confidence),
                        "impact_score": impact_score,
                        "score_impact": impact_score,
                        "resume_fr": result.get("resume_fr") or result.get("summary") or normalized.get("resume_fr", ""),
                        "summary": result.get("summary") or normalized.get("summary", ""),
                        "entities": result.get("entities") or normalized.get("entities", {}),
                        "keywords": result.get("keywords") or normalized.get("keywords", []),
                        "reasoning": reasoning,
                        "category": result.get("category", category),
                        "classification": result.get("classification", classification),
                        "origin": result.get("origin", self._as_text(origin)),
                        "maroc_relevant": result.get("maroc_relevant", maroc_relevant),
                        "nlp_enhanced": True,
                        "llm_enhanced": True,
                    }
                )
                logger.info("NLP analysis completed for alert %s", alert_id)

            except Exception as exc:
                fallback_level = normalized.get("niveau") or LEVEL_INFO
                normalized.update(
                    {
                        "niveau": fallback_level,
                        "level": normalized.get("level") or fallback_level,
                        "confidence": normalized.get("confidence") or 0.2,
                        "confiance": normalized.get("confiance") or 0.2,
                        "nlp_enhanced": False,
                        "llm_enhanced": False,
                    }
                )
                logger.exception("NLP analysis failed for alert %s: %s", alert_id, exc)

            enriched_alerts.append(normalized)

        return enriched_alerts

    def _fetch_structured_rasff_alerts(self, limit: int = 30) -> list:
        """Fetch recent structured RASFF alerts with metadata for the NLP model."""
        try:
            logger.info("RegulatoryWatchEngine fetching structured RASFF alerts")
            alerts = self.rasff_client.fetch_latest(max_items=limit, use_cache=True)
            logger.info("Structured RASFF fetch returned %s alert(s)", len(alerts))
            return alerts
        except Exception as exc:
            logger.exception("Structured RASFF fetch failed: %s", exc)
            return []

    def _deduplicate_alerts(self, alerts: list) -> list:
        """Remove duplicates across static rules, structured sources, and RSS."""
        seen = set()
        unique_alerts = []
        for alert in alerts:
            title = self._as_text(alert.get("titre") or alert.get("title")).lower().strip()
            date = self._as_text(alert.get("date"))[:10]
            source = self._as_text(alert.get("source")).lower().strip()
            key = alert.get("id") or hashlib.md5(f"{source}|{date}|{title}".encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            unique_alerts.append(alert)
        return unique_alerts

    def run(
        self,
        hs_code: str,
        product_name: str,
        target_countries: list,
        include_live: bool = True,
    ) -> list:
        """
        Lance la veille réglementaire complète.

        Args:
            hs_code:          Code HS du produit
            product_name:     Nom du produit
            target_countries: Liste ISO3 des marchés cibles
            include_live:     Inclure les flux RSS en temps réel

        Returns:
            Liste d'alertes triées par pertinence décroissante
        """
        print(f"\n📡 Veille réglementaire pour : {product_name} (HS {hs_code})")
        print(f"   Marchés surveillés : {', '.join(target_countries)}\n")

        all_alerts = []

        # ① Base de connaissances statique
        print("  ① Chargement de la base réglementaire...")
        for reg in REGLEMENTATIONS_BASE:
            pays_list = [reg["pays"]] if isinstance(reg["pays"], str) else reg["pays"]
            # Élargir EU → tous les pays UE
            if "EU" in pays_list:
                pays_list = ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL", "GBR"]

            relevance = score_relevance(
                {**reg, "pays": pays_list},
                hs_code,
                target_countries,
                product_name,
            )
            if relevance > 20:
                all_alerts.append({**reg, "pays_list": pays_list, "relevance": relevance})

        # ② Flux RSS en temps réel
        if include_live:
            print("  Collecte RASFF structuree...")
            structured_rasff = self._fetch_structured_rasff_alerts()
            for alert in structured_rasff:
                relevance = score_relevance(alert, hs_code, target_countries, product_name)
                if relevance > 20:
                    all_alerts.append({**alert, "relevance": relevance})
            print(f"     RASFF structure: {len(structured_rasff)} notification(s)")

            print("  ② Collecte des flux RSS en temps réel...")
            for src_name, src_cfg in RSS_SOURCES.items():
                live = fetch_rss_alerts(src_name, src_cfg)
                for alert in live:
                    relevance = score_relevance(alert, hs_code, target_countries, product_name)
                    if relevance > 25:
                        all_alerts.append({**alert, "relevance": relevance})
                if live:
                    print(f"     {src_name}: {len(live)} article(s) pertinent(s)")
                else:
                    print(f"     {src_name}: hors ligne — base statique utilisée")

        # ③ Trier par pertinence puis par niveau
        level_order = {LEVEL_CRITICAL: 0, LEVEL_WARNING: 1, LEVEL_INFO: 2}
        all_alerts.sort(
            key=lambda x: (level_order.get(x.get("niveau", LEVEL_INFO), 2), -x.get("relevance", 0))
        )

        print(f"\n  ✅ {len(all_alerts)} alerte(s) identifiée(s)\n")
        all_alerts = self._deduplicate_alerts(all_alerts)
        all_alerts = self._enrich_alerts_with_nlp(all_alerts, hs_code, target_countries)
        all_alerts.sort(
            key=lambda x: (
                level_order.get(x.get("niveau", LEVEL_INFO), 2),
                -x.get("score_impact", x.get("impact_score", x.get("relevance", 0))),
            )
        )

        return all_alerts

    def get_summary(self, alerts: list) -> dict:
        """Retourne un résumé statistique des alertes."""
        return {
            "total":    len(alerts),
            "critique": sum(1 for a in alerts if a.get("niveau") == LEVEL_CRITICAL),
            "attention": sum(1 for a in alerts if a.get("niveau") == LEVEL_WARNING),
            "info":     sum(1 for a in alerts if a.get("niveau") == LEVEL_INFO),
            "pays_touches": list(set(
                p for a in alerts
                for p in (a.get("pays_list") or ([a["pays"]] if isinstance(a.get("pays"), str) else a.get("pays", [])))
            )),
        }


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE TERMINAL
# ═══════════════════════════════════════════════════════════════

def print_alerts(alerts: list, product_name: str):
    icons = {LEVEL_CRITICAL: "🔴", LEVEL_WARNING: "🟡", LEVEL_INFO: "🟢"}

    print(f"\n{'═'*60}")
    print(f"  ALERTES RÉGLEMENTAIRES — {product_name.upper()}")
    print(f"{'═'*60}")

    for a in alerts:
        icon = icons.get(a.get("niveau", LEVEL_INFO), "⚪")
        print(f"\n  {icon} [{a.get('niveau')}] {a.get('titre', '')[:60]}")
        print(f"     Source : {a.get('source')} · {a.get('date', '')[:10]}")
        print(f"     Impact : {a.get('score_impact', a.get('relevance', 0)):.0f}/100")
        print(f"     Résumé : {a.get('resume', '')[:120]}...")
        if a.get("action"):
            print(f"     Action : {a.get('action', '')[:100]}")

    print(f"\n{'═'*60}\n")


if __name__ == "__main__":
    engine = RegulatoryWatchEngine()
    alerts = engine.run(
        hs_code="151590",
        product_name="Huile d'argan bio",
        target_countries=["FRA", "USA", "JPN", "CAN", "SAU"],
    )
    print_alerts(alerts, "Huile d'argan bio")
    summary = engine.get_summary(alerts)
    print(f"Résumé : {summary['critique']} critique(s) · {summary['attention']} attention(s) · {summary['info']} info(s)")
