"""Metadata-aware hybrid retrieval for the MaoGongShan knowledge base."""

from __future__ import annotations

import math
import re
import sqlite3
from collections import Counter
from typing import Any


METADATA_COLUMNS = {
    "topic": "TEXT DEFAULT 'extended_reference'",
    "location": "TEXT DEFAULT ''",
    "source_type": "TEXT DEFAULT 'reference'",
    "authority": "TEXT DEFAULT 'secondary'",
    "document_date": "TEXT DEFAULT ''",
    "relevance": "REAL DEFAULT 0.2",
    "tags": "TEXT DEFAULT ''",
    "knowledge_level": "INTEGER DEFAULT 6",
}

REALTIME_TERMS = ("最近", "今天", "现在", "当前", "开放吗", "开放时间", "活动", "新闻", "天气", "票价", "预约")
MAOGONGSHAN_TERMS = ("毛公山", "毛公三", "毛工山", "毛功山")
PROJECT_TERMS = ("这个项目", "本项目", "谁开发", "软件学院", "山东大学", "社会实践", "实践团队", "山软")
PARTY_TERMS = ("党史", "中国共产党", "长征", "井冈山", "延安", "西柏坡", "红色精神")
IRRELEVANT_PLACES = ("青岛地铁", "烟台山", "潍坊", "梅园新村", "南京", "济南站", "地铁站")
STOPWORDS = {"介绍", "一下", "什么", "怎么", "如何", "哪些", "有什么", "为什么", "这个", "那个", "它", "那", "的是"}


