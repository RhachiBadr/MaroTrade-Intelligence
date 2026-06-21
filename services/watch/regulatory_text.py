"""French presentation helpers for regulatory alerts.

The classifier works on the original multilingual text. These helpers are
applied only after inference to create concise, user-facing French content.
"""

import re


COUNTRIES_FR = {
    "argentina": "Argentine",
    "belgium": "Belgique",
    "colombia": "Colombie",
    "egypt": "Égypte",
    "france": "France",
    "germany": "Allemagne",
    "india": "Inde",
    "italy": "Italie",
    "morocco": "Maroc",
    "netherlands": "Pays-Bas",
    "nigeria": "Nigeria",
    "poland": "Pologne",
    "rwanda": "Rwanda",
    "south africa": "Afrique du Sud",
    "spain": "Espagne",
    "thailand": "Thaïlande",
}

CATEGORIES_FR = {
    "cereals and bakery products": "céréales et produits de boulangerie",
    "fish and fish products": "poissons et produits de la pêche",
    "fruits and vegetables": "fruits et légumes",
    "herbs and spices": "herbes et épices",
    "milk and milk products": "lait et produits laitiers",
    "nuts, nut products and seeds": "fruits à coque, produits dérivés et graines",
    "poultry meat and poultry meat products": "viande de volaille et produits dérivés",
}

CLASSIFICATIONS_FR = {
    "alert notification": "notification d’alerte",
    "border rejection notification": "notification de rejet à la frontière",
    "information notification for attention": "notification d’information nécessitant une attention",
    "information notification for follow-up": "notification d’information pour suivi",
}

PHRASES_FR = {
    "company": "l’entreprise",
    "announces voluntary recall of": "annonce le rappel volontaire de",
    "voluntary recall of": "rappel volontaire de",
    "due to possible": "en raison d’un risque possible de",
    "due to potential": "en raison d’un risque potentiel de",
    "undeclared allergen": "allergène non déclaré",
    "undeclared": "présence non déclarée de",
    "presence of": "présence de",
    "detection of": "détection de",
    "excessive levels of": "teneurs excessives en",
    "above mrl": "au-dessus de la limite maximale de résidus",
    "pesticide residues": "résidus de pesticides",
    "turkey meat": "viande de dinde",
    "chicken meat": "viande de poulet",
    "sesame seeds": "graines de sésame",
    "sunflower seeds": "graines de tournesol",
    "smoked salmon": "saumon fumé",
    "cold-smoked salmon": "saumon fumé à froid",
    "cheese": "fromage",
    "vegetable oil": "huile végétale",
    "oil": "huile",
    "in": "dans",
    "from": "originaire de",
}

FRENCH_MARKERS = {
    " le ", " la ", " les ", " des ", " une ", " dans ", " avec ", " origine ",
    " présence ", " détection ", " règlement ", " droits ", " maroc ",
    " certification ", " biologique ", " mécanisme ", " loi ", " obligatoire ",
}


def _clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _translate_country(value: str) -> str:
    clean = _clean(value)
    return COUNTRIES_FR.get(clean.lower(), clean)


def _translate_term(value: str, mapping: dict[str, str]) -> str:
    clean = _clean(value)
    return mapping.get(clean.lower(), clean)


def is_probably_french(value: str) -> bool:
    text = f" {_clean(value).lower()} "
    if not text.strip():
        return False
    if re.search(r"[àâçéèêëîïôùûüÿœ]", text):
        return True
    return sum(marker in text for marker in FRENCH_MARKERS) >= 2


