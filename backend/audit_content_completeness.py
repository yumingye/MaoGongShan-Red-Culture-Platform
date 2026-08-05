"""审查公开内容的完整度，输出空字段和过短正文。"""

from __future__ import annotations

import sqlite3

try:
    from .config import DB_PATH
except ImportError:
    from config import DB_PATH


TABLE_RULES = {
    "learning_articles": {"title": 4, "summary": 40, "content": 300, "youth_insight": 45, "source_name": 4},
    "historical_events": {"title": 4, "summary": 35, "details": 180, "source": 4},
    "historical_figures": {"name": 2, "biography": 45, "deeds": 50, "source": 4},
    "history": {"title": 4, "summary": 45, "content": 220, "source_name": 4},
    "red_stories": {"title": 4, "summary": 45, "content": 250, "source": 4},
    "achievements": {"title": 4, "summary": 45, "content": 250, "source": 4},
    "places": {"title": 4, "summary": 45, "content": 220, "source": 4},
    "scenery": {"name": 2, "summary": 45, "content": 220, "source_name": 4},
    "scenic_spots": {"name": 2, "description": 50, "source": 4},
    "scenic_images": {"name": 2, "description": 60, "source": 4},
    "images": {"title": 4, "description": 70, "source_name": 4, "alt": 4},
    "routes": {"name": 4, "summary": 70, "source_name": 4},
    "categories": {"name": 2, "description": 35},
    "source_records": {"title": 4, "summary": 35, "source_name": 4},
    "resources": {"title": 4, "summary": 35, "source": 4},
    "research_logs": {"title": 4, "summary": 35, "content": 180, "source": 4},
    "expected_results": {"title": 4, "summary": 45},
    "project_information": {"title": 4, "value": 50},
    "practice_plans": {"title": 4, "summary": 50},
    "team_members": {"name": 2, "responsibility": 28, "public_bio": 28},
    "digital_resources": {"title": 4, "summary": 35, "content": 100, "source_name": 4},
    "audio_guides": {"title": 4, "summary": 35, "script": 180},
    "narrations": {"title": 4, "script": 150},
    "qa_knowledge": {"question": 6, "answer": 80, "category": 2, "source": 4},
}

FORBIDDEN_PHRASES = (
    "暂无内容",
    "敬请期待",
    "这里是介绍",
    "请输入内容",
    "示例文字",
    "标题一",
    "Lorem ipsum",
    "数字资源平台专题 0",
    "问法00",
)


def audit() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    issues: list[dict] = []
    existing_tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    for table, rules in TABLE_RULES.items():
        if table not in existing_tables:
            continue
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        selected = [field for field in rules if field in columns]
        if not selected:
            continue
        identity = "id" if "id" in columns else selected[0]
        query = f"SELECT {identity}, {', '.join(selected)} FROM {table}"
        for row in conn.execute(query):
            for field in selected:
                value = str(row[field] or "").strip()
                if len(value) < rules[field]:
                    issues.append({
                        "table": table,
                        "id": row[identity],
                        "field": field,
                        "length": len(value),
                        "minimum": rules[field],
                        "value": value[:80],
                    })
                for phrase in FORBIDDEN_PHRASES:
                    if phrase.lower() in value.lower():
                        issues.append({
                            "table": table,
                            "id": row[identity],
                            "field": field,
                            "length": len(value),
                            "minimum": rules[field],
                            "value": f"命中占位词“{phrase}”：{value[:60]}",
                        })
    conn.close()
    return issues


def main() -> None:
    issues = audit()
    by_table: dict[str, int] = {}
    for issue in issues:
        by_table[issue["table"]] = by_table.get(issue["table"], 0) + 1
    print(f"内容完整度审查：发现 {len(issues)} 个待扩充字段。")
    for table, count in sorted(by_table.items()):
        print(f"- {table}: {count}")
    for issue in issues[:120]:
        print(
            f"{issue['table']}#{issue['id']} {issue['field']} "
            f"{issue['length']}/{issue['minimum']}：{issue['value']}"
        )


if __name__ == "__main__":
    main()