def ensure_metadata_schema(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(knowledge_documents)")}
    for name, definition in METADATA_COLUMNS.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE knowledge_documents ADD COLUMN {name} {definition}")


def _metadata_for(row: sqlite3.Row) -> dict[str, Any]:
    title = str(row["title"] or "")
    summary = str(row["summary"] or "")
    content = str(row["content"] or "")
    category = str(row["category"] or "")
    source = str(row["source_name"] or "")
    url = str(row["source_url"] or "")
    text = f"{title} {summary} {content} {category} {source} {url}".lower()

    primary_text = f"{title} {summary} {category}".lower()
    project_categories = {"项目介绍", "实践计划", "项目成果", "实践团队", "软件学院", "实践调研", "实践过程", "实践成果", "青年实践", "技术介绍", "技术资料", "成果", "青年感悟", "调研方法", "调研记录", "调研访谈", "访谈整理稿", "实践活动"}
    is_project = category in project_categories or any(term.lower() in primary_text for term in PROJECT_TERMS)
    is_maogongshan = any(term.lower() in primary_text for term in MAOGONGSHAN_TERMS)
    is_local = any(term in text for term in ("城阳", "惜福镇", "惜福", "青峰社区"))
    is_qingdao = "青岛" in text
    is_party = any(term.lower() in text for term in PARTY_TERMS)

    is_low_value_asset = category in {"数字资源", "图片资源", "图片资料", "音频资料", "智能问答"}
    is_synthetic_variant = bool(re.search(r"(?:问法|扩写|补充)\s*\d+", title))
    is_repeated_card = title.startswith("扩展参考资源") or bool(re.search(r"(?:专题|资源卡)\s*(?:0?[2-9]|[1-9]\d+)$", title))

    if (is_low_value_asset or is_synthetic_variant or is_repeated_card) and not category == "毛公山核心资源":
        level, topic = 6, "extended_reference"
    elif is_project:
        level, topic = 5, "social_practice"
        if "软件学院" in text:
            topic = "software_school"
        if "山东大学" in text and "软件学院" not in text:
            topic = "shandong_university"
    elif is_maogongshan:
        level, topic = 1, "maogongshan_core"
        if any(term in text for term in ("历史", "由来", "得名", "名称")):
            topic = "maogongshan_history"
        elif any(term in text for term in ("红色", "文化", "故事")):
            topic = "maogongshan_culture"
        elif any(term in text for term in ("景观", "山体", "风景", "生态", "自然")):
            topic = "maogongshan_scenic"
        elif any(term in text for term in ("游览", "路线", "登山", "交通", "景点")):
            topic = "maogongshan_travel"
    elif is_local or is_qingdao:
        level, topic = 2, "chengyang" if (is_local or "城阳" in text) else "qingdao"
        if "惜福" in text:
            topic = "xifuzhen"
        if is_party or "红色" in text:
            level, topic = 3, "qingdao_red_history"
    elif is_party or "红色" in text:
        level, topic = 4, "party_history"
    else:
        level, topic = 6, "extended_reference"

    if any(term.lower() in text for term in IRRELEVANT_PLACES) and not is_maogongshan:
        level, topic = 6, "extended_reference"

    host_text = f"{source} {url}".lower()
    if any(value in host_text for value in ("gov.cn", "青岛市政府", "城阳区政府", "城阳政务", "国家体育总局")):
        source_type, authority = "official_government", "official"
    elif any(value in host_text for value in ("sdu.edu.cn", "山东大学", "软件学院专题")):
        source_type, authority = "official_university", "official"
    elif is_project:
        source_type, authority = "project_material", "project_verified"
    elif any(value in host_text for value in ("people.com.cn", "人民网", "xinhuanet", "新华社", "青岛新闻网", "大众网")):
        source_type, authority = "authoritative_media", "authoritative"
    elif any(value in host_text for value in ("wikipedia", "wikimedia", "维基")):
        source_type, authority = "encyclopedia", "secondary"
    else:
        source_type, authority = "reference", "secondary"

    location = ""
    if is_maogongshan or is_local:
        location = "青岛市城阳区惜福镇街道"
    elif is_qingdao:
        location = "青岛市"
    date_match = re.search(r"(?<!\d)((?:19|20)\d{2}(?:[-/.年]\d{1,2}(?:[-/.月]\d{1,2}日?)?)?)", text)
    document_date = date_match.group(1) if date_match else ""
    relevance = {1: 1.0, 2: 0.82, 3: 0.68, 4: 0.55, 5: 0.72, 6: 0.18}[level]
    tags = [topic]
    if is_maogongshan:
        tags.append("maogongshan")
    if is_local:
        tags.extend(["chengyang", "xifuzhen"])
    if is_project:
        tags.append("social_practice")
    return {
        "topic": topic,
        "location": location,
        "source_type": source_type,
        "authority": authority,
        "document_date": document_date,
        "relevance": relevance,
        "tags": ",".join(dict.fromkeys(tags)),
        "knowledge_level": level,
    }


def backfill_knowledge_metadata(conn: sqlite3.Connection) -> dict[int, int]:
    """Classify all current documents; deterministic so startup rebuilds stay consistent."""
    ensure_metadata_schema(conn)
    counts: Counter[int] = Counter()
    rows = conn.execute("SELECT * FROM knowledge_documents").fetchall()
    for row in rows:
        meta = _metadata_for(row)
        counts[meta["knowledge_level"]] += 1
        conn.execute(
            """UPDATE knowledge_documents SET topic=?, location=?, source_type=?, authority=?,
               document_date=?, relevance=?, tags=?, knowledge_level=? WHERE id=?""",
            (*meta.values(), row["id"]),
        )
    return dict(sorted(counts.items()))


def is_realtime_question(question: str) -> bool:
    return any(term in question for term in REALTIME_TERMS)


def classify_question(question: str) -> str:
    """Route knowledge sources before retrieval; project-owned facts stay RAG-first."""
    if any(term in question for term in ("资料库里", "数据库", "你们收录", "平台有哪些功能", "根据你们", "平台资料")):
        return "database_query"
    if any(term in question for term in PROJECT_TERMS):
        return "university_practice" if any(term in question for term in ("软件学院", "山东大学", "学生", "社会实践")) else "project_info"
    if is_realtime_question(question):
        return "realtime"
    if any(term in question for term in ("游览", "怎么逛", "值得看", "路线", "景点", "旅游")):
        return "travel"
    if any(term in question for term in ("历史", "由来", "得名", "为什么叫", "红色故事")):
        return "history"
    if "文化" in question or "红色" in question:
        return "culture"
    if any(term in question for term in MAOGONGSHAN_TERMS):
        return "scenic_guide"
    return "public_knowledge"


def contextualize_question(question: str, history: list[dict[str, str]] | None) -> str:
    """Resolve short Chinese follow-ups for retrieval without rewriting the user message."""
    if any(term in question for term in MAOGONGSHAN_TERMS + PROJECT_TERMS + PARTY_TERMS):
        return question
    if not any(term in question for term in ("它", "那", "这个", "那里", "最值得", "第一次去")):
        return question
    for turn in reversed(history or []):
        content = str(turn.get("content") or "")
        if any(term in content for term in MAOGONGSHAN_TERMS):
            return f"{question}（承接上文：毛公山）"
        if any(term in content for term in PROJECT_TERMS):
            return f"{question}（承接上文：山东大学软件学院毛公山社会实践项目）"
    return question


def _tokens(value: str) -> list[str]:
    normalized = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", " ", value.lower())
    tokens: list[str] = []
    for part in normalized.split():
        if re.fullmatch(r"[\u4e00-\u9fff]+", part):
            tokens.extend(part[index:index + 2] for index in range(max(1, len(part) - 1)))
        elif len(part) > 1:
            tokens.append(part)
    for phrase in MAOGONGSHAN_TERMS + PROJECT_TERMS + PARTY_TERMS:
        if phrase.lower() in normalized:
            tokens.append(phrase.lower())
    return [token for token in tokens if token not in STOPWORDS]


def _intent(question: str) -> str:
    if any(term in question for term in PROJECT_TERMS):
        return "project"
    if any(term in question for term in MAOGONGSHAN_TERMS) or "承接上文：毛公山" in question:
        return "maogongshan"
    if any(term in question for term in PARTY_TERMS):
        return "party"
    return "general"


def hybrid_search(
    conn: sqlite3.Connection,
    question: str,
    history: list[dict[str, str]] | None = None,
    limit: int = 6,
) -> tuple[list[dict[str, Any]], str, str]:
    """BM25 + keyword + metadata filter + deterministic rerank."""
    contextual_question = contextualize_question(question, history)
    if any(term in contextual_question for term in ("月球", "火星", "彩票", "股票行情")):
        return [], "none", contextual_question
    query_tokens = _tokens(contextual_question)
    if not query_tokens:
        return [], "none", contextual_question
    rows = [dict(row) for row in conn.execute("SELECT * FROM knowledge_documents").fetchall()]
    if not rows:
        return [], "none", contextual_question

    intent = _intent(contextual_question)
    asks_history = any(term in contextual_question for term in ("历史", "文化", "由来", "得名", "为什么叫", "红色故事"))
    asks_location = any(term in contextual_question for term in ("哪里", "位置", "在哪", "城阳是什么关系"))
    asks_travel = any(term in contextual_question for term in ("游览", "怎么逛", "值得看", "路线", "第一次去"))
    asks_general = intent == "maogongshan" and not (asks_history or asks_location or asks_travel)
    doc_tokens = [_tokens(f"{row.get('title','')} {row.get('summary','')} {row.get('content','')} {row.get('tags','')}") for row in rows]
    document_frequency = Counter(token for tokens in doc_tokens for token in set(tokens))
    average_length = sum(len(tokens) for tokens in doc_tokens) / max(len(doc_tokens), 1)
    scored: list[tuple[float, dict[str, Any]]] = []
    for row, tokens in zip(rows, doc_tokens):
        level = int(row.get("knowledge_level") or 6)
        text = f"{row.get('title','')} {row.get('summary','')} {row.get('content','')} {row.get('tags','')}"
        title = str(row.get("title") or "")
        if intent == "maogongshan" and (level == 6 or (level >= 4 and "毛公山" not in text)):
            continue
        if intent == "project" and level not in {1, 5}:
            continue
        if intent == "party" and level not in {1, 3, 4}:
            continue
        counts = Counter(tokens)
        score = 0.0
        for token in set(query_tokens):
            frequency = counts[token]
            if not frequency:
                continue
            inverse_frequency = math.log(1 + (len(rows) - document_frequency[token] + 0.5) / (document_frequency[token] + 0.5))
            score += inverse_frequency * (frequency * 2.2) / (frequency + 1.2 * (0.25 + 0.75 * len(tokens) / max(average_length, 1)))
        for phrase in MAOGONGSHAN_TERMS + PROJECT_TERMS + PARTY_TERMS:
            if phrase in contextual_question and phrase in title:
                score += 9.0
        if intent == "maogongshan":
            if level == 1:
                score += 10.0
            elif level == 2:
                score += 2.5
            if any(place in text for place in IRRELEVANT_PLACES) and "毛公山" not in title + str(row.get("summary") or ""):
                score -= 25.0
            topic = str(row.get("topic") or "")
            category = str(row.get("category") or "")
            if asks_history and topic in {"maogongshan_history", "maogongshan_culture"}:
                score += 12.0
            if any(term in contextual_question for term in ("为什么叫", "得名", "名字", "名称")) and any(term in title for term in ("名称", "由来", "得名")):
                score += 18.0
            if any(term in contextual_question for term in ("为什么叫", "得名", "名字", "名称")) and "为什么要建设" in title:
                score -= 18.0
            if asks_location and (row.get("location") or category in {"地点", "景点导览", "毛公山概况"}):
                score += 10.0
            if asks_travel and topic == "maogongshan_travel":
                score += 11.0
            if asks_general and (topic == "maogongshan_core" or category in {"基础介绍", "基础资料", "毛公山概况", "毛公山核心资源"}):
                score += 13.0
            if asks_general and "3A" in title and "3A" not in contextual_question:
                score -= 10.0
            if asks_general and "4A" in title:
                score += 5.0
            if category in {"数字资源", "图片资源", "图片资料", "智能问答"}:
                score -= 12.0
        if intent == "project" and level == 5:
            score += 10.0
        if intent == "party" and level in {3, 4}:
            score += 6.0
        score += float(row.get("relevance") or 0) * 2.5
        if row.get("authority") in {"official", "authoritative", "project_verified"}:
            score += 1.5
        if score >= 2.2:
            row["retrieval_score"] = round(score, 3)
            row["retrieval_level"] = level
            scored.append((score, row))

    scored.sort(key=lambda item: (item[0], -int(item[1].get("knowledge_level") or 6)), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    seen_content: set[str] = set()
    for score, row in scored:
        normalized_title = re.sub(r"\W+", "", str(row.get("title") or "").lower())[:80]
        if normalized_title in seen_titles:
            continue
        content_fingerprint = re.sub(r"\W+", "", f"{row.get('summary','')} {row.get('content','')}".lower())[:360]
        if content_fingerprint and content_fingerprint in seen_content:
            continue
        seen_titles.add(normalized_title)
        if content_fingerprint:
            seen_content.add(content_fingerprint)
        selected.append(row)
        if len(selected) >= limit:
            break
    if not selected:
        quality = "none"
    elif selected[0]["retrieval_score"] >= 13 and sum(1 for row in selected if int(row.get("knowledge_level") or 6) <= 2) >= 2:
        quality = "high"
    else:
        quality = "partial"
    return selected, quality, contextual_question
