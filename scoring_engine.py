"""
scoring_engine.py — Moteur de scoring C03
Architecture : Score pondéré (60%) + XGBoost (40%) + explications SHAP
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
import shap

from data_sources import (
    get_trade_data, get_accord_score, get_wb_scores,
    get_diaspora, get_logistique
)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION DU MOTEUR
# ═══════════════════════════════════════════════════════════════

# Poids des 6 dimensions (somme = 1.0)
WEIGHTS = {
    "marche":      0.28,   # Taille + croissance du marché
    "accord":      0.22,   # Accord commercial Maroc
    "business":    0.18,   # Facilité des affaires (World Bank)
    "stabilite":   0.12,   # Stabilité politique et risque pays
    "diaspora":    0.10,   # Présence communauté marocaine
    "logistique":  0.10,   # Distance et coût transport
}

# Ratio ensemble final
ENSEMBLE_RATIO = {"weighted": 0.60, "xgboost": 0.40}

# Noms lisibles des features pour les explications
FEATURE_LABELS = {
    "vol_norm":         "Volume importé",
    "growth_norm":      "Croissance des imports",
    "prix_norm":        "Prix moyen pratiqué",
    "accord_norm":      "Accord commercial Maroc",
    "droits_norm":      "Droits de douane",
    "ease_biz_norm":    "Facilité des affaires",
    "rule_law_norm":    "État de droit",
    "stability_norm":   "Stabilité politique",
    "risk_norm":        "Risque pays global",
    "diaspora_norm":    "Population diaspora MRE",
    "transferts_norm":  "Transferts MRE (M USD)",
    "distance_norm":    "Distance logistique",
    "lpi_norm":         "Indice performance logistique",
    "cout_norm":        "Coût transport conteneur",
}


# ═══════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════

@dataclass
class DimensionScore:
    """Score d'une dimension avec détail."""
    nom: str
    score: float          # 0–100
    poids: float          # poids dans le score final
    contribution: float   # score × poids
    detail: dict          # valeurs brutes des indicateurs
    interpretation: str   # texte explicatif

@dataclass
class MarketResult:
    """Résultat complet pour un marché."""
    rank: int
    country_code: str
    country_name: str
    score_final: float        # 0–100
    score_weighted: float     # composante scoring pondéré
    score_xgboost: float      # composante XGBoost
    dimensions: list          # liste de DimensionScore
    shap_values: dict         # contribution SHAP par feature
    top_atouts: list          # 3 meilleurs points forts
    top_risques: list         # risques identifiés
    accord_info: dict
    logistique_info: dict