def translate_regulatory_title(title: str, origin: str = "") -> str:
    """Translate common RASFF title patterns without altering scientific names."""
    clean = _clean(title).split(" | ", 1)[0]
    if not clean or is_probably_french(clean):
        return clean

    translated = clean
    for english, french in sorted(PHRASES_FR.items(), key=lambda item: -len(item[0])):
        translated = re.sub(rf"\b{re.escape(english)}\b", french, translated, flags=re.IGNORECASE)

    for english, french in COUNTRIES_FR.items():
        translated = re.sub(rf"\b{re.escape(english)}\b", french, translated, flags=re.IGNORECASE)

    translated = re.sub(r"\s*//\s*", " / ", translated)
    translated = re.sub(r"\bdans viande\b", "dans de la viande", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bdans graines\b", "dans des graines", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bdans saumon\b", "dans du saumon", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bdans fromage\b", "dans du fromage", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bde huile\b", "d’huile", translated, flags=re.IGNORECASE)
    translated = _clean(translated).rstrip(".")
    if origin and "originaire de" not in translated.lower():
        translated = f"{translated} — origine : {_translate_country(origin)}"
    translated = translated[:220]
    return translated[:1].upper() + translated[1:]


def build_french_summary(alert: dict, title_fr: str) -> str:
    """Build a concise factual summary from reliable source metadata."""
    source = _clean(alert.get("source")).upper()
    category = _translate_term(alert.get("category", ""), CATEGORIES_FR)
    classification = _translate_term(alert.get("classification", ""), CLASSIFICATIONS_FR)
    origin = _translate_country(alert.get("origin", ""))

    if source == "RASFF":
        details = []
        if classification:
            details.append(classification)
        if category:
            details.append(f"catégorie : {category}")
        if origin:
            details.append(f"origine : {origin}")
        suffix = f" ({'; '.join(details)})" if details else ""
        return f"Le réseau RASFF signale : {title_fr.rstrip('.')}{suffix}."

    if source == "FDA":
        return f"La FDA signale : {title_fr.rstrip('.')}."

    if alert.get("live") and source:
        return f"La source {source} publie l’alerte suivante : {title_fr.rstrip('.')}."

    existing = _clean(alert.get("resume_fr") or alert.get("resume") or alert.get("summary"))
    return existing or title_fr


def build_business_explanation(
    final_level: str,
    model_level: str,
    relevance: float,
    product_match,
    calibration_reason: str,
    classification_basis: str = "",
) -> str:
    """Explain the final decision in plain French for SMEs and audit."""
    if classification_basis == "curated_source_level":
        return (
            f"Priorité {final_level} définie à partir de la réglementation de référence, puis vérifiée "
            f"selon sa pertinence pour le produit et les marchés suivis ({relevance:.0f}/100)."
        )
    if product_match is False:
        return (
            f"Priorité {final_level} : le danger détecté peut être sérieux, mais l’alerte ne concerne "
            f"pas directement le produit surveillé. Pertinence export : {relevance:.0f}/100."
        )
    if final_level != model_level:
        return (
            f"Priorité {final_level} après calibration métier : signal initial {model_level}, "
            f"ajusté selon la pertinence produit/marché ({relevance:.0f}/100), la source et l’impact."
        )
    if "confirmed:" in (calibration_reason or ""):
        return (
            f"Priorité {final_level} confirmée : le danger, le type de notification et la pertinence "
            "export justifient une action rapide."
        )
    return (
        f"Priorité {final_level} confirmée après analyse du texte, des métadonnées réglementaires "
        f"et de la pertinence export ({relevance:.0f}/100)."
    )


def build_french_action(alert: dict) -> str:
    """Return an actionable French recommendation for live RASFF alerts."""
    if _clean(alert.get("source")).upper() != "RASFF":
        existing = _clean(alert.get("action") or alert.get("action_requise"))
        if existing:
            return existing
        if _clean(alert.get("source")).upper() == "FDA":
            return "Vérifier si le produit, le fournisseur ou un lot exporté est concerné par le rappel."
        return ""
    if alert.get("product_match") is False:
        return "Aucune action immédiate sur ce produit ; conserver l’alerte en veille sectorielle."
    if alert.get("niveau") == "CRITIQUE":
        return "Suspendre l’expédition concernée et vérifier immédiatement les analyses et certificats sanitaires."
    if alert.get("niveau") == "ATTENTION":
        return "Vérifier la conformité sanitaire et documentaire avant la prochaine expédition."
    return "Conserver cette notification en veille et vérifier son évolution auprès de la source officielle."
