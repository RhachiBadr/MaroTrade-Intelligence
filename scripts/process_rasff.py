"""
prepare_rasff_data.py
=====================
Préparation des données RASFF pour le projet MaroTrade Intelligence.
Produit 3 datasets NLP prêts à l'emploi :
  - rasff_nlp_dataset.csv      : toutes les alertes
  - rasff_maroc_dataset.csv    : produits pertinents pour le Maroc
  - nlp_dataset_combined.csv   : RASFF + FDA fusionnés (si FDA disponible)
"""

import pandas as pd
from pathlib import Path


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

INPUT_RASFF  = Path('data/raw/RASFF_window.csv')
INPUT_FDA    = Path('data/raw/fda_alerts.csv')
OUTPUT_DIR   = Path('data/raw')

# Catégories de produits pertinentes pour le Maroc
MAROC_CATS = [
    'herbs and spices',
    'fish and fish products',
    'fruits and vegetables',
    'nuts, nut products and seeds',
    'oils and fats',
    'cereals and bakery products',
    'dietetic foods, food supplements and fortified foods',
]


# ─────────────────────────────────────────────
# ÉTAPE 1 — Lecture du fichier RASFF
# ─────────────────────────────────────────────

def load_rasff(path: Path) -> pd.DataFrame:
    print(f"Lecture de {path.name} ...")
    df = pd.read_csv(
        path,
        encoding='utf-8',
        on_bad_lines='skip',
        engine='python'
    )
    print(f"  → {df.shape[0]} lignes chargées, {df.shape[1]} colonnes")
    return df


# ─────────────────────────────────────────────
# ÉTAPE 2 — Mapping niveau d'alerte
# ─────────────────────────────────────────────

def map_niveau(row) -> str:
    """
    Simplifie les alertes en 3 niveaux :
      CRITIQUE  → risque grave / refus frontière
      ATTENTION → risque potentiel
      INFO      → information générale
    """
    risk = str(row.get('risk_decision', '')).lower()
    cls  = str(row.get('classification', '')).lower()

    if risk == 'serious' or 'alert' in cls or 'border rejection' in cls:
        return 'CRITIQUE'
    elif risk in ['potentially serious', 'potential risk']:
        return 'ATTENTION'
    else:
        return 'INFO'


# ─────────────────────────────────────────────
# ÉTAPE 3 — Construction du texte NLP
# ─────────────────────────────────────────────

def build_texte(df: pd.DataFrame) -> pd.Series:
    """
    Fusionne subject + category + hazards + origin
    en une seule phrase pour l'analyse NLP.
    Exemple : "Pesticides in tomatoes | fruits and vegetables | chlorpyrifos | Morocco"
    """
    return (
        df['subject'].fillna('') + ' | ' +
        df['category'].fillna('') + ' | ' +
        df['hazards'].fillna('') + ' | ' +
        df['origin'].fillna('')
    )


# ─────────────────────────────────────────────
# ÉTAPE 4 — Features supplémentaires
# ─────────────────────────────────────────────

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute année, mois et flag pertinence Maroc."""
    dates        = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df['year']   = dates.dt.year
    df['month']  = dates.dt.month

    maroc_cats_lower = [c.lower() for c in MAROC_CATS]
    df['maroc_relevant'] = df['category'].str.lower().isin(maroc_cats_lower).astype(int)

    return df


# ─────────────────────────────────────────────
# ÉTAPE 5 — Fusion avec FDA (optionnel)
# ─────────────────────────────────────────────

def load_fda(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        print(f"\nFichier FDA non trouvé ({path}) — étape fusion ignorée.")
        return None

    print(f"\nLecture de {path.name} ...")
    fda_df = pd.read_csv(path)

    fda_df['texte'] = (
        fda_df['product'].fillna('') + ' | ' +
        fda_df['reason'].fillna('')
    )
    fda_df['niveau'] = fda_df['classification'].apply(
        lambda x: 'CRITIQUE'  if 'Class I'  in str(x) else
                  'ATTENTION' if 'Class II' in str(x) else
                  'INFO'
    )
    fda_df['source'] = 'FDA'
    print(f"  → {len(fda_df)} alertes FDA chargées")
    return fda_df[['texte', 'niveau', 'source']]


# ─────────────────────────────────────────────
# ÉTAPE 6 — Résumé des fichiers produits
# ─────────────────────────────────────────────

def print_summary(output_dir: Path) -> None:
    print()
    print('=' * 60)
    print('RÉSUMÉ DATASETS DISPONIBLES')
    print('=' * 60)
    for f in sorted(output_dir.glob('*.csv')):
        try:
            with open(f, encoding='utf-8') as fh:
                lines = sum(1 for _ in fh) - 1
            size = f.stat().st_size / 1024
            print(f"  {f.name:<42} {lines:>8} lignes  {size:>8.1f} KB")
        except Exception:
            print(f"  {f.name:<42} (erreur lecture)")


# ─────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Charger RASFF
    df = load_rasff(INPUT_RASFF)

    # 2. Niveau d'alerte
    print("\nCalcul des niveaux d'alerte ...")
    df['niveau'] = df.apply(map_niveau, axis=1)

    # 3. Texte NLP
    print("Construction du texte NLP ...")
    df['texte'] = build_texte(df)

    # 4. Features
    print("Ajout des features (année, mois, maroc_relevant) ...")
    df = add_features(df)

    # 5. Dataset NLP complet
    nlp_cols = ['texte', 'niveau', 'category', 'classification',
                'risk_decision', 'origin', 'year', 'month', 'maroc_relevant']
    nlp_df = df[nlp_cols].copy()

    out_nlp = OUTPUT_DIR / 'rasff_nlp_dataset.csv'
    nlp_df.to_csv(out_nlp, index=False, encoding='utf-8')
    print(f"\nDataset NLP complet sauvegardé → {out_nlp}")
    print(f"  Shape : {nlp_df.shape}")
    print("  Distribution niveaux :")
    print(nlp_df['niveau'].value_counts().to_string(index=True))

    # 6. Dataset filtré Maroc
    maroc_df = nlp_df[nlp_df['maroc_relevant'] == 1].copy()
    maroc_df['source'] = 'RASFF'

    out_maroc = OUTPUT_DIR / 'rasff_maroc_dataset.csv'
    maroc_df.to_csv(out_maroc, index=False, encoding='utf-8')
    print(f"\nDataset MAROC sauvegardé → {out_maroc}")
    print(f"  Shape : {maroc_df.shape}")
    print("  Distribution niveaux (Maroc) :")
    print(maroc_df['niveau'].value_counts().to_string(index=True))

    # 7. Fusion FDA (optionnel)
    fda_df = load_fda(INPUT_FDA)
    if fda_df is not None:
        combined = pd.concat(
            [maroc_df[['texte', 'niveau', 'source']], fda_df],
            ignore_index=True
        )
        out_combined = OUTPUT_DIR / 'nlp_dataset_combined.csv'
        combined.to_csv(out_combined, index=False, encoding='utf-8')
        print(f"\nDataset combiné RASFF + FDA sauvegardé → {out_combined}")
        print(f"  Shape : {combined.shape}")
        print("  Distribution niveaux :")
        print(combined['niveau'].value_counts().to_string(index=True))
        print("  Sources :")
        print(combined['source'].value_counts().to_string(index=True))

    # 8. Résumé final
    print_summary(OUTPUT_DIR)
    print("\nTerminé !")


if __name__ == '__main__':
    main()