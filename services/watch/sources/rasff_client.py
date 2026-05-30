"""Structured RASFF public data connector.

The connector starts from the public RASFF consumer RSS feed, then attempts to
hydrate each item with the public notification detail endpoint when a
notification id is present. The output is normalized for RegulatoryWatchEngine
and intentionally never exposes or uses risk_decision.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import feedparser
import requests

logger = logging.getLogger(__name__)


LEVEL_CRITICAL = "CRITIQUE"
LEVEL_WARNING = "ATTENTION"
LEVEL_INFO = "INFO"


class RASFFStructuredClient:
    """Fetches recent RASFF alerts and normalizes them for the NLP pipeline."""

    BASE_URL = "https://webgate.ec.europa.eu/rasff-window/backend/public"
    SEARCH_URL = f"{BASE_URL}/notification/search/consolidated/en/"
    RSS_URL = f"{BASE_URL}/consumer/rss/all/"
    DETAIL_URL = f"{BASE_URL}/notification/view/id/{{notification_id}}/"

    def __init__(
        self,
        cache_dir: str | Path = ".cache_c02/rasff_structured",
        timeout: int = 15,
        cache_ttl_minutes: int = 60,
        max_items: int = 30,
    ):
        self.cache_dir = Path(cache_dir)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.cache_dir = Path(".cache_rasff_structured")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.max_items = max_items
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json, application/rss+xml, application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "MaroTrade-Intelligence/1.0 (+https://localhost)",
            }
        )

    def fetch_latest(self, max_items: Optional[int] = None, use_cache: bool = True) -> List[Dict]:
        """Return latest RASFF alerts normalized for RegulatoryWatchEngine."""
        limit = max_items or self.max_items
        cache_path = self.cache_dir / f"rasff_latest_{limit}.json"

        if use_cache:
            cached = self._read_cache(cache_path)
            if cached is not None:
                return cached

        alerts: List[Dict] = []
        try:
            notifications = self._fetch_search_notifications(limit)
            if notifications:
                logger.info("RASFFStructuredClient fetched %s structured notifications", len(notifications))
                alerts = [self._normalize_search_notification(item) for item in notifications]
            else:
                feed = feedparser.parse(self.RSS_URL)
                entries = list(feed.entries or [])[:limit]
                logger.info("RASFFStructuredClient fetched %s RSS entries", len(entries))

                for entry in entries:
                    notification_id = self._extract_notification_id(entry)
                    detail = self._fetch_detail(notification_id) if notification_id else None
                    alert = self._normalize_detail(detail, entry, notification_id) if detail else self._normalize_entry(entry)
                    if alert:
                        alerts.append(alert)

        except Exception as exc:
            logger.exception("RASFF structured fetch failed: %s", exc)

        alerts = self._deduplicate(alerts)
        if alerts:
            self._write_cache(cache_path, alerts)
        return alerts

    def _fetch_search_notifications(self, limit: int) -> List[Dict]:
        payload = {
            "parameters": {
                "pageNumber": 1,
                "itemsPerPage": limit,
            }
        }
        try:
            response = self.session.post(
                self.SEARCH_URL,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
            notifications = payload.get("notifications") if isinstance(payload, dict) else None
            return notifications if isinstance(notifications, list) else []
        except Exception as exc:
            logger.debug("RASFF consolidated search failed: %s", exc)
            return []

    def _normalize_search_notification(self, item: Dict) -> Dict:
        title = self._first_text(item.get("subject"), "RASFF notification")
        category = self._first_text(self._path(item, ["productCategory", "description"]))
        classification = self._first_text(self._path(item, ["notificationClassification", "description"]))
        origin = self._countries_to_text(item.get("originCountries"))
        notifying_country = self._first_text(self._path(item, ["notifyingCountry", "organizationName"]))
        reference = self._first_text(item.get("reference"), item.get("notifId"), self._stable_hash(title))
        date = self._normalize_date(item.get("ecValidationDate"))
        summary = self._compose_summary(title, category, "", origin)
        text_for_level = f"{title} {summary} {classification}".lower()

        return {
            "id": f"RASFF-{reference}",
            "titre": title[:180],
            "titre_fr": title[:180],
            "niveau": self._detect_level(text_for_level),
            "level": self._detect_level(text_for_level),
            "source": "RASFF",
            "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL", "GBR"],
            "pays_nom": "Union Europeenne",
            "date": date,
            "resume": summary,
            "resume_fr": summary,
            "action": "Verifier la conformite documentaire et sanitaire avant expedition.",
            "url": "https://webgate.ec.europa.eu/rasff-window/",
            "score_impact": self._estimate_impact_score(text_for_level),
            "impact_score": self._estimate_impact_score(text_for_level),
            "delai_jours": 0,
            "category": category,
            "classification": classification,
            "origin": origin,
            "maroc_relevant": self._contains_morocco(f"{title} {summary} {origin} {notifying_country}"),
            "notifying_country": notifying_country,
            "reference": reference,
            "structured": True,
            "live": True,
        }

    def _fetch_detail(self, notification_id: str) -> Optional[Dict]:
        detail_cache = self.cache_dir / f"notification_{notification_id}.json"
        cached = self._read_cache(detail_cache)
        if cached is not None:
            return cached

        try:
            response = self.session.get(
                self.DETAIL_URL.format(notification_id=notification_id),
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                self._write_cache(detail_cache, payload)
                return payload
        except Exception as exc:
            logger.debug("RASFF detail fetch failed for %s: %s", notification_id, exc)
        return None

    def _normalize_detail(self, detail: Dict, entry: Any, notification_id: Optional[str]) -> Dict:
        product = self._find_first_dict(detail, ["product"]) or {}
        title = (
            self._first_text(
                self._path(product, ["description"]),
                self._find_first_value(detail, ["title", "subject", "description"]),
                self._entry_value(entry, "title"),
            )
            or "RASFF notification"
        )
        category = self._first_text(
            self._path(product, ["productCategory", "description"]),
            self._path(product, ["category", "description"]),
            self._find_first_value(detail, ["productCategory", "category"]),
        )
        classification = self._first_text(
            self._find_first_value(detail, ["classification", "notificationClassification", "notificationType", "type"]),
        )
        origin = self._first_text(
            self._path(product, ["originCountry", "description"]),
            self._path(product, ["countryOfOrigin", "description"]),
            self._find_first_value(detail, ["origin", "countryOfOrigin", "originCountry"]),
        )
        hazard = self._first_text(
            self._path(product, ["hazard", "description"]),
            self._find_first_value(detail, ["hazard", "hazards", "substance", "risk"]),
        )
        date = self._first_text(
            self._find_first_value(detail, ["ecValidationDate", "validationDate", "date", "createdDate"]),
            self._entry_value(entry, "published"),
        )
        reference = self._first_text(self._find_first_value(detail, ["reference"]), notification_id)
        url = self.DETAIL_URL.format(notification_id=notification_id) if notification_id else self._entry_value(entry, "link")
        summary = self._compose_summary(title, category, hazard, origin)
        text_for_level = f"{title} {summary} {classification} {hazard}".lower()

        return {
            "id": f"RASFF-{reference or self._stable_hash(title, date)}",
            "titre": title[:180],
            "titre_fr": title[:180],
            "niveau": self._detect_level(text_for_level),
            "level": self._detect_level(text_for_level),
            "source": "RASFF",
            "pays": origin or "EU",
            "pays_nom": origin or "Union Europeenne",
            "date": self._normalize_date(date),
            "resume": summary,
            "resume_fr": summary,
            "action": "Verifier la conformite documentaire et sanitaire avant expedition.",
            "url": url,
            "score_impact": self._estimate_impact_score(text_for_level),
            "impact_score": self._estimate_impact_score(text_for_level),
            "delai_jours": 0,
            "category": category,
            "classification": classification,
            "origin": origin,
            "maroc_relevant": self._is_maroc_relevant(detail, title, summary, origin),
            "structured": True,
            "live": True,
        }

    def _normalize_entry(self, entry: Any) -> Dict:
        title = self._entry_value(entry, "title") or "RASFF notification"
        summary = self._entry_value(entry, "summary") or self._entry_value(entry, "description") or title
        date = self._entry_value(entry, "published") or self._entry_value(entry, "updated")
        link = self._entry_value(entry, "link")
        text_for_level = f"{title} {summary}".lower()
        entry_id = self._extract_notification_id(entry) or self._stable_hash(title, date)

        return {
            "id": f"RASFF-{entry_id}",
            "titre": title[:180],
            "titre_fr": title[:180],
            "niveau": self._detect_level(text_for_level),
            "level": self._detect_level(text_for_level),
            "source": "RASFF",
            "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL", "GBR"],
            "pays_nom": "Union Europeenne",
            "date": self._normalize_date(date),
            "resume": summary[:500],
            "resume_fr": summary[:500],
            "action": "Verifier les exigences RASFF et les certificats sanitaires applicables.",
            "url": link,
            "score_impact": self._estimate_impact_score(text_for_level),
            "impact_score": self._estimate_impact_score(text_for_level),
            "delai_jours": 0,
            "category": "",
            "classification": "",
            "origin": "",
            "maroc_relevant": self._contains_morocco(f"{title} {summary}"),
            "structured": False,
            "live": True,
        }

    def _extract_notification_id(self, entry: Any) -> Optional[str]:
        candidates = [
            self._entry_value(entry, "id"),
            self._entry_value(entry, "guid"),
            self._entry_value(entry, "link"),
            self._entry_value(entry, "summary"),
            self._entry_value(entry, "title"),
        ]
        text = " ".join(value for value in candidates if value)
        patterns = [
            r"/notification/view/id/(\d+)",
            r"/notification/(\d+)",
            r"[?&]id=(\d+)",
            r"\b(\d{5,8})\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _compose_summary(self, title: str, category: str, hazard: str, origin: str) -> str:
        parts = [title]
        if category:
            parts.append(f"Category: {category}")
        if hazard:
            parts.append(f"Hazard: {hazard}")
        if origin:
            parts.append(f"Origin: {origin}")
        return " | ".join(parts)[:600]

    def _detect_level(self, text: str) -> str:
        critical = ["serious", "alert", "recall", "withdrawal", "salmonella", "listeria", "aflatoxin", "border rejection"]
        warning = ["information", "attention", "follow-up", "pesticide", "residue", "migration", "unauthorised"]
        if any(keyword in text for keyword in critical):
            return LEVEL_CRITICAL
        if any(keyword in text for keyword in warning):
            return LEVEL_WARNING
        return LEVEL_INFO

    def _estimate_impact_score(self, text: str) -> float:
        score = 35.0
        for keyword in ["border rejection", "serious", "recall", "withdrawal", "salmonella", "listeria", "aflatoxin"]:
            if keyword in text:
                score += 15
        for keyword in ["pesticide", "residue", "origin", "unauthorised", "contaminant"]:
            if keyword in text:
                score += 8
        return min(score, 100.0)

    def _is_maroc_relevant(self, detail: Dict, title: str, summary: str, origin: str) -> bool:
        haystack = f"{title} {summary} {origin} {json.dumps(detail, ensure_ascii=False)[:3000]}"
        return self._contains_morocco(haystack)

    def _contains_morocco(self, value: str) -> bool:
        value_lower = (value or "").lower()
        return any(token in value_lower for token in ["morocco", "maroc", "marocain", "moroccan"])

    def _countries_to_text(self, countries: Any) -> str:
        if not isinstance(countries, list):
            return self._stringify(countries)

        names = []
        for country in countries:
            text = self._first_text(
                self._path(country, ["organizationName"]) if isinstance(country, dict) else "",
                self._path(country, ["description"]) if isinstance(country, dict) else "",
                self._path(country, ["isoCode"]) if isinstance(country, dict) else "",
                country,
            )
            if text:
                names.append(text)
        return ", ".join(names)

    def _deduplicate(self, alerts: Iterable[Dict]) -> List[Dict]:
        seen = set()
        results = []
        for alert in alerts:
            key = alert.get("id") or self._stable_hash(alert.get("titre", ""), alert.get("date", ""))
            if key in seen:
                continue
            seen.add(key)
            results.append(alert)
        return results

    def _read_cache(self, path: Path) -> Optional[Any]:
        if not path.exists():
            return None
        try:
            age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
            if age > self.cache_ttl:
                return None
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return None

    def _write_cache(self, path: Path, payload: Any) -> None:
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.debug("RASFF cache write failed for %s: %s", path, exc)

    def _entry_value(self, entry: Any, key: str) -> str:
        if not entry:
            return ""
        if isinstance(entry, dict):
            return str(entry.get(key, "") or "")
        return str(getattr(entry, key, "") or "")

    def _first_text(self, *values: Any) -> str:
        for value in values:
            text = self._stringify(value)
            if text:
                return text
        return ""

    def _stringify(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            for key in ["description", "name", "label", "value", "code"]:
                if key in value:
                    text = self._stringify(value.get(key))
                    if text:
                        return text
            return ""
        if isinstance(value, list):
            texts = [self._stringify(item) for item in value]
            return ", ".join(text for text in texts if text)
        return str(value).strip()

    def _path(self, payload: Dict, keys: List[str]) -> Any:
        current: Any = payload
        for key in keys:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current

    def _find_first_dict(self, payload: Any, keys: List[str]) -> Optional[Dict]:
        value = self._find_first_value(payload, keys)
        return value if isinstance(value, dict) else None

    def _find_first_value(self, payload: Any, keys: List[str]) -> Any:
        wanted = {key.lower() for key in keys}
        stack = [payload]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                for key, value in current.items():
                    if key.lower() in wanted:
                        return value
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(current, list):
                stack.extend(current)
        return None

    def _normalize_date(self, value: Any) -> str:
        text = self._stringify(value)
        if not text:
            return datetime.now().strftime("%Y-%m-%d")
        match = re.search(r"(\d{4})[-/](\d{2})[-/](\d{2})", text)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        match = re.search(r"(\d{2})[-/](\d{2})[-/](\d{4})", text)
        if match:
            return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        try:
            parsed = datetime(*getattr(value, "timetuple")()[:6])
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return text[:10]

    def _stable_hash(self, *parts: Any) -> str:
        raw = "|".join(self._stringify(part) for part in parts)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:10]
