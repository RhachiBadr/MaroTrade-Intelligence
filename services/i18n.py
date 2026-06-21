"""Small centralized localization layer for user-facing API messages."""

from typing import Any


API_MESSAGES = {
    "en": {
        "Moteur de scoring non chargé.": "Scoring engine is not loaded.",
        "Moteur de veille non chargé.": "Regulatory watch engine is not loaded.",
        "Analyse introuvable dans votre espace PME.": "Analysis not found in your SME workspace.",
        "Base utilisateurs indisponible. Démarrez PostgreSQL puis exécutez Prisma.": (
            "User database unavailable. Start PostgreSQL and run Prisma."
        ),
        "Session invalide ou expirée.": "Invalid or expired session.",
        "Authentification requise.": "Authentication required.",
        "Droits insuffisants.": "Insufficient permissions.",
        "Email ou mot de passe incorrect.": "Incorrect email or password.",
        "Un compte existe déjà avec cet email.": "An account already exists with this email.",
        "Aucune PME active associée à ce compte.": "No active SME workspace is associated with this account.",
        "Espace PME désactivé.": "SME workspace is disabled.",
        "Session invalide.": "Invalid session.",
        "Jeton de vérification invalide ou expiré.": "Invalid or expired verification token.",
        "Jeton de réinitialisation invalide ou expiré.": "Invalid or expired reset token.",
        "Endpoint Forecast en cours de construction.": "Forecast endpoint is under construction.",
    }
}


def request_locale(accept_language: str | None) -> str:
    return "en" if (accept_language or "").lower().startswith("en") else "fr"


def localize_api_message(message: Any, locale: str) -> Any:
    if not isinstance(message, str) or locale == "fr":
        return message
    direct = API_MESSAGES["en"].get(message)
    if direct:
        return direct
    if message.startswith("Échec de la veille réglementaire :"):
        return message.replace("Échec de la veille réglementaire :", "Regulatory watch failed:", 1)
    return message
