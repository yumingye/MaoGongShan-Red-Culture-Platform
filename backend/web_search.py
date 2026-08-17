"""Web-first search with source tiers, relevance filtering and bounded TTL caching."""

from __future__ import annotations

import html
import logging
import os
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus, urlparse

import httpx

logger = logging.getLogger("maogongshan.web_search")

SOURCE_TIERS = {
    1: (
        ".gov.cn", "qingdao.gov.cn", "chengyang.gov.cn", "sdu.edu.cn",
        "qdzyfw.qingdao.gov.cn", "qdwmsj.qingdao.gov.cn",
    ),
    2: (
        "xinhuanet.com", "news.cn", "people.com.cn", "cnr.cn", "chinanews.com.cn",
        "qingdaonews.com", "dzwww.com",
    ),
    3: ("ctnews.com.cn", "visitqingdao.com", "sdta.cn", "bendibao.com"),
}
MAO_TERMS = ("毛公山", "毛公三", "毛工山", "毛功山")
INTENT_TERMS = {
    "history": ("历史", "文化", "由来", "得名", "为什么叫", "红色故事"),
    "travel": ("游览", "路线", "值得看", "景点", "怎么逛", "旅游"),
    "realtime": ("最近", "今天", "现在", "活动", "新闻", "开放", "门票", "票价", "天气", "通知", "交通"),
}

_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}
_CACHE_LOCK = threading.Lock()
_CACHE_MAX_ITEMS = 128


def _source_tier(url: str) -> int:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    for tier, domains in SOURCE_TIERS.items():
        if any(host == domain.lstrip(".") or host.endswith(domain) for domain in domains):
            return tier
    return 4


def _strip_markup(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def _query_terms(question: str) -> list[str]:
    terms = ["毛公山"] if any(term in question for term in MAO_TERMS) else []
    for values in INTENT_TERMS.values():
        terms.extend(term for term in values if term in question)
    if "城阳" in question:
        terms.append("城阳")
    if "红色文化" in question:
        terms.append("红色文化")
    return list(dict.fromkeys(terms))


def rewrite_query(question: str) -> str:
    """Keep Chinese named entities intact and add only high-signal context."""
    normalized = " ".join(question.replace("？", "").replace("。", "").split())[:160]
    if any(term in normalized for term in INTENT_TERMS["realtime"]):
        normalized = f"{normalized} {datetime.now().year}"
    if any(term in normalized for term in MAO_TERMS):
        return f'"毛公山" 青岛 城阳 {normalized}'
    return normalized


def _cache_ttl(question: str) -> int:
    if any(term in question for term in ("今天", "现在", "开放", "门票", "票价", "天气", "交通")):
        return 120
    if any(term in question for term in ("最近", "活动", "新闻", "通知", "公告")):
        return 300
    return 21600


def _cache_get(key: str) -> list[dict[str, Any]] | None:
    now = time.monotonic()
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if not cached:
            return None
        expires_at, rows = cached
        if expires_at <= now:
            _CACHE.pop(key, None)
            return None
        return [dict(row) for row in rows]


def _cache_put(key: str, ttl: int, rows: list[dict[str, Any]]) -> None:
    with _CACHE_LOCK:
        if len(_CACHE) >= _CACHE_MAX_ITEMS:
            _CACHE.pop(next(iter(_CACHE)), None)
        _CACHE[key] = (time.monotonic() + ttl, [dict(row) for row in rows])


def _parse_bing_html(payload: bytes) -> list[dict[str, str]]:
    page = payload.decode("utf-8", "ignore")
    blocks = re.findall(r'<li[^>]+class="[^"]*\bb_algo\b[^"]*"[^>]*>(.*?)</li>', page, re.I | re.S)
    rows: list[dict[str, str]] = []
    for block in blocks:
        heading = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.I | re.S)
        if not heading:
            continue
        summary_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.I | re.S)
        rows.append({
            "source_url": html.unescape(heading.group(1)).strip(),
            "title": _strip_markup(heading.group(2)),
            "summary": _strip_markup(summary_match.group(1)) if summary_match else "",
        })
    return rows


