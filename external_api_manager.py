# external_api_manager.py — Gestionnaire d'APIs externes avec cache Redis

import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, List, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from services.cache import CacheService

logger = logging.getLogger(__name__)

class ExternalAPIManager:
    """
    Gestionnaire centralisé pour toutes les APIs externes.
    - Cache Redis pour performance
    - Retry automatique avec backoff
    - Appels async pour parallélisation
    - Fallbacks sur données statiques
    """

    def __init__(self):
        self.cache = CacheService()
        self.session_headers = {
            'User-Agent': 'MaroTrade Intelligence/2.0 (contact@marotrade.ma)',
            'Accept': 'application/json',
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_un_comtrade(self, hs_code: str, country: str, year: int) -> Optional[Dict]:
        """Récupère données UN Comtrade avec cache."""
        cache_key = f"un_comtrade:{hs_code}:{country}:{year}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = f"https://comtradeapi.un.org/public/v1/get?type=C&freq=A&px=HS&ps={year}&r={country}&p=all&cc={hs_code}"
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cache.set(cache_key, data, ttl=86400 * 7)  # 7 jours
                        return data
        except Exception as e:
            logger.warning(f"UN Comtrade API error: {e}")
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_world_bank(self, indicator: str, country: str) -> Optional[Dict]:
        """Récupère indicateurs World Bank."""
        cache_key = f"world_bank:{indicator}:{country}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Mapping ISO3 to ISO2 (simplifié)
        iso2_mapping = {
            "FRA": "FR", "DEU": "DE", "ESP": "ES", "ITA": "IT", "NLD": "NL",
            "BEL": "BE", "GBR": "GB", "USA": "US", "CAN": "CA", "SAU": "SA",
            "ARE": "AE", "EGY": "EG", "QAT": "QA", "KWT": "KW", "JPN": "JP",
            "CHN": "CN", "KOR": "KR", "SGP": "SG"
        }
        iso2 = iso2_mapping.get(country, country)
        url = f"https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}?format=json&per_page=1"
        try:
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 1 and data[1]:
                            result = data[1][0]
                            self.cache.set(cache_key, result, ttl=86400 * 7)
                            return result
        except Exception as e:
            logger.warning(f"World Bank API error: {e}")
        return None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=5, max=15))
    async def fetch_google_trends(self, keyword: str, geo: str = 'MA') -> Optional[Dict]:
        """Récupère tendances Google Trends (limité à 5 req/min)."""
        cache_key = f"google_trends:{keyword}:{geo}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='fr-MA', tz=360, timeout=(10, 25))
            pytrends.build_payload([keyword], cat=0, timeframe='today 5-y', geo=geo, gprop='')
            data = pytrends.interest_over_time()
            if not data.empty:
                result = data.to_dict()
                self.cache.set(cache_key, result, ttl=86400 * 3)  # 3 jours
                return result
        except Exception as e:
            logger.warning(f"Google Trends error: {e}")
        return None

    async def batch_fetch(self, requests: List[Dict]) -> List[Optional[Dict]]:
        """Exécute plusieurs requêtes en parallèle."""
        tasks = []
        for req in requests:
            if req['type'] == 'un_comtrade':
                tasks.append(self.fetch_un_comtrade(req['hs_code'], req['country'], req['year']))
            elif req['type'] == 'world_bank':
                tasks.append(self.fetch_world_bank(req['indicator'], req['country']))
            elif req['type'] == 'google_trends':
                tasks.append(self.fetch_google_trends(req['keyword'], req.get('geo', 'MA')))
        
        return await asyncio.gather(*tasks, return_exceptions=True)

# Instance globale
api_manager = ExternalAPIManager()