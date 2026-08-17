"""Deterministic checks for trusted-source web search parsing and ranking."""

from __future__ import annotations

from unittest.mock import patch

from backend import web_search


HTML = """<html><body><ol>
<li class="res-list"><h3 class="res-title"><a href="https://www.so.com/link" data-mdurl="https://www.qingdao.gov.cn/example">毛公山官方活动</a></h3><span class="res-list-summary">城阳毛公山近期活动公开信息</span></li>
<li class="res-list"><h3 class="res-title"><a href="https://example.com/other">不相关页面</a></h3><span class="res-list-summary">青岛地铁其他内容</span></li>
</ol></body></html>""".encode("utf-8")


def main() -> None:
    web_search._CACHE.clear()
    with patch.object(web_search, "_fetch_html", return_value=HTML):
        results, cache_hit = web_search.search_web_with_meta("毛公山最近有什么活动？")
        cached_results, cached_hit = web_search.search_web_with_meta("毛公山最近有什么活动？")
    assert len(results) == 1
    assert not cache_hit and cached_hit and cached_results == results
    assert results[0]["source_url"] == "https://www.qingdao.gov.cn/example"
    assert results[0]["authority"] == "official"
    assert results[0]["source_tier"] == 1
    assert results[0]["source_type"] == "web_search"
    stale = {
        "title": "2022年毛公山旧活动",
        "summary": "城阳毛公山往年活动",
        "source_url": "https://www.qingdao.gov.cn/2022/example.shtml",
    }
    assert web_search._relevance("毛公山最近有什么活动？", stale) < 45
    print("All trusted web-search checks passed.")


if __name__ == "__main__":
    main()
