"""Deterministic checks for trusted-source web search parsing and ranking."""

from __future__ import annotations

from unittest.mock import patch

from backend import web_search


RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss><channel>
<item><title>毛公山官方活动</title><link>https://www.qingdao.gov.cn/example</link><description>城阳毛公山近期活动公开信息</description><pubDate>Sun, 16 Aug 2026 10:00:00 GMT</pubDate></item>
<item><title>不相关页面</title><link>https://example.com/other</link><description>其他内容</description></item>
</channel></rss>""".encode("utf-8")


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int) -> bytes:
        return RSS


def main() -> None:
    with patch.object(web_search, "urlopen", return_value=FakeResponse()):
        results = web_search.search_web("毛公山最近有什么活动？")
    assert len(results) == 1
    assert results[0]["source_url"] == "https://www.qingdao.gov.cn/example"
    assert results[0]["authority"] == "official"
    assert results[0]["source_type"] == "web_search"
    print("All trusted web-search checks passed.")


if __name__ == "__main__":
    main()
