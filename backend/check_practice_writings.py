"""校验实践文稿的数据库同步结果与内容性质标记。"""

from __future__ import annotations

import sqlite3

try:
    from .config import DB_PATH
    from .sync_practice_writings import PRACTICE_WRITINGS
except ImportError:
    from config import DB_PATH
    from sync_practice_writings import PRACTICE_WRITINGS


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    missing_logs: list[str] = []
    missing_knowledge: list[str] = []
    invalid_interviews: list[str] = []

    for entry in PRACTICE_WRITINGS:
        log = conn.execute(
            "SELECT title, category, source, content FROM research_logs WHERE title=?",
            (entry["title"],),
        ).fetchone()
        if not log:
            missing_logs.append(entry["title"])
            continue
        knowledge = conn.execute(
            "SELECT title, category, verification_status FROM knowledge_documents WHERE title=?",
            (f"实践调研：{entry['title']}",),
        ).fetchone()
        if not knowledge:
            missing_knowledge.append(entry["title"])
        if entry["category"] == "访谈整理稿":
            status = knowledge["verification_status"] if knowledge else ""
            searchable = f"{log['source']} {log['content']}"
            if status != "情景化整理稿" or "整理稿" not in searchable:
                invalid_interviews.append(entry["title"])

    conn.close()
    if missing_logs or missing_knowledge or invalid_interviews:
        raise SystemExit(
            "校验失败："
            f"缺少日志 {missing_logs}；"
            f"缺少知识文档 {missing_knowledge}；"
            f"访谈标识不完整 {invalid_interviews}"
        )
    print(f"实践文稿校验通过：{len(PRACTICE_WRITINGS)} 条，访谈真实性标识完整。")


if __name__ == "__main__":
    main()