# ═══════════════════════════════════════════════════════════════
# MOTEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class MarketScoringEngine:
    """
    Moteur de scoring des marchés d'export pour PME marocaines.
    Combine scoring pondéré multi-critères et XGBoost en ensemble.
    """

    def __init__(self):
        self.scaler = MinMaxScaler()
        self.xgb_model = None
        self.explainer = None
        self._is_trained = False

    # ───────────────────────────────────────
    # 1. Construction du dataset de features
    # ───────────────────────────────────────

    def build_feature_matrix(self, trade_df: pd.DataFrame) -> pd.DataFrame:
        """
        Construit la matrice de features enrichie pour tous les pays.
        Fusionne les 6 sources de données.
        """
        rows = []
        for _, row in trade_df.iterrows():
            code = row["country_code"]
            accord   = get_accord_score(code)
            wb       = get_wb_scores(code)
            diaspora = get_diaspora(code)
            logist   = get_logistique(code)

            rows.append({
                "country_code": code,
                "country_name": row["country_name"],
                # Dimension 1 — Marché
                "value_usd":    row["value_usd"],
                "growth_pct":   row.get("growth_pct", 5.0),
                "price_usd_kg": row.get("price_usd_kg", row["value_usd"] / max(row["weight_kg"], 1)),
                # Dimension 2 — Accord commercial
                "droits":       accord["droits"],
                "accord_type":  1.0 if accord["type"] == "ALE" else (0.5 if accord["type"] == "PREF" else 0.0),
                "accord_label": accord["accord"],
                # Dimension 3 — Facilité des affaires
                "ease_business":    wb["ease_business"],
                "rule_of_law":      wb["rule_of_law"],
                "regulatory_qual":  wb["regulatory_quality"],
                # Dimension 4 — Stabilité politique
                "political_stab":   wb["political_stability"],
                "risk_global":      (wb["political_stability"] + wb["rule_of_law"]) / 2,
                # Dimension 5 — Diaspora
                "diaspora_pop":     diaspora["population"],
                "transferts_musd":  diaspora["transferts_musd"],
                # Dimension 6 — Logistique
                "distance_km":      logist["distance_km"],
                "lpi":              logist["lpi"],
                "cout_conteneur":   logist["cout_conteneur_usd"],
            })

        return pd.DataFrame(rows)

    # ───────────────────────────────────────
    # 2. Normalisation
    # ───────────────────────────────────────

    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise toutes les features entre 0 et 1.
        Les features "inversées" (plus c'est bas, mieux c'est) sont inversées.
        """
        n = df.copy()

        def norm(series):
            mn, mx = series.min(), series.max()
            if mx == mn:
                return pd.Series(np.ones(len(series)), index=series.index)
            return (series - mn) / (mx - mn)

        def norm_inv(series):
            return 1 - norm(series)

        # Dimension 1 — Marché (plus grand = mieux, plus croissance = mieux, meilleur prix = mieux)
        n["vol_norm"]    = norm(df["value_usd"])
        n["growth_norm"] = norm(df["growth_pct"])
        n["prix_norm"]   = norm(df["price_usd_kg"])

        # Dimension 2 — Accord (moins de droits = mieux, ALE = mieux)
        n["accord_norm"] = df["accord_type"]
        n["droits_norm"] = norm_inv(df["droits"])

        # Dimension 3 — Business (plus élevé = mieux)
        n["ease_biz_norm"]  = norm(df["ease_business"]) / 100 * df["ease_business"] / 100
        n["ease_biz_norm"]  = df["ease_business"] / 100
        n["rule_law_norm"]  = df["rule_of_law"] / 100
        n["reg_qual_norm"]  = df["regulatory_qual"] / 100

        # Dimension 4 — Stabilité (plus élevé = mieux)
        n["stability_norm"] = df["political_stab"] / 100
        n["risk_norm"]      = df["risk_global"] / 100

        # Dimension 5 — Diaspora (plus grande = mieux)
        n["diaspora_norm"]    = norm(df["diaspora_pop"])
        n["transferts_norm"]  = norm(df["transferts_musd"])

        # Dimension 6 — Logistique (distance → moins = mieux, LPI → plus = mieux, coût → moins = mieux)
        n["distance_norm"] = norm_inv(df["distance_km"])
        n["lpi_norm"]      = (df["lpi"] - 1) / 4       # LPI entre 1–5 → 0–1
        n["cout_norm"]     = norm_inv(df["cout_conteneur"])

        return n

    # ───────────────────────────────────────
    # 3. Scoring pondéré
    # ───────────────────────────────────────

    def compute_weighted_score(self, n: pd.DataFrame) -> pd.Series:
        """
        Calcule le score pondéré pour chaque pays.
        Chaque dimension est une moyenne de ses features normalisées.
        """
        # Score par dimension
        dim_marche    = (n["vol_norm"] * 0.45 + n["growth_norm"] * 0.35 + n["prix_norm"] * 0.20)
        dim_accord    = (n["accord_norm"] * 0.60 + n["droits_norm"] * 0.40)
        dim_business  = (n["ease_biz_norm"] * 0.40 + n["rule_law_norm"] * 0.35 + n["reg_qual_norm"] * 0.25)
        dim_stabilite = (n["stability_norm"] * 0.55 + n["risk_norm"] * 0.45)
        dim_diaspora  = (n["diaspora_norm"] * 0.50 + n["transferts_norm"] * 0.50)
        dim_logist    = (n["distance_norm"] * 0.40 + n["lpi_norm"] * 0.35 + n["cout_norm"] * 0.25)

        score = (
            dim_marche    * WEIGHTS["marche"] +
            dim_accord    * WEIGHTS["accord"] +
            dim_business  * WEIGHTS["business"] +
            dim_stabilite * WEIGHTS["stabilite"] +
            dim_diaspora  * WEIGHTS["diaspora"] +
            dim_logist    * WEIGHTS["logistique"]
        )

        return score * 100  # ramener sur 100

    # ───────────────────────────────────────
    # 4. Entraînement XGBoost
    # ───────────────────────────────────────

    FEATURE_COLS = [
        "vol_norm", "growth_norm", "prix_norm",
        "accord_norm", "droits_norm",
        "ease_biz_norm", "rule_law_norm", "reg_qual_norm",
        "stability_norm", "risk_norm",
        "diaspora_norm", "transferts_norm",
        "distance_norm", "lpi_norm", "cout_norm",
    ]

    def train_xgboost(self, n: pd.DataFrame, weighted_scores: pd.Series):
        """
        Entraîne XGBoost sur les features normalisées.
        Cible = score pondéré (apprentissage supervisé auto-généré).
        On augmente les données avec du bruit pour simuler variance réelle.
        """
        X = n[self.FEATURE_COLS].values
        y = weighted_scores.values / 100

        # Augmentation : 5× avec bruit gaussien léger
        np.random.seed(42)
        X_aug = np.vstack([X + np.random.normal(0, 0.03, X.shape) for _ in range(5)] + [X])
        y_aug = np.tile(y, 6)
        X_aug = np.clip(X_aug, 0, 1)

        self.xgb_model = XGBRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        self.xgb_model.fit(X_aug, y_aug)

        # Explainer SHAP
        self.explainer = shap.TreeExplainer(self.xgb_model)
        self._is_trained = True

    def predict_xgboost(self, n: pd.DataFrame) -> np.ndarray:
        """Prédit le score XGBoost pour tous les pays."""
        X = n[self.FEATURE_COLS].values
        return self.xgb_model.predict(X) * 100

    def get_shap_values(self, n: pd.DataFrame) -> np.ndarray:
        """Calcule les valeurs SHAP pour l'explicabilité."""
        X = n[self.FEATURE_COLS].values
        return self.explainer.shap_values(X)

    # ───────────────────────────────────────
    # 5. Score ensemble final
    # ───────────────────────────────────────

    def ensemble_score(self, weighted: float, xgb: float) -> float:
        """Combine les deux scores en ensemble pondéré."""
        return (
            weighted * ENSEMBLE_RATIO["weighted"] +
            xgb      * ENSEMBLE_RATIO["xgboost"]
        )

    # ───────────────────────────────────────
    # 6. Génération des explications
    # ───────────────────────────────────────

    def build_dimension_scores(self, row: pd.Series, n_row: pd.Series) -> list:
        """Construit les scores détaillés par dimension pour un pays."""
        dimensions = []

        # D1 — Marché
        score_marche = (
            n_row["vol_norm"] * 0.45 +
            n_row["growth_norm"] * 0.35 +
            n_row["prix_norm"] * 0.20
        ) * 100
        dimensions.append(DimensionScore(
            nom="Potentiel de marché",
            score=round(score_marche, 1),
            poids=WEIGHTS["marche"],
            contribution=round(score_marche * WEIGHTS["marche"], 1),
            detail={
                "Volume importé": f"{row['value_usd']/1e6:.1f}M USD/an",
                "Croissance":     f"+{row['growth_pct']:.1f}%/an",
                "Prix moyen":     f"{row['price_usd_kg']:.2f} USD/kg",
            },
            interpretation=self._interpret_marche(row, n_row),
        ))

        # D2 — Accord commercial
        score_accord = (n_row["accord_norm"] * 0.60 + n_row["droits_norm"] * 0.40) * 100
        dimensions.append(DimensionScore(
            nom="Accord commercial",
            score=round(score_accord, 1),
            poids=WEIGHTS["accord"],
            contribution=round(score_accord * WEIGHTS["accord"], 1),
            detail={
                "Type d'accord":  row["accord_label"],
                "Droits de douane": f"{row['droits']:.1f}%",
            },
            interpretation=self._interpret_accord(row),
        ))

        # D3 — Facilité des affaires
        score_biz = (
            n_row["ease_biz_norm"] * 0.40 +
            n_row["rule_law_norm"] * 0.35 +
            n_row["reg_qual_norm"] * 0.25
        ) * 100
        dimensions.append(DimensionScore(
            nom="Facilité des affaires",
            score=round(score_biz, 1),
            poids=WEIGHTS["business"],
            contribution=round(score_biz * WEIGHTS["business"], 1),
            detail={
                "Ease of Business (WB)": f"{row['ease_business']:.1f}/100",
                "État de droit":         f"{row['rule_of_law']:.1f}/100",
                "Qualité réglementaire": f"{row['regulatory_qual']:.1f}/100",
            },
            interpretation=self._interpret_business(row),
        ))

        # D4 — Stabilité
        score_stab = (n_row["stability_norm"] * 0.55 + n_row["risk_norm"] * 0.45) * 100
        dimensions.append(DimensionScore(
            nom="Stabilité & risque pays",
            score=round(score_stab, 1),
            poids=WEIGHTS["stabilite"],
            contribution=round(score_stab * WEIGHTS["stabilite"], 1),
            detail={
                "Stabilité politique": f"{row['political_stab']:.1f}/100",
                "Risque global":       f"{row['risk_global']:.1f}/100",
            },
            interpretation=self._interpret_stabilite(row),
        ))

        # D5 — Diaspora
        score_dias = (n_row["diaspora_norm"] * 0.50 + n_row["transferts_norm"] * 0.50) * 100
        dimensions.append(DimensionScore(
            nom="Diaspora marocaine (MRE)",
            score=round(score_dias, 1),
            poids=WEIGHTS["diaspora"],
            contribution=round(score_dias * WEIGHTS["diaspora"], 1),
            detail={
                "Population MRE":    f"{row['diaspora_pop']:,}",
                "Transferts/an": f"{row['transferts_musd']}M USD",
            },
            interpretation=self._interpret_diaspora(row),
        ))

        # D6 — Logistique
        score_log = (
            n_row["distance_norm"] * 0.40 +
            n_row["lpi_norm"] * 0.35 +
            n_row["cout_norm"] * 0.25
        ) * 100
        dimensions.append(DimensionScore(
            nom="Logistique & transport",
            score=round(score_log, 1),
            poids=WEIGHTS["logistique"],
            contribution=round(score_log * WEIGHTS["logistique"], 1),
            detail={
                "Distance Casablanca": f"{row['distance_km']:,} km",
                "LPI (World Bank)":    f"{row['lpi']:.2f}/5",
                "Coût conteneur":      f"{row['cout_conteneur']:,} USD",
            },
            interpretation=self._interpret_logistique(row),
        ))

        return dimensions

    def _interpret_marche(self, row, n_row):
        parts = []
        if n_row["vol_norm"] > 0.6:
            parts.append(f"Grand marché de {row['value_usd']/1e6:.1f}M USD/an")
        elif n_row["vol_norm"] > 0.3:
            parts.append(f"Marché moyen de {row['value_usd']/1e6:.1f}M USD/an")
        else:
            parts.append(f"Marché de niche, {row['value_usd']/1e6:.1f}M USD/an")
        if row["growth_pct"] > 10:
            parts.append(f"croissance forte (+{row['growth_pct']:.1f}%/an)")
        elif row["growth_pct"] > 5:
            parts.append(f"croissance modérée (+{row['growth_pct']:.1f}%/an)")
        return ", ".join(parts) + "."

    def _interpret_accord(self, row):
        t = row.get("accord_label", "")
        d = row.get("droits", 8.0)
        if d == 0:
            return f"{t} — entrée en franchise de droits, avantage compétitif direct."
        elif d < 5:
            return f"{t} — droits réduits à {d}%, reste avantageux."
        else:
            return f"Pas d'accord préférentiel — droits à {d}%, surveiller la concurrence."

    def _interpret_business(self, row):
        eb = row.get("ease_business", 50)
        if eb > 80:
            return "Environnement très favorable aux affaires, procédures rapides et prévisibles."
        elif eb > 65:
            return "Bon environnement des affaires, quelques formalités à anticiper."
        else:
            return "Environnement des affaires complexe, accompagnement recommandé."

    def _interpret_stabilite(self, row):
        ps = row.get("political_stab", 40)
        if ps > 70:
            return "Pays stable, risque pays faible, paiements sécurisés."
        elif ps > 40:
            return "Stabilité moyenne, surveiller l'évolution du risque."
        else:
            return "Risque pays élevé, sécuriser les paiements (lettre de crédit recommandée)."

    def _interpret_diaspora(self, row):
        pop = row.get("diaspora_pop", 0)
        tr  = row.get("transferts_musd", 0)
        if pop > 500_000:
            return f"Très forte communauté MRE ({pop:,} personnes), réseau commercial naturel."
        elif pop > 50_000:
            return f"Communauté MRE significative ({pop:,}), relais potentiel à l'export."
        elif pop > 0:
            return f"Petite communauté MRE ({pop:,}), impact limité sur les ventes."
        else:
            return "Peu ou pas de diaspora marocaine, approche commerciale classique requise."

    def _interpret_logistique(self, row):
        km  = row.get("distance_km", 10000)
        lpi = row.get("lpi", 2.5)
        if km < 3000 and lpi > 3.5:
            return f"Excellente accessibilité ({km:,} km, LPI {lpi:.1f}/5), délais courts."
        elif km < 5000:
            return f"Bonne accessibilité ({km:,} km), infrastructure logistique satisfaisante."
        else:
            return f"Distance importante ({km:,} km), prévoir délais et coûts de transport élevés."

    def build_shap_dict(self, shap_vals: np.ndarray, idx: int) -> dict:
        """Retourne les valeurs SHAP triées par importance pour un pays."""
        vals = shap_vals[idx]
        result = {}
        for i, col in enumerate(self.FEATURE_COLS):
            label = FEATURE_LABELS.get(col, col)
            result[label] = round(float(vals[i]) * 100, 2)
        return dict(sorted(result.items(), key=lambda x: abs(x[1]), reverse=True))

    def extract_atouts_risques(self, dims: list, shap_dict: dict) -> tuple:
        """Extrait les 3 meilleurs atouts et principaux risques."""
        atouts  = []
        risques = []

        for d in dims:
            if d.score >= 70:
                atouts.append(f"{d.nom} : {d.interpretation}")
            elif d.score < 45:
                risques.append(f"{d.nom} ({d.score:.0f}/100) — {d.interpretation}")

        # Compléter avec SHAP si manque
        for label, val in shap_dict.items():
            if val > 0 and len(atouts) < 3:
                if not any(label in a for a in atouts):
                    atouts.append(f"{label} contribue positivement au score")
            if val < -0.5 and len(risques) < 2:
                if not any(label in r for r in risques):
                    risques.append(f"{label} pèse négativement sur le score")

        return atouts[:3], risques[:2]

    # ───────────────────────────────────────
    # 7. Pipeline principal
    # ───────────────────────────────────────

    def run(self, product_name: str, hs_code: str, top_n: int = 5) -> list:
        """
        Lance le pipeline complet de scoring.
        Retourne une liste de MarketResult triés par score.
        """
        print(f"\n🌍 Analyse en cours pour : {product_name} (HS {hs_code})")

        # Données brutes
        print("  ① Chargement des données commerciales...")
        trade_df = get_trade_data(hs_code)

        # Matrice de features
        print("  ② Construction de la matrice de features (6 dimensions)...")
        df = self.build_feature_matrix(trade_df)

        # Normalisation
        n = self.normalize_features(df)

        # Score pondéré
        print("  ③ Calcul du score pondéré multi-critères...")
        weighted_scores = self.compute_weighted_score(n)

        # XGBoost
        print("  ④ Entraînement et inférence XGBoost...")
        self.train_xgboost(n, weighted_scores)
        xgb_scores = self.predict_xgboost(n)

        # SHAP
        print("  ⑤ Calcul des valeurs SHAP (explicabilité)...")
        shap_vals = self.get_shap_values(n)

        # Score ensemble
        final_scores = np.array([
            self.ensemble_score(w, x)
            for w, x in zip(weighted_scores, xgb_scores)
        ])

        # Normaliser sur 100
        if final_scores.max() > 0:
            final_scores = final_scores / final_scores.max() * 100

        # Trier et construire résultats
        order = np.argsort(final_scores)[::-1]
        results = []

        for rank, idx in enumerate(order[:top_n], start=1):
            row = df.iloc[idx]
            n_row = n.iloc[idx]
            dims = self.build_dimension_scores(row, n_row)
            shap_dict = self.build_shap_dict(shap_vals, idx)
            atouts, risques = self.extract_atouts_risques(dims, shap_dict)

            results.append(MarketResult(
                rank=rank,
                country_code=row["country_code"],
                country_name=row["country_name"],
                score_final=round(float(final_scores[idx]), 1),
                score_weighted=round(float(weighted_scores.iloc[idx]), 1),
                score_xgboost=round(float(xgb_scores[idx]), 1),
                dimensions=dims,
                shap_values=shap_dict,
                top_atouts=atouts,
                top_risques=risques,
                accord_info=get_accord_score(row["country_code"]),
                logistique_info=get_logistique(row["country_code"]),
            ))

        print(f"\n✅ Analyse terminée — Top {top_n} marchés identifiés.\n")
        return results


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE TERMINAL
# ═══════════════════════════════════════════════════════════════

