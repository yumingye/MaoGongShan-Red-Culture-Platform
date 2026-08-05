"""从 Wikidata 查询人物实体候选和 Commons 肖像字段，供人工核对。"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


NAMES = [
    "刘少奇", "任弼时", "陈云", "董必武", "彭德怀", "林伯渠", "贺龙",
    "刘伯承", "陈毅", "聂荣臻", "徐向前", "叶剑英", "罗荣桓", "粟裕",
    "雷锋", "焦裕禄", "王进喜", "钱学森", "邓稼先", "郭永怀", "袁隆平",
    "黄旭华", "屠呦呦", "杨利伟", "张富清", "申纪兰",
]

HEADERS = {
    "User-Agent": "MaogongshanCulturePlatform/1.0 (educational project)"
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> None:
    for name in NAMES:
        params = urllib.parse.urlencode({
            "action": "wbsearchentities",
            "search": name,
            "language": "zh",
            "uselang": "zh",
            "type": "item",
            "limit": 3,
            "format": "json",
            "origin": "*",
        })
        search = get_json(f"https://www.wikidata.org/w/api.php?{params}")
        candidates = search.get("search", [])
        if not candidates:
            print(f"{name} => no candidate")
            continue
        ids = "|".join(item["id"] for item in candidates)
        entities = get_json(
            "https://www.wikidata.org/w/api.php?"
            + urllib.parse.urlencode({
                "action": "wbgetentities",
                "ids": ids,
                "props": "claims",
                "format": "json",
                "origin": "*",
            })
        ).get("entities", {})
        rows = []
        for item in candidates:
            claims = entities.get(item["id"], {}).get("claims", {})
            image_claim = claims.get("P18", [])
            image_name = ""
            if image_claim:
                image_name = image_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            rows.append(
                f"{item['id']} {item.get('label', '')} "
                f"[{item.get('description', '')}] P18={image_name or '-'}"
            )
        print(f"{name} => {' || '.join(rows)}")


if __name__ == "__main__":
    main()
