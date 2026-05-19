# test_external_apis.py — Test des APIs externes avec cache

import asyncio
import logging
from external_api_manager import api_manager

logging.basicConfig(level=logging.INFO)

async def test_apis():
    print("=== Test APIs Externes ===")

    # Test UN Comtrade
    print("\n1. Test UN Comtrade...")
    result = await api_manager.fetch_un_comtrade("151590", "USA", 2022)
    print(f"UN Comtrade USA 2022: {'OK' if result else 'FAIL'}")

    # Test World Bank
    print("\n2. Test World Bank...")
    result = await api_manager.fetch_world_bank("IC.BUS.EASE.XQ", "FRA")
    print(f"World Bank FRA: {'OK' if result else 'FAIL'}")

    # Test Google Trends
    print("\n3. Test Google Trends...")
    result = await api_manager.fetch_google_trends("huile d'argan", "MA")
    print(f"Google Trends MA: {'OK' if result else 'FAIL'}")

    # Test batch
    print("\n4. Test batch fetch...")
    requests = [
        {'type': 'un_comtrade', 'hs_code': '151590', 'country': 'FRA', 'year': 2022},
        {'type': 'world_bank', 'indicator': 'IC.BUS.EASE.XQ', 'country': 'DEU'},
        {'type': 'google_trends', 'keyword': 'olive oil', 'geo': 'ES'}
    ]
    results = await api_manager.batch_fetch(requests)
    print(f"Batch results: {len(results)} requêtes")

    print("\n=== Test terminé ===")

if __name__ == "__main__":
    asyncio.run(test_apis())