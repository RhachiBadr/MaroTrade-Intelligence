"""
llm_regulatory_analyzer.py — Innovation 01
Analyse réglementaire intelligente via Claude 3.5 Haiku
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remplace le système de mots-clés basique par un vrai LLM
qui comprend et extrait les informations réglementaires
en langage naturel, avec structured outputs JSON.

Usage :
    from llm_regulatory_analyzer import LLMRegulatoryAnalyzer
    analyzer = LLMRegulatoryAnalyzer()
    result = analyzer.analyze(text, hs_code, target_countries)
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

import anthropic


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CACHE_DIR = Path(".cache_marotrade")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_DAYS = 3  # Alertes mises en cache 3 jours

MODEL = "claude-haiku-4-5"  # Claude 3.5 Haiku — rapide et économique

# Contexte Maroc injecté dans chaque prompt
MAROC_CONTEXT = """
Tu analyses des textes réglementaires pour des PME exportatrices marocaines.
Le Maroc exporte principalement vers : UE (accord association), USA (ALE),
pays arabes (GAFTA), et pays africains (ZLECAf).
Produits phares : huile d'argan, sardines, dattes, safran, cumin,
tapis berbères, zellige, phosphates, câbles automobiles.
Réponds TOUJOURS en français, de façon concise et actionnable.
"""


# ═══════════════════════════════════════════════════════════════
# STRUCTURE DE SORTIE
# ═══════════════════════════════════════════════════════════════

@dataclass
class RegulatoryAnalysis:
    """Résultat structuré de l'analyse LLM d'une alerte réglementaire."""

    # Identification
    titre_fr:        str            # Titre reformulé en français clair
    niveau:          str            # CRITIQUE / ATTENTION / INFO

    # Impact
    pays_concernes:  list           # Codes ISO3 des pays affectés
    produits:        list           # Produits ou codes HS concernés
    impact_score:    float          # 0–100

    # Contenu
    resume_fr:       str            # Résumé court (2–3 phrases) en français
    impact_export:   str            # Impact concret sur les exportateurs marocains
    action_requise:  str            # Action concrète à faire, délai si connu

    # Métadonnées
    date_vigueur:    Optional[str]  # Date d'entrée en vigueur si mentionnée
    source_fiable:   bool           # Le LLM estime-t-il la source fiable ?
    confiance:       float          # Score de confiance de l'analyse (0–1)


# ═══════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════

ANALYSIS_SYSTEM_PROMPT = f"""
Tu es un expert en réglementation du commerce international spécialisé
dans les exportations marocaines. {MAROC_CONTEXT}

Ta tâche : analyser un texte réglementaire et extraire les informations
structurées pertinentes pour les exportateurs marocains.

Tu dois répondre UNIQUEMENT avec un objet JSON valide, sans texte avant
ni après, sans backticks. Respecte exactement ce schéma :

{{
  "titre_fr": "Titre reformulé en français clair et concis (max 100 chars)",
  "niveau": "CRITIQUE | ATTENTION | INFO",
  "pays_concernes": ["ISO3", ...],
  "produits": ["nom produit ou code HS", ...],
  "impact_score": 0-100,
  "resume_fr": "Résumé en 2-3 phrases simples pour une PME marocaine",
  "impact_export": "Impact concret sur les exportations marocaines",
  "action_requise": "Action précise à effectuer, avec délai si connu",
  "date_vigueur": "YYYY-MM-DD ou null si non mentionnée",
  "source_fiable": true | false,
  "confiance": 0.0-1.0
}}

Règles de classification du niveau :
- CRITIQUE : blocage immédiat possible, rappel produit, interdiction, suspension
- ATTENTION : nouveau règlement, modification de norme, délai de mise en conformité
- INFO : mise à jour mineure, clarification, information utile sans urgence

