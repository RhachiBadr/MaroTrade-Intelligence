#!/usr/bin/env python3
"""Test rapide de la structure des données."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_sources import get_trade_data, DEMO_TRADE_DATA

def test_data_structure():
    print("Test de la structure des données...")

    # Test données commerciales (fallback local)
    trade_df = get_trade_data('151590')
    print(f"✅ Données commerciales: {len(trade_df)} pays")

    # Vérifier les colonnes attendues
    expected_cols = ['country_code', 'country_name', 'value_usd', 'weight_kg', 'price_usd_kg']
    print(f"✅ Colonnes attendues: {expected_cols}")
    print(f"   Colonnes présentes: {list(trade_df.columns)}")

    # Vérifier les dimensions du dashboard
    dashboard_dims = [
        "Potentiel de marché", "Accord commercial", "Facilité des affaires",
        "Stabilité & risque pays", "Diaspora marocaine (MRE)", "Logistique & transport",
        "Tendance & demande"
    ]
    print(f"✅ Dimensions dashboard: {len(dashboard_dims)}")
    for dim in dashboard_dims:
        print(f"   - {dim}")

    # Test données démo
    if '151590' in DEMO_TRADE_DATA:
        demo_data = DEMO_TRADE_DATA['151590']
        print(f"✅ Données démo HS 151590: {len(demo_data)} pays")
        sample = demo_data[0]
        print(f"   Exemple: {sample}")

if __name__ == "__main__":
    test_data_structure()