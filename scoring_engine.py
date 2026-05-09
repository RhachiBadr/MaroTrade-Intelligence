from services.scoring.scoring_engine import (
    MarketScoringEngine,
    DimensionScore,
    RentabiliteEstimee,
    MarketResult,
    print_results,
)

__all__ = [
    "MarketScoringEngine",
    "DimensionScore",
    "RentabiliteEstimee",
    "MarketResult",
    "print_results",
]

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    engine = MarketScoringEngine()
    results = engine.run(
        product_name="Huile d'argan bio",
        hs_code="151590",
        top_n=5,
        cout_production_usd_kg=8.0,
    )
    print_results(results, "Huile d'argan bio")
