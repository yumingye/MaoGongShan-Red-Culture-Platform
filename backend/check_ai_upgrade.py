"""Regression checks for personas, metadata hierarchy, retrieval and optional live LLM."""

from __future__ import annotations

import argparse
import sqlite3
import time

from backend.ai_service import generate_rag_answer, llm_status
from backend.config import DB_PATH
from backend.retrieval_service import backfill_knowledge_metadata, classify_question, hybrid_search

QUESTIONS = [
    "介绍一下毛公山",
    "介绍一下毛公山的历史文化",
    "毛公山为什么叫毛公山？",
    "毛公山在哪里？",
    "毛公山有什么红色故事？",
    "毛公山有什么值得看的？",
    "怎么游览毛公山？",
    "毛公山和青岛城阳是什么关系？",
    "这个项目是谁开发的？",
    "软件学院为什么做这个项目？",
    "山东大学学生为什么适合在毛公山开展社会实践？",
]
WEB_FIRST_EXPECTATIONS = {
    "介绍一下毛公山": "scenic_guide",
    "介绍一下毛公山的历史文化": "history",
    "毛公山为什么叫毛公山？": "history",
    "毛公山在哪里？": "scenic_guide",
    "毛公山有什么红色故事？": "history",
    "毛公山有什么值得看的？": "travel",
    "怎么游览毛公山？": "travel",
}
RAG_FIRST_EXPECTATIONS = {
    "这个项目是谁开发的？": "project_info",
    "软件学院为什么做这个项目？": "university_practice",
    "山东大学学生为什么适合在毛公山开展社会实践？": "university_practice",
}
FOLLOW_UPS = ["介绍一下毛公山", "它为什么叫这个名字？", "最值得看的是什么？", "那如果第一次去应该怎么逛？"]
UNRELATED = ("青岛地铁", "烟台山", "潍坊地图", "梅园新村")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--live-limit", type=int, default=2)
    args = parser.parse_args()
    for question, expected in WEB_FIRST_EXPECTATIONS.items():
        assert classify_question(question) == expected, (question, classify_question(question))
    for question, expected in RAG_FIRST_EXPECTATIONS.items():
        assert classify_question(question) == expected, (question, classify_question(question))
    assert classify_question("毛公山最近有什么活动？") == "realtime"
    assert classify_question("毛公山现在开放吗？") == "realtime"
    print("PASS web-first / RAG-first intent routing")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        backfill_knowledge_metadata(conn)
        conn.commit()
        for question in QUESTIONS:
            docs, quality, _ = hybrid_search(conn, question, [], 6)
            titles = " ".join(str(doc.get("title") or "") for doc in docs)
            if "毛公山" in question:
                assert docs, f"missing retrieval: {question}"
                assert all(int(doc.get("knowledge_level") or 6) < 6 for doc in docs), (question, titles)
                assert not any(term in titles for term in UNRELATED), (question, titles)
            print(f"PASS retrieval {quality}: {question} -> {len(docs)} docs")

        docs, _, contextual = hybrid_search(
            conn,
            "它为什么叫这个名字？",
            [{"role": "user", "content": "介绍一下毛公山"}, {"role": "assistant", "content": "毛公山位于城阳区。"}],
            6,
        )
        assert "承接上文：毛公山" in contextual and docs
        print("PASS multi-turn retrieval context")

        if args.live:
            assert llm_status()["configured"], "LLM is not configured"
            history: list[dict[str, str]] = []
            for question in FOLLOW_UPS[: max(1, args.live_limit)]:
                docs, quality, _ = hybrid_search(conn, question, history, 6)
                started = time.monotonic()
                answer = generate_rag_answer(question, docs, history, persona="guide", retrieval_quality=quality)
                assert len(answer) >= 80
                print(f"LIVE guide {question} ({round((time.monotonic() - started) * 1000)} ms):\n{answer}\n")
                history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])


if __name__ == "__main__":
    main()