def _parse_so_html(payload: bytes) -> list[dict[str, str]]:
    page = payload.decode("utf-8", "ignore")
    blocks = re.findall(r'<li[^>]+class=["\'][^"\']*\bres-list\b[^"\']*["\'][^>]*>(.*?)</li>', page, re.I | re.S)
    rows: list[dict[str, str]] = []
    for block in blocks:
        heading = re.search(r'<h3[^>]*class=["\'][^"\']*\bres-title\b[^"\']*["\'][^>]*>\s*<a([^>]*)>(.*?)</a>', block, re.I | re.S)
        if not heading:
            continue
        attributes = heading.group(1)
        direct = re.search(r'data-mdurl=["\']([^"\']+)', attributes, re.I)
        href = re.search(r'href=["\']([^"\']+)', attributes, re.I)
        summary_match = re.search(r'class=["\'][^"\']*\bres-list-summary\b[^"\']*["\'][^>]*>(.*?)</span>', block, re.I | re.S)
        url = html.unescape((direct or href).group(1)).strip() if (direct or href) else ""
        rows.append({
            "source_url": url,
            "title": _strip_markup(heading.group(2)),
            "summary": _strip_markup(summary_match.group(1)) if summary_match else "",
        })
    return rows


def _fetch_html(endpoint: str, headers: dict[str, str], timeout: float) -> bytes:
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        response = client.get(endpoint)
        response.raise_for_status()
        return response.content[:2_500_000]