def print_results(results: list, product_name: str):
    print(f"\n{'═'*60}")
    print(f"  MARCHÉS PRIORITAIRES — {product_name.upper()}")
    print(f"{'═'*60}")

    for r in results:
        bar = "█" * int(r.score_final / 5) + "░" * (20 - int(r.score_final / 5))
        print(f"\n  #{r.rank}  {r.country_name:<20} {bar} {r.score_final:.1f}/100")
        print(f"       Score pondéré: {r.score_weighted:.1f}  |  XGBoost: {r.score_xgboost:.1f}")
        print(f"       Accord: {r.accord_info['accord']}")

        print(f"\n       Dimensions:")
        for d in r.dimensions:
            bar_d = "▓" * int(d.score / 10) + "░" * (10 - int(d.score / 10))
            print(f"         {d.nom:<30} {bar_d} {d.score:.0f}/100")

        print(f"\n       Atouts:")
        for a in r.top_atouts:
            print(f"         ✓ {a}")

        if r.top_risques:
            print(f"\n       Risques:")
            for ri in r.top_risques:
                print(f"         ⚠ {ri}")

    print(f"\n{'═'*60}\n")


if __name__ == "__main__":
    engine = MarketScoringEngine()
    results = engine.run("Huile d'argan bio", "151590", top_n=5)
    print_results(results, "Huile d'argan bio")
