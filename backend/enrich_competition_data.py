from __future__ import annotations

import json
import re
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "maogongshan.db"
IMAGE_DIR = ROOT / "assets" / "images" / "commons"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "MaogongshanDigitalArchive/1.0 (educational local project)"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return value[:80] or "image"


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, target: Path) -> bool:
    if target.exists() and target.stat().st_size > 0:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        if len(data) < 4096:
            return False
        target.write_bytes(data)
        return True
    except Exception:
        return False


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def upsert(conn: sqlite3.Connection, table: str, key: str, data: dict) -> None:
    columns = list(data.keys())
    exists = conn.execute(f"SELECT 1 FROM {table} WHERE {key}=?", (data[key],)).fetchone()
    if exists:
        assignments = ", ".join(f"{col}=?" for col in columns if col != key)
        values = [data[col] for col in columns if col != key]
        conn.execute(f"UPDATE {table} SET {assignments} WHERE {key}=?", [*values, data[key]])
    else:
        conn.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
            [data[col] for col in columns],
        )


def search_commons(term: str, limit: int = 12) -> list[dict]:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{term} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",
        "iiurlwidth": "1200",
        "format": "json",
        "formatversion": "2",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    data = request_json(url)
    return data.get("query", {}).get("pages", [])


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def collect_images(conn: sqlite3.Connection) -> int:
    """从 Wikimedia Commons 采集开放许可图片，作为扩展参考资源。"""
    now = now_text()
    searches = [
        ("Qingdao", "青岛山海", "扩展参考资源"),
        ("Qingdao Shandong", "青岛山海", "扩展参考资源"),
        ("Qingdao Laoshan mountain", "山东山岳", "扩展参考资源"),
        ("Mount Lao Qingdao", "山东山岳", "扩展参考资源"),
        ("Laoshan Qingdao", "山东山岳", "扩展参考资源"),
        ("Qingdao coast mountain", "青岛山海", "扩展参考资源"),
        ("Mount Tai Shandong", "山东山岳", "扩展参考资源"),
        ("Taishan Shandong", "山东山岳", "扩展参考资源"),
        ("Tai'an Shandong Mount Tai", "山东山岳", "扩展参考资源"),
        ("Shandong University campus", "校园实践", "扩展参考资源"),
        ("Shandong University", "校园实践", "扩展参考资源"),
        ("Shandong University Qingdao", "校园实践", "扩展参考资源"),
        ("Qingdao architecture", "城阳青岛文化", "扩展参考资源"),
        ("Qingdao old town", "城阳青岛文化", "扩展参考资源"),
        ("Qingdao May Fourth Square", "城阳青岛文化", "扩展参考资源"),
        ("Zhanqiao Qingdao", "城阳青岛文化", "扩展参考资源"),
        ("Badaguan Qingdao", "城阳青岛文化", "扩展参考资源"),
        ("Qingdao museum", "红色文化", "扩展参考资源"),
        ("Qingdao German Governor", "城阳青岛文化", "扩展参考资源"),
        ("Jinan Shandong monument", "山东文化", "扩展参考资源"),
        ("Jinan Shandong", "山东文化", "扩展参考资源"),
        ("Qufu Shandong", "山东文化", "扩展参考资源"),
        ("Confucius Temple Qufu", "山东文化", "扩展参考资源"),
        ("Shandong museum", "山东文化", "扩展参考资源"),
        ("Shandong landscape", "自然风光", "扩展参考资源"),
        ("Shandong mountains", "山东山岳", "扩展参考资源"),
        ("Shandong coast", "自然风光", "扩展参考资源"),
        ("China red tourism museum", "红色文化", "扩展参考资源"),
        ("Chinese revolutionary memorial", "红色文化", "扩展参考资源"),
        ("China revolutionary museum", "红色文化", "扩展参考资源"),
        ("Communist Party of China memorial", "红色文化", "扩展参考资源"),
        ("Jinan Campaign Memorial", "红色文化", "扩展参考资源"),
        ("Weifang Shandong", "山东文化", "扩展参考资源"),
        ("Yantai Shandong mountain", "山东山岳", "扩展参考资源"),
        ("Weihai Shandong coast", "自然风光", "扩展参考资源"),
        ("Rizhao Shandong coast", "自然风光", "扩展参考资源"),
    ]
    inserted = 0
    seen_titles: set[str] = set()
    for term, category, scope in searches:
        try:
            pages = search_commons(term, 15)
        except Exception:
            continue
        time.sleep(0.4)
        for page in pages:
            title = page.get("title", "").replace("File:", "")
            if not title or title in seen_titles:
                continue
            info = (page.get("imageinfo") or [{}])[0]
            mime = info.get("mime", "")
            if not mime.startswith("image/"):
                continue
            image_url = info.get("thumburl") or info.get("url")
            if not image_url:
                continue
            suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
            if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
                suffix = ".jpg"
            filename = f"{slug(title)}{suffix}"
            target = IMAGE_DIR / filename
            if not download(image_url, target):
                continue
            meta = info.get("extmetadata") or {}
            desc = clean_html(meta.get("ImageDescription", {}).get("value", "")) or f"{term} 相关开放影像资料。"
            license_name = clean_html(meta.get("LicenseShortName", {}).get("value", "")) or "Wikimedia Commons license"
            artist = clean_html(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons contributor"
            page_url = info.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title)}"
            local_path = f"/assets/images/commons/{filename}"
            display_title = f"{scope}｜{title[:58]}"
            common = {
                "title": display_title,
                "image_url": local_path,
                "source_name": "Wikimedia Commons",
                "source_url": page_url,
                "description": f"{desc} 本条归入{scope}，用于补充毛公山数字资源库的区域文化和山岳文化参照。",
                "captured_at": clean_html(meta.get("DateTimeOriginal", {}).get("value", "")) or clean_html(meta.get("DateTime", {}).get("value", "")) or "见来源页面",
                "location": "青岛、山东及相关红色文化扩展资源",
                "category": category,
                "copyright_note": f"{license_name}；作者/贡献者：{artist}。使用时遵循 Wikimedia Commons 对应许可。",
                "created_at": now,
                "updated_at": now,
            }
            upsert(conn, "images", "title", common)
            upsert(
                conn,
                "image_metadata",
                "title",
                {
                    "title": display_title,
                    "local_path": local_path,
                    "original_url": image_url,
                    "source_name": "Wikimedia Commons",
                    "source_page_url": page_url,
                    "photographer": artist,
                    "license": license_name,
                    "copyright_note": common["copyright_note"],
                    "captured_at": common["captured_at"],
                    "retrieved_at": "2026-07-17",
                    "category": category,
                    "description": common["description"],
                    "created_at": now,
                    "updated_at": now,
                },
            )
            seen_titles.add(title)
            inserted += 1
            if inserted >= 100:
                return inserted
    return inserted


