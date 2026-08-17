"""Conservative, key-free web search for time-sensitive public information."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

logger = logging.getLogger("maogongshan.web_search")

TRUSTED_DOMAINS = {
    "qingdao.gov.cn": 100,
    "chengyang.gov.cn": 100,
    "sdu.edu.cn": 95,
    "people.com.cn": 90,
    "xinhuanet.com": 90,
    "news.cn": 90,
    "sd.gov.cn": 88,
    "qingdaonews.com": 75,
}


def _trust_score(url: str) -> int:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    for domain, score in TRUSTED_DOMAINS.items():
        if host == domain or host.endswith(f".{domain}"):
            return score
    return 45


def search_web(question: str, limit: int = 5, timeout: float | None = None) -> list[dict[str, Any]]:
    """Use Bing's public RSS output, then rerank and expose only safe HTTP(S) sources."""
    if os.getenv("WEB_SEARCH_PROVIDER", "bing-rss").strip().lower() in {"off", "disabled", "none"}:
        return []
    timeout = timeout or min(max(float(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "8")), 3), 15)
    trusted_filter = "site:qingdao.gov.cn OR site:chengyang.gov.cn OR site:sdu.edu.cn OR site:people.com.cn OR site:news.cn"
    query = f"毛公山 城阳 {question} ({trusted_filter})"
    endpoint = f"https://www.bing.com/search?format=rss&q={quote_plus(query)}"
    request = Request(endpoint, headers={"User-Agent": "MaoGongShan-Cultural-Research/2.0", "Accept": "application/rss+xml"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read(1_500_000)
        root = ElementTree.fromstring(payload)
    except Exception as error:  # Network/search failure must never take down chat.
        logger.warning("Web search unavailable: error=%s", error.__class__.__name__)
        return []

    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        summary = (item.findtext("description") or "").strip()
        published = (item.findtext("pubDate") or "").strip()
        parsed = urlparse(link)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or link in seen:
            continue
        seen.add(link)
        relevance = 30 if "毛公山" in f"{title} {summary}" else 0
        relevance += 12 if "城阳" in f"{title} {summary}" else 0
        score = _trust_score(link) + relevance
        results.append({
            "title": title[:240] or "联网检索资料",
            "summary": summary[:1200],
            "content": summary[:1800],
            "category": "实时联网资料",
            "source_name": parsed.hostname or "公开网页",
            "source_url": link,
            "verification_status": "联网检索，请以来源页面最新信息为准",
            "source_type": "web_search",
            "authority": "official" if _trust_score(link) >= 88 else "secondary",
            "topic": "maogongshan_current",
            "location": "青岛市城阳区",
            "document_date": published,
            "relevance": score / 100,
            "tags": "maogongshan,web_search,current",
            "knowledge_level": 1 if "毛公山" in f"{title} {summary}" else 2,
            "retrieval_score": float(score),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        })
    results.sort(key=lambda row: row["retrieval_score"], reverse=True)
    return [row for row in results if row["retrieval_score"] >= 88][:limit]
