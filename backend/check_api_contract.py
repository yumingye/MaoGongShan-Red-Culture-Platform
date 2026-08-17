"""Non-destructive HTTP contract checks for the running FastAPI service."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = os.getenv("API_TEST_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def request(path: str, *, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request_headers = {"Accept": "application/json", **(headers or {})}
    if payload is not None:
        request_headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(f"{BASE_URL}{path}", data=payload, method=method, headers=request_headers)
    try:
        with urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                payload = None
            else:
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    payload = raw
            return response.status, payload, dict(response.headers)
    except HTTPError as error:
        raw = error.read().decode("utf-8")
        if not raw:
            payload = None
        else:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = raw
        return error.code, payload, dict(error.headers)


def expect(path: str, status: int = 200, **kwargs):
    actual, payload, headers = request(path, **kwargs)
    if actual != status:
        raise AssertionError(f"{kwargs.get('method', 'GET')} {path}: expected {status}, got {actual}: {payload}")
    return payload, headers


def rows(payload):
    return payload if isinstance(payload, list) else payload.get("items", [])


def main() -> int:
    failures: list[str] = []

    def check(label, callback):
        try:
            callback()
            print(f"PASS {label}")
        except Exception as error:  # keep checking independent contracts
            failures.append(f"{label}: {error}")
            print(f"FAIL {label}: {error}")

    list_endpoints = [
        "/api/events", "/api/figures", "/api/resources", "/api/scenic-images",
        "/api/scenic-spots", "/api/categories", "/api/tags", "/api/sources",
        "/api/images", "/api/routes", "/api/narrations", "/api/research-logs",
        "/api/audio-guides", "/api/red-stories", "/api/places", "/api/achievements",
        "/api/learning-articles", "/api/chat/suggestions",
    ]
    object_endpoints = [
        "/api/health", "/api/stats", "/api/home", "/api/project",
        "/api/platform-overview", "/api/guide", "/api/school",
        "/api/chat/status",
        "/api/search?q=" + urlencode({"q": "毛公山"})[2:],
        "/api/search/suggestions?q=" + urlencode({"q": "红色"})[2:],
    ]
    for path in list_endpoints + object_endpoints:
        check(path, lambda path=path: expect(path))

    detail_sources = {
        "/api/events": "/api/events/{id}",
        "/api/figures": "/api/figures/{id}",
        "/api/resources": "/api/resources/{id}",
        "/api/images": "/api/images/{id}",
        "/api/research-logs": "/api/research-logs/{id}",
        "/api/audio-guides": "/api/audio-guides/{id}",
        "/api/red-stories": "/api/red-stories/{id}",
        "/api/places": "/api/places/{id}",
        "/api/achievements": "/api/achievements/{id}",
        "/api/learning-articles": "/api/learning-articles/{id}",
    }
    for source, detail in detail_sources.items():
        def detail_check(source=source, detail=detail):
            payload, _ = expect(source)
            items = rows(payload)
            if not items:
                raise AssertionError("list is empty")
            expect(detail.format(id=items[0]["id"]))
        check(f"detail {detail}", detail_check)

    validation_cases = [
        "/api/events?page=-1&page_size=10",
        "/api/figures?page=1&page_size=501",
        "/api/red-stories?page=0&page_size=12",
        "/api/learning-articles?page=1&page_size=501",
    ]
    for path in validation_cases:
        check(f"validation {path}", lambda path=path: expect(path, 422))

    check("unknown detail returns 404", lambda: expect("/api/events/999999999", 404))
    def anonymous_admin_check():
        status, _, _ = request("/api/admin/events/999999999", method="DELETE")
        if status not in {401, 403, 503}:
            raise AssertionError(f"expected 401, read-only 403 or secure-unconfigured 503, got {status}")
    check("admin route rejects anonymous write", anonymous_admin_check)
    check("blank chat is rejected", lambda: expect("/api/chat", 422, method="POST", body={"question": "   "}))
    check("oversized chat is rejected", lambda: expect("/api/chat", 422, method="POST", body={"question": "问" * 301}))

    qa_questions = ["毛公三有啥特色", "毛公山怎么走", "长征精神是什么", "第一次去怎么游览毛公山"]
    for question in qa_questions:
        def qa_check(question=question):
            payload, _ = expect("/api/chat", method="POST", body={"question": question})
            if len(payload.get("answer", "")) < 40 or not payload.get("sources"):
                raise AssertionError("answer or sources are incomplete")
        check(f"chat {question}", qa_check)

    def chat_history_check():
        payload, _ = expect(
            "/api/chat",
            method="POST",
            body={
                "question": "那它还有哪些特色？",
                "persona": "guide",
                "history": [
                    {"role": "user", "content": "毛公山在哪里？"},
                    {"role": "assistant", "content": "请以资料库来源为准。"},
                ],
            },
        )
        expected = {"answer", "sources", "mode", "degraded", "notice", "provider_error", "follow_up_suggestions", "persona", "rag_used", "web_search_used", "retrieval_quality", "latency_ms"}
        if not expected.issubset(payload):
            raise AssertionError(f"missing chat response fields: {sorted(expected - set(payload))}")
        if payload.get("persona") != "guide":
            raise AssertionError("guide persona was not preserved")
    check("chat multi-turn response contract", chat_history_check)

    def unknown_qa_check():
        payload, _ = expect("/api/chat", method="POST", body={"question": "月球实时天气和火星公交班次"})
        if payload.get("sources"):
            raise AssertionError("unknown real-time question should not invent sources")
        if len(payload.get("answer", "")) < 20:
            raise AssertionError("unknown question needs a natural fallback answer")
    check("chat unknown question fallback", unknown_qa_check)

    def blank_search_check():
        payload, _ = expect("/api/search?q=%20%20%20")
        if any(payload.values()):
            raise AssertionError("whitespace-only search should return empty groups")
    check("blank search normalization", blank_search_check)

    expected_search_groups = {
        "events", "figures", "resources", "images", "spots", "learning",
        "stories", "places", "achievements", "research",
    }

    def search_group_check(query: str, expected_group: str | None = None):
        path = "/api/search?" + urlencode({"q": query})
        payload, _ = expect(path)
        if set(payload) != expected_search_groups:
            raise AssertionError(f"unexpected groups: {sorted(payload)}")
        if expected_group:
            if not payload.get(expected_group):
                raise AssertionError(f"{query!r} returned no {expected_group} results")
        elif not any(payload.values()):
            raise AssertionError(f"{query!r} returned no result in any group")

    search_cases = [
        ("毛公山在哪里", None),
        ("毛公三", None),
        ("红色人物", "figures"),
        ("红色故事", "stories"),
        ("实践成果", "achievements"),
        ("沂蒙精神", None),
        ("青岛", None),
    ]
    for query, expected_group in search_cases:
        check(
            f"search relevance {query}",
            lambda query=query, expected_group=expected_group: search_group_check(query, expected_group),
        )

    def cors_check():
        _, headers = expect("/api/health", headers={"Origin": "http://127.0.0.1:5173"})
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        if normalized_headers.get("access-control-allow-origin") != "http://127.0.0.1:5173":
            raise AssertionError("allowed development origin was not echoed")
    check("CORS development origin", cors_check)

    def cors_preflight_check():
        _, headers = expect(
            "/api/chat",
            method="OPTIONS",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        if normalized_headers.get("access-control-allow-origin") != "http://127.0.0.1:5173":
            raise AssertionError("preflight did not allow the configured origin")
    check("CORS preflight", cors_preflight_check)

    def security_headers_check():
        _, headers = expect("/api/health")
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        expected = {
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY",
            "referrer-policy": "strict-origin-when-cross-origin",
        }
        for key, value in expected.items():
            if normalized_headers.get(key) != value:
                raise AssertionError(f"missing or invalid security header {key}")
    check("API security headers", security_headers_check)

    if failures:
        print("\nContract check failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nAll API contract checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