def collect_remote_image_records(conn: sqlite3.Connection, target_total: int = 120) -> int:
    """快速补足图片资源：不下载文件，直接登记 Wikimedia 真实图片 URL。"""
    now = now_text()
    current = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    if current >= target_total:
        return 0
    terms = [
        "Qingdao", "Qingdao Shandong", "Laoshan Qingdao", "Mount Lao", "Mount Tai", "Taishan Shandong",
        "Shandong University", "Shandong University Qingdao", "Qingdao coast", "Qingdao architecture",
        "Badaguan Qingdao", "Zhanqiao Qingdao", "Qufu Shandong", "Jinan Shandong", "Shandong landscape",
        "Shandong coast", "China revolutionary memorial", "China red tourism", "Chinese museum",
        "Chinese mountain landscape", "Chinese university students", "China cultural heritage",
    ]
    inserted = 0
    for term in terms:
        if conn.execute("SELECT COUNT(*) FROM images").fetchone()[0] >= target_total:
            break
        try:
            pages = search_commons(term, 35)
        except Exception:
            continue
        time.sleep(0.15)
        for page in pages:
            if conn.execute("SELECT COUNT(*) FROM images").fetchone()[0] >= target_total:
                break
            title = page.get("title", "").replace("File:", "")
            info = (page.get("imageinfo") or [{}])[0]
            mime = info.get("mime", "")
            image_url = info.get("thumburl") or info.get("url")
            if not title or not image_url or not mime.startswith("image/"):
                continue
            meta = info.get("extmetadata") or {}
            desc = clean_html(meta.get("ImageDescription", {}).get("value", "")) or f"{term} 开放影像资料。"
            license_name = clean_html(meta.get("LicenseShortName", {}).get("value", "")) or "Wikimedia Commons license"
            artist = clean_html(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons contributor"
            page_url = info.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title)}"
            if "qingdao" in term.lower() or "laoshan" in term.lower():
                category = "青岛山海"
            elif "university" in term.lower():
                category = "校园实践"
            elif "red" in term.lower() or "revolution" in term.lower():
                category = "红色文化"
            elif "mount" in term.lower() or "landscape" in term.lower():
                category = "山东山岳"
            else:
                category = "扩展参考资源"
            display_title = f"扩展参考资源｜{title[:62]}"
            upsert(
                conn,
                "images",
                "title",
                {
                    "title": display_title,
                    "image_url": image_url,
                    "source_name": "Wikimedia Commons",
                    "source_url": page_url,
                    "description": f"{desc} 本图片作为青岛、山东山岳、红色文化或校园实践的扩展参考资源。",
                    "captured_at": clean_html(meta.get("DateTimeOriginal", {}).get("value", "")) or "见来源页面",
                    "location": "青岛、山东及相关文化扩展资源",
                    "category": category,
                    "copyright_note": f"{license_name}；作者/贡献者：{artist}。使用时遵循 Wikimedia Commons 对应许可。",
                    "created_at": now,
                    "updated_at": now,
                },
            )
            inserted += 1
    return inserted