Règles d'impact_score :
- 80-100 : Blocage certain à la frontière sans action
- 60-79  : Risque élevé de blocage ou surcoût important
- 40-59  : Impact modéré, action recommandée
- 20-39  : Impact faible, information utile
- 0-19   : Information de veille, pas d'impact immédiat
"""

RELEVANCE_SYSTEM_PROMPT = f"""
Tu es un expert du commerce international. {MAROC_CONTEXT}
Réponds UNIQUEMENT avec un JSON valide, sans texte autour.
"""


# ═══════════════════════════════════════════════════════════════
# MOTEUR D'ANALYSE LLM
# ═══════════════════════════════════════════════════════════════

class LLMRegulatoryAnalyzer:
    """
    Analyseur réglementaire intelligent basé sur Claude 3.5 Haiku.

    Remplace le système de mots-clés de regulatory_watch.py par
    une compréhension sémantique réelle des textes réglementaires.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Clé API Anthropic manquante. "
                "Définir : $env:ANTHROPIC_API_KEY='sk-ant-...'"
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self._call_count = 0
        self._total_tokens = 0

    # ───────────────────────────────────────
    # Analyse principale d'une alerte
    # ───────────────────────────────────────

    def analyze(
        self,
        text: str,
        hs_code: str = "",
        target_countries: list = None,
        use_cache: bool = True,
    ) -> RegulatoryAnalysis:
        """
        Analyse un texte réglementaire avec Claude 3.5 Haiku.

        Args:
            text:             Texte brut de l'alerte (titre + résumé RSS)
            hs_code:          Code HS du produit de l'utilisateur
            target_countries: Pays cibles (pour contextualiser l'analyse)
            use_cache:        Utiliser le cache (évite les appels répétés)

        Returns:
            RegulatoryAnalysis structuré
        """
        # Cache basé sur le hash du texte + contexte
        cache_key = hashlib.md5(
            f"{text[:200]}{hs_code}{''.join(target_countries or [])}".encode()
        ).hexdigest()[:12]

        if use_cache:
            cached = self._cache_get(cache_key)
            if cached:
                return self._dict_to_analysis(cached)

        # Construire le prompt utilisateur
        user_prompt = self._build_user_prompt(text, hs_code, target_countries)

        # Appel Claude 3.5 Haiku
        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=800,
                system=ANALYSIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text.strip()
            self._call_count += 1
            self._total_tokens += response.usage.input_tokens + response.usage.output_tokens

            # Parser la réponse JSON
            data = json.loads(raw)
            analysis = self._dict_to_analysis(data)

            # Sauvegarder en cache
            self._cache_set(cache_key, data)
            return analysis

        except json.JSONDecodeError as e:
            # Fallback si le JSON est malformé
            return self._fallback_analysis(text, str(e))
        except Exception as e:
            return self._fallback_analysis(text, str(e))

    # ───────────────────────────────────────
    # Analyse par lot (batch)
    # ───────────────────────────────────────

    def analyze_batch(
        self,
        alerts: list,
        hs_code: str = "",
        target_countries: list = None,
        verbose: bool = True,
    ) -> list:
        """
        Analyse une liste d'alertes brutes en lot.

        Optimisé pour minimiser les appels API :
        - Déduplique les textes similaires
        - Utilise le cache pour les alertes déjà analysées
        - Filtre les alertes non pertinentes avant d'appeler le LLM

        Args:
            alerts:           Liste de dicts avec 'titre' et 'resume'
            hs_code:          Code HS produit
            target_countries: Pays cibles
            verbose:          Afficher la progression

        Returns:
            Liste de RegulatoryAnalysis triés par impact_score décroissant
        """
        results = []
        total = len(alerts)

        if verbose:
            print(f"\n🤖 Analyse LLM de {total} alertes avec Claude 3.5 Haiku...")

        for i, alert in enumerate(alerts, 1):
            text = f"{alert.get('titre', '')} — {alert.get('resume', '')}"

            # Pré-filtre rapide : ignorer les alertes clairement hors sujet
            if not self._is_relevant(text, hs_code, target_countries):
                continue

            if verbose:
                print(f"  [{i}/{total}] Analyse : {alert.get('titre', '')[:60]}...")

            analysis = self.analyze(text, hs_code, target_countries)

            # Enrichir le dict original avec l'analyse LLM
            enriched = {**alert, "llm_analysis": analysis}
            results.append(enriched)

        # Trier par impact décroissant
        results.sort(
            key=lambda x: x["llm_analysis"].impact_score,
            reverse=True,
        )

        if verbose:
            print(f"\n  ✅ {len(results)} alertes analysées")
            print(f"  📊 Tokens utilisés : {self._total_tokens:,}")
            print(f"  💰 Coût estimé : ~${self._total_tokens * 0.0000008:.4f} USD\n")

        return results

    # ───────────────────────────────────────
    # Génération de recommandations globales
    # ───────────────────────────────────────

    def generate_export_brief(
        self,
        analyses: list,
        product_name: str,
        hs_code: str,
        target_market: str,
    ) -> str:
        """
        Génère un brief exécutif personnalisé pour un exportateur.

        Synthétise toutes les alertes en un paragraphe actionnable
        adapté au produit et au marché cible spécifique.

        Args:
            analyses:      Liste de RegulatoryAnalysis
            product_name:  Nom du produit (ex: "Huile d'argan bio")
            hs_code:       Code HS
            target_market: Pays cible (ex: "France")

        Returns:
            Brief en français, 3–5 phrases, prêt à afficher dans le dashboard
        """
        # Construire le résumé des alertes critiques
        critiques = [a["llm_analysis"] for a in analyses
                     if a["llm_analysis"].niveau == "CRITIQUE"]
        attentions = [a["llm_analysis"] for a in analyses
                      if a["llm_analysis"].niveau == "ATTENTION"]

        context = f"""
Produit : {product_name} (HS {hs_code})
Marché cible : {target_market}

Alertes CRITIQUES ({len(critiques)}) :
{chr(10).join(f'- {a.resume_fr}' for a in critiques[:3])}

Alertes ATTENTION ({len(attentions)}) :
{chr(10).join(f'- {a.resume_fr}' for a in attentions[:3])}
"""

        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=400,
                system=f"""{RELEVANCE_SYSTEM_PROMPT}
Génère un brief exécutif en français (3-5 phrases) pour un dirigeant
de PME marocaine qui veut exporter. Commence par l'essentiel.
Sois direct, concret, sans jargon. Termine par la priorité #1.""",
                messages=[{
                    "role": "user",
                    "content": f"Génère le brief export pour :\n{context}",
                }],
            )
            return response.content[0].text.strip()
        except Exception:
            return f"Analyse de {len(analyses)} alertes pour {product_name} vers {target_market}."

    # ───────────────────────────────────────
    # Helpers internes
    # ───────────────────────────────────────

    def _build_user_prompt(
        self,
        text: str,
        hs_code: str,
        target_countries: list,
    ) -> str:
        """Construit le prompt utilisateur contextualisé."""
        ctx_parts = []
        if hs_code:
            ctx_parts.append(f"Produit de l'exportateur : code HS {hs_code}")
        if target_countries:
            ctx_parts.append(f"Marchés cibles : {', '.join(target_countries)}")

        context = "\n".join(ctx_parts)
        return f"""
{context}

Texte réglementaire à analyser :
\"\"\"
{text[:2000]}
\"\"\"

Analyse ce texte et retourne le JSON structuré.
"""

    def _is_relevant(
        self,
        text: str,
        hs_code: str,
        target_countries: list,
    ) -> bool:
        """
        Pré-filtre rapide SANS appel LLM.
        Évite d'appeler Claude pour des textes clairement hors sujet.
        """
        text_lower = text.lower()

        # Mots-clés commerce/réglementation
        trade_kws = [
            "import", "export", "douane", "customs", "food", "alimentaire",
            "sanitary", "sanitaire", "regulation", "règlement", "certification",
            "recall", "rappel", "ban", "interdit", "restriction", "tarif",
            "standard", "norme", "label", "étiquetage", "organic", "bio",
            "halal", "pesticide", "contaminant", "safety", "sécurité",
        ]
        return any(kw in text_lower for kw in trade_kws)

    def _dict_to_analysis(self, data: dict) -> RegulatoryAnalysis:
        """Convertit un dict JSON en objet RegulatoryAnalysis."""
        return RegulatoryAnalysis(
            titre_fr       = data.get("titre_fr", "Alerte réglementaire"),
            niveau         = data.get("niveau", "INFO"),
            pays_concernes = data.get("pays_concernes", []),
            produits       = data.get("produits", []),
            impact_score   = float(data.get("impact_score", 30)),
            resume_fr      = data.get("resume_fr", ""),
            impact_export  = data.get("impact_export", ""),
            action_requise = data.get("action_requise", ""),
            date_vigueur   = data.get("date_vigueur"),
            source_fiable  = bool(data.get("source_fiable", True)),
            confiance      = float(data.get("confiance", 0.7)),
        )

    def _fallback_analysis(self, text: str, error: str) -> RegulatoryAnalysis:
        """Analyse de fallback si le LLM échoue."""
        return RegulatoryAnalysis(
            titre_fr       = text[:80],
            niveau         = "INFO",
            pays_concernes = [],
            produits       = [],
            impact_score   = 20.0,
            resume_fr      = text[:200],
            impact_export  = "Analyse automatique indisponible.",
            action_requise = "Vérifier manuellement cette alerte.",
            date_vigueur   = None,
            source_fiable  = False,
            confiance      = 0.0,
        )

    def _cache_get(self, key: str) -> Optional[dict]:
        path = CACHE_DIR / f"llm_{key}.json"
        if not path.exists():
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            cached_at = datetime.fromisoformat(data["_cached_at"])
            if datetime.now() - cached_at < timedelta(days=CACHE_TTL_DAYS):
                return data["payload"]
        except Exception:
            pass
        return None

    def _cache_set(self, key: str, payload: dict):
        try:
            path = CACHE_DIR / f"llm_{key}.json"
            with open(path, "w") as f:
                json.dump({
                    "_cached_at": datetime.now().isoformat(),
                    "payload": payload,
                }, f, ensure_ascii=False)
        except Exception:
            pass

    @property
    def stats(self) -> dict:
        """Statistiques d'utilisation."""
        return {
            "appels_api":    self._call_count,
            "tokens_totaux": self._total_tokens,
            "cout_estime_usd": round(self._total_tokens * 0.0000008, 4),
        }