def _fetch_qingdao_official(question: str, headers: dict[str, str], timeout: float) -> list[dict[str, str]]:
    """Query Qingdao Government's public unified-search API without credentials."""
    params = {
        "code": "0060ed3eefe4449c93734b28fab5622a",
        "siteId": "5",
        "searchWord": "毛公山",
        "pageSize": "20",
        "pageNumber": "1",
        "modal": "1,3",
        "area": "0",
    }
    if any(term in question for term in INTENT_TERMS["realtime"]):
        params["publishTime"] = "DESC"
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        # The government endpoint currently serves this public JSON API over HTTP.
        response = client.get(
            "http://www.qingdao.gov.cn/igs/front/search.jhtml",
            params=params,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
    content = payload.get("page", {}).get("content", []) if isinstance(payload, dict) else []
    rows: list[dict[str, str]] = []
    for item in content if isinstance(content, list) else []:
        if not isinstance(item, dict):
            continue
        rows.append({
            "source_url": str(item.get("LinkUrl") or item.get("url") or "").strip(),
            "title": _strip_markup(str(item.get("title") or "")),
            "summary": _strip_markup(str(item.get("Content") or "")),
            "published": str(item.get("publishTime") or item.get("fwTime") or "").strip(),
        })
    return rows


def _fetch_candidates(question: str, timeout: float) -> tuple[list[dict[str, str]], str]:
    query = quote_plus(rewrite_query(question))
    endpoints = [
        (f"https://www.so.com/s?q={query}", _parse_so_html, "so-html"),
        (f"https://cn.bing.com/search?q={query}&setlang=zh-cn&cc=cn&count=12", _parse_bing_html, "bing-html"),
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MaoGongShan-Cultural-Research/3.0)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    if any(term in question for term in MAO_TERMS):
        for attempt in range(2):
            try:
                rows = _fetch_qingdao_official(question, headers, timeout)
                if rows:
                    return rows, "qingdao-government-search"
                break
            except Exception as error:
                logger.warning("Web search unavailable: provider=qingdao-government-search attempt=%s error=%s", attempt + 1, error.__class__.__name__)
    for endpoint, parser, provider in endpoints:
        for attempt in range(2):
            try:
                rows = parser(_fetch_html(endpoint, headers, timeout))
                if rows:
                    return rows, provider
                break
            except Exception as error:
                logger.warning("Web search unavailable: provider=%s attempt=%s error=%s", provider, attempt + 1, error.__class__.__name__)
    return [], "unavailable"


def _relevance(question: str, row: dict[str, str]) -> float:
    title = row.get("title", "")
    summary = row.get("summary", "")
    url = row.get("source_url", "")
    text = f"{title} {summary} {url}"
    terms = _query_terms(question)
    score = 0.0
    if any(term in question for term in MAO_TERMS):
        if "毛公山" not in text:
            return -100.0
        score += 45.0
    for term in terms:
        if term in title:
            score += 14.0
        elif term in summary:
            score += 6.0
    if "城阳" in text:
        score += 8.0
    if not any(term in question for term in INTENT_TERMS["realtime"]):
        if any(term in title for term in ("景区", "文旅", "简介", "旅游", "山头公园", "4A")):
            score += 12.0
        if any(term in text for term in ("站立石像", "巍然站立", "自然景观", "风景优美", "旅游资源", "国家4A")):
            score += 24.0
        if any(term in title for term in ("公安", "支队", "大队", "拉练", "督导", "检查", "妇女节")):
            score -= 45.0
        if any(term in title for term in ("主题党日", "开展活动")) and not any(term in question for term in ("活动", "红色故事")):
            score -= 16.0
    else:
        year = _extract_year(row)
        current_year = datetime.now().year
        if year == current_year:
            score += 30.0
        elif year == current_year - 1:
            score += 10.0
        elif year and year < current_year - 1:
            score -= 90.0
        else:
            score -= 5.0
    tier = _source_tier(url)
    score += {1: 40.0, 2: 28.0, 3: 18.0, 4: 4.0}[tier]
    if any(noise in text for noise in ("青岛地铁", "烟台山", "梅园新村", "潍坊地图", "南京")):
        score -= 80.0
    return score


def _extract_year(row: dict[str, str]) -> int | None:
    match = re.search(r"(?<!\d)(20\d{2})", f"{row.get('published', '')} {row.get('title', '')} {row.get('summary', '')} {row.get('source_url', '')}")
    return int(match.group(1)) if match else None


def _to_document(question: str, row: dict[str, str]) -> dict[str, Any]:
    url = row["source_url"]
    tier = _source_tier(url)
    score = _relevance(question, row)
    text = f"{row['title']} {row['summary']}"
    return {
        "title": row["title"][:240] or "联网检索资料",
        "summary": row["summary"][:1600],
        "content": row["summary"][:2000],
        "category": "实时联网资料" if any(term in question for term in INTENT_TERMS["realtime"]) else "联网公开资料",
        "source_name": urlparse(url).hostname or "公开网页",
        "source_url": url,
        "verification_status": f"联网检索 · Tier {tier}，请以来源页面最新信息为准",
        "source_type": "web_search",
        "authority": "official" if tier == 1 else "authoritative" if tier == 2 else "secondary",
        "source_tier": tier,
        "topic": "maogongshan_web" if "毛公山" in text else "public_web",
        "location": "青岛市城阳区" if "城阳" in text else "",
        "document_date": row.get("published", "")[:10] or str(_extract_year(row) or ""),
        "relevance": round(score / 100, 3),
        "tags": "web_search,maogongshan" if "毛公山" in text else "web_search",
        "knowledge_level": 1 if "毛公山" in text else 2,
        "retrieval_score": score,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def search_web_with_meta(question: str, limit: int = 5, timeout: float | None = None) -> tuple[list[dict[str, Any]], bool]:
    provider = os.getenv("WEB_SEARCH_PROVIDER", "auto-html").strip().lower()
    if provider in {"off", "disabled", "none"}:
        return [], False
    timeout = timeout or min(max(float(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10")), 3), 20)
    cache_key = rewrite_query(question).lower()
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached[:limit], True

    search_questions = [question]
    candidates: list[dict[str, str]] = []
    for search_question in search_questions:
        batch, actual_provider = _fetch_candidates(search_question, timeout)
        for row in batch:
            row["_search_provider"] = actual_provider
        candidates.extend(batch)
    if not candidates:
        return [], False

    documents: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for row in candidates:
        url = row.get("source_url", "")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or url in seen_urls:
            continue
        seen_urls.add(url)
        document = _to_document(question, row)
        document["search_provider"] = row.get("_search_provider", provider)
        if document["retrieval_score"] < 45:
            continue
        documents.append(document)
    documents.sort(key=lambda row: (row["source_tier"], -row["retrieval_score"]))
    reliable_documents = [row for row in documents if row["source_tier"] <= 3]
    if any(term in question for term in MAO_TERMS):
        documents = reliable_documents
    elif len(reliable_documents) >= 2:
        documents = reliable_documents
    if len(documents) > 2:
        best_score = max(float(row["retrieval_score"]) for row in documents)
        focused_documents = [row for row in documents if float(row["retrieval_score"]) >= best_score - 20]
        if len(focused_documents) >= 2:
            documents = focused_documents
    selected = documents[: max(2, min(limit, 5))]
    _cache_put(cache_key, _cache_ttl(question), selected)
    return selected, False


def search_web(question: str, limit: int = 5, timeout: float | None = None) -> list[dict[str, Any]]:
    return search_web_with_meta(question, limit, timeout)[0]