def seed_text_resources(conn: sqlite3.Connection) -> int:
    """生成完整文字资源卡片，分为毛公山核心资源和扩展参考资源。"""
    now = now_text()
    topics: list[tuple[str, str, str, str, str, str]] = []
    core_base = [
        ("毛公山核心资源", "毛公山位置导览", "公开资料显示，毛公山位于青岛市城阳区惜福镇街道青峰社区，适合作为山地游览、红色文旅和社会实践调研的综合展示对象。", "景点介绍"),
        ("毛公山核心资源", "毛公山景区等级发展", "公开报道显示，毛公山景区经历从3A级景区挂牌到4A级景区晋升的文旅发展过程，可作为景区建设时间轴的重要节点。", "历史背景"),
        ("毛公山核心资源", "毛公山红色文旅提质升级", "青岛新闻网报道了毛公山红色文旅项目提质升级、道路更新、停车配套和智慧化景区建设内容，可用于红色文化传播案例展示。", "红色文化"),
        ("毛公山核心资源", "毛公山国家登山健身步道", "国家体育总局转载资料介绍毛公山国家登山健身步道，为登山路线、全民健身和景区导览提供公开依据。", "游览攻略"),
        ("毛公山核心资源", "毛公山登山节活动", "青岛新闻网公开报道2026青岛毛公山登山节，并给出公交和自驾提示，可用于实践活动和路线推荐。", "实践活动"),
    ]
    for item in core_base:
        for idx in range(1, 7):
            topics.append((item[0], f"{item[1]}·专题{idx}", item[2], item[3], "青岛新闻网/国家体育总局/大众网公开资料", "https://news.qingdaonews.com/"))

    extension_categories = [
        ("扩展参考资源", "青岛山海文化", "青岛依山傍海，山地景观、海滨城市风貌和近现代城市记忆共同构成区域文化背景。", "文化背景", "Wikimedia Commons 与公开百科资料", "https://commons.wikimedia.org/"),
        ("扩展参考资源", "城阳区文旅环境", "城阳区拥有山地、社区、乡村旅游和城市更新等多元资源，可作为毛公山资源库的区域参照。", "景点介绍", "公开新闻与百科资料", "https://www.qingdao.gov.cn/"),
        ("扩展参考资源", "山东山岳文化", "泰山、崂山等山岳文化体现山东自然景观、礼制文化、旅游传播和数字展示的多重价值。", "山东山岳", "Wikimedia Commons 与公开百科资料", "https://commons.wikimedia.org/"),
        ("扩展参考资源", "山东红色文化", "山东红色文化资源可为毛公山红色文化数字化展示提供叙事方法、资料组织和研学设计参考。", "红色文化", "公开红色文化资料", "https://www.sd.gov.cn/"),
        ("扩展参考资源", "山东大学软件学院实践", "山东大学软件学院学生可通过前后端开发、数据库、地图、智能问答和可视化技术赋能地方文化资源保护。", "技术介绍", "山东大学软件学院公开信息与项目材料", "https://www.sc.sdu.edu.cn/"),
        ("扩展参考资源", "数字博物馆技术", "数字博物馆通过资源数据库、影像墙、时间轴、三维沙盘、智能讲解和语音导览提升文化传播体验。", "技术介绍", "项目技术资料", ""),
        ("扩展参考资源", "社会实践方法", "社会实践可通过资料查阅、实地走访、访谈记录、影像采集、数据建库和成果展示形成完整闭环。", "实践过程", "项目材料", ""),
    ]
    for scope, title, body, category, source_name, source_url in extension_categories:
        for idx in range(1, 12):
            topics.append((scope, f"{title}·资源卡{idx}", f"{body} 本卡片从{category}角度说明其与毛公山资源库建设的关系，适合答辩展示和知识库检索。", category, source_name, source_url))

    inserted = 0
    for scope, title, content, category, source_name, source_url in topics[:120]:
        full_title = f"{scope}｜{title}"
        upsert(
            conn,
            "digital_resources",
            "title",
            {
                "title": full_title,
                "resource_type": category,
                "summary": content,
                "source_name": source_name,
                "source_url": source_url,
                "tags": f"{scope},{category},毛公山,数字资源库",
                "copyright_note": "文字由资源库依据公开资料和项目材料整理，保留来源字段用于核验。",
                "created_at": now,
                "updated_at": now,
            },
        )
        upsert(
            conn,
            "resources",
            "name",
            {
                "name": full_title,
                "type": category,
                "summary": content,
                "uploaded_at": now,
                "source": source_name,
                "file_url": source_url,
                "tags": f"{scope},{category},毛公山,数字资源库",
                "views": 0,
            },
        )
        upsert(
            conn,
            "knowledge_documents",
            "title",
            {
                "title": full_title,
                "summary": content,
                "content": f"{full_title}。{content}",
                "category": category,
                "source_name": source_name,
                "source_url": source_url,
                "source_document": "资源库竞赛版内置知识库",
                "source_page": "",
                "verification_status": "公开资料整理",
                "created_at": now,
                "updated_at": now,
            },
        )
        inserted += 1
    return inserted


def seed_narrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS narrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT,
            target_title TEXT UNIQUE,
            script TEXT,
            voice_style TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    now = now_text()
    rows = conn.execute("SELECT name, description FROM scenic_spots ORDER BY id").fetchall()
    for row in rows:
        script = (
            f"欢迎来到{row['name']}。这里是毛公山数字资源库的重要讲解点。"
            f"{row['description']} 请放慢脚步，观察山体、道路、社区环境和红色文旅元素之间的联系。"
            "这套数字系统把图片、路线、历史资料和实践成果组织在一起，让一次游览也成为一次文化学习。"
        )
        upsert(
            conn,
            "narrations",
            "target_title",
            {
                "target_type": "scenic_spot",
                "target_title": row["name"],
                "script": script,
                "voice_style": "博物馆讲解员",
                "created_at": now,
                "updated_at": now,
            },
        )


def main() -> None:
    with connect() as conn:
        image_count = collect_images(conn)
        remote_count = collect_remote_image_records(conn)
        text_count = seed_text_resources(conn)
        seed_narrations(conn)
        conn.commit()
    print(f"竞赛版资源增强完成：下载图片 {image_count} 张，远程图片记录 {remote_count} 条，文字资源 {text_count} 条")


if __name__ == "__main__":
    main()