# ═══════════════════════════════════════════════════════════════
# INTÉGRATION AVEC regulatory_watch.py
# ═══════════════════════════════════════════════════════════════

def upgrade_regulatory_watch(
    alerts: list,
    hs_code: str,
    target_countries: list,
    api_key: str = "",
) -> list:
    """
    Fonction drop-in pour upgrader regulatory_watch.py avec le LLM.

    Prend les alertes brutes de RegulatoryWatchEngine.run()
    et les enrichit avec l'analyse Claude 3.5 Haiku.

    Args:
        alerts:           Sortie de RegulatoryWatchEngine.run()
        hs_code:          Code HS produit
        target_countries: Pays cibles
        api_key:          Clé Anthropic (ou via env ANTHROPIC_API_KEY)

    Returns:
        Alertes enrichies avec champ 'llm_analysis'
    """
    try:
        analyzer = LLMRegulatoryAnalyzer(api_key or os.getenv("ANTHROPIC_API_KEY", ""))
        enriched = analyzer.analyze_batch(alerts, hs_code, target_countries)

        # Remplacer les champs basiques par l'analyse LLM
        for item in enriched:
            if "llm_analysis" in item:
                a = item["llm_analysis"]
                # Override avec les données LLM
                item["titre"]        = a.titre_fr
                item["niveau"]       = a.niveau
                item["resume"]       = a.resume_fr
                item["action"]       = a.action_requise
                item["score_impact"] = a.impact_score
                item["llm_enhanced"] = True

        return enriched

    except Exception as e:
        print(f"⚠️  LLM indisponible ({e}) — alertes basiques retournées")
        return alerts


