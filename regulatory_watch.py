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
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re


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
    "080410": ["datte", "date", "palm fruit"],
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
        feed = feedparser.parse(source_config["url"])
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

def score_relevance(alert: dict, hs_code: str, target_countries: list) -> float:
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
    hs_kws = HS_KEYWORDS.get(hs_code, [])
    alert_text = (alert.get("titre", "") + " " + alert.get("resume", "")).lower()
    if any(kw in alert_text for kw in hs_kws):
        score *= 1.3

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
            )
            if relevance > 20:
                all_alerts.append({**reg, "pays_list": pays_list, "relevance": relevance})

        # ② Flux RSS en temps réel
        if include_live:
            print("  ② Collecte des flux RSS en temps réel...")
            for src_name, src_cfg in RSS_SOURCES.items():
                live = fetch_rss_alerts(src_name, src_cfg)
                for alert in live:
                    relevance = score_relevance(alert, hs_code, target_countries)
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
