"""Module de service de scoring.

Ce package est le point d'entrée pour le service de scoring métier.
Il expose `MarketScoringEngine` pour être utilisé depuis l'API.
"""

# Import différé
def __getattr__(name):
    if name == "MarketScoringEngine":
        from services.scoring.scoring_engine import MarketScoringEngine
        return MarketScoringEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["MarketScoringEngine"]