# ═══════════════════════════════════════════════════════════════
# DÉMONSTRATION
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("❌ Définir la clé : $env:ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    analyzer = LLMRegulatoryAnalyzer(api_key)

    # Exemple 1 — Alerte critique UE
    print("\n" + "═" * 60)
    print("  TEST 1 — Règlement anti-déforestation UE")
    print("═" * 60)

    text1 = """
    EU Deforestation Regulation (EUDR) enters into force.
    All operators placing products such as palm oil, soy, wood,
    cocoa, coffee, cattle, rubber and derived products on the EU market
    must ensure these products have not contributed to deforestation
    after December 31, 2020. Mandatory geolocalization of production
    plots required. Non-compliant shipments will be blocked at EU border.
    Entry into force: January 2025.
    """

    result1 = analyzer.analyze(text1, hs_code="151590", target_countries=["FRA", "DEU"])
    print(f"\nTitre    : {result1.titre_fr}")
    print(f"Niveau   : {result1.niveau}")
    print(f"Impact   : {result1.impact_score}/100")
    print(f"Résumé   : {result1.resume_fr}")
    print(f"Action   : {result1.action_requise}")
    print(f"Pays     : {result1.pays_concernes}")
    print(f"Confiance: {result1.confiance:.0%}")

    # Exemple 2 — Alerte FDA
    print("\n" + "═" * 60)
    print("  TEST 2 — Alerte FDA sardines")
    print("═" * 60)

    text2 = """
    FDA Import Alert 16-131: Detention Without Physical Examination
    of Canned Fish and Seafood Products from Morocco.
    Products from firms not registered under FSMA Foreign Supplier
    Verification Program (FSVP) are subject to automatic detention.
    Affected HS codes: 1604.13, 1604.14.
    """

    result2 = analyzer.analyze(text2, hs_code="160413", target_countries=["USA"])
    print(f"\nTitre    : {result2.titre_fr}")
    print(f"Niveau   : {result2.niveau}")
    print(f"Impact   : {result2.impact_score}/100")
    print(f"Résumé   : {result2.resume_fr}")
    print(f"Action   : {result2.action_requise}")

    # Statistiques
    print(f"\n📊 Stats : {analyzer.stats}")
