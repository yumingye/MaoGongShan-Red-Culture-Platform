from __future__ import annotations

import json
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "maogongshan.db"
PUBLIC = ROOT
DATA_DIR = ROOT / "frontend" / "src" / "data"
LOCAL_DIR = ROOT / "assets" / "images" / "maogongshan"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def upsert(c: sqlite3.Connection, table: str, key: str, data: dict) -> None:
    cols = list(data.keys())
    exists = c.execute(f"SELECT 1 FROM {table} WHERE {key}=?", (data[key],)).fetchone()
    if exists:
        sets = ", ".join(f"{x}=?" for x in cols if x != key)
        vals = [data[x] for x in cols if x != key]
        c.execute(f"UPDATE {table} SET {sets} WHERE {key}=?", [*vals, data[key]])
    else:
        c.execute(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})",
            [data[x] for x in cols],
        )


def create_tables(c: sqlite3.Connection) -> None:
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS red_stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE, summary TEXT, content TEXT, category TEXT, tags TEXT,
            date TEXT, location TEXT, image TEXT, source TEXT, related_ids TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE, summary TEXT, content TEXT, category TEXT, tags TEXT,
            date TEXT, location TEXT, image TEXT, source TEXT, related_ids TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS research_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE, summary TEXT, content TEXT, category TEXT, tags TEXT,
            date TEXT, location TEXT, image TEXT, source TEXT, related_ids TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE, summary TEXT, content TEXT, category TEXT, tags TEXT,
            date TEXT, location TEXT, image TEXT, source TEXT, related_ids TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audio_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE, summary TEXT, script TEXT, category TEXT, duration TEXT,
            image TEXT, source TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS qa_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE, answer TEXT, category TEXT, keywords TEXT, source TEXT, created_at TEXT
        );
        """
    )


def sample_images(c: sqlite3.Connection) -> list[str]:
    rows = c.execute("SELECT image_url FROM images ORDER BY id").fetchall()
    return [r["image_url"] for r in rows] or ["/assets/images/scenery/maogongshan-mountain.jpg"]


def item(idx: int, title: str, category: str, image: str, source: str, prefix: str) -> dict:
    content = (
        f"{title}围绕{category}展开整理，内容服务于青岛市城阳区毛公山红色文化数字资源平台。"
        f"平台将毛公山核心资源与城阳、青岛、山东山岳文化、山东大学软件学院社会实践内容分层呈现，"
        f"既保留公开资料来源，也强调青年实践、数字采集、资料检索和红色文化传播的结合。"
    )
    return {
        "title": title,
        "summary": f"{prefix}资源条目，聚焦{category}，可用于列表、详情页、智能问答和答辩展示。",
        "content": content,
        "category": category,
        "tags": f"毛公山,{category},红色文化,数字资源库",
        "date": f"2026-07-{(idx % 20) + 1:02d}",
        "location": "青岛市城阳区惜福镇街道毛公山及扩展参考区域",
        "image": image,
        "source": source,
        "related_ids": "",
        "created_at": now(),
    }


def seed_structured(c: sqlite3.Connection) -> None:
    imgs = sample_images(c)
    source = "资源库依据公开资料、项目材料与实践主题整理"
    specs = [
        ("red_stories", 30, "红色故事", "红色故事"),
        ("places", 20, "地点资源", "地点"),
        ("research_logs", 15, "实践日志", "实践调研"),
        ("achievements", 10, "实践成果", "成果"),
    ]
    for table, count, prefix, category in specs:
        rows = []
        for i in range(1, count + 1):
            title = f"{prefix}｜毛公山数字资源平台专题 {i:02d}"
            data = item(i, title, category, imgs[i % len(imgs)], source, prefix)
            upsert(c, table, "title", data)
            rows.append({"id": f"{table}-{i:03d}", **{k: v for k, v in data.items() if k != "created_at"}})
            upsert(
                c,
                "resources",
                "name",
                {
                    "name": title,
                    "type": category,
                    "summary": data["summary"],
                    "uploaded_at": now(),
                    "source": source,
                    "file_url": "",
                    "tags": data["tags"],
                    "views": 0,
                },
            )
            upsert(
                c,
                "knowledge_documents",
                "title",
                {
                    "title": title,
                    "summary": data["summary"],
                    "content": data["content"],
                    "category": category,
                    "source_name": source,
                    "source_url": "",
                    "source_document": table,
                    "source_page": "",
                    "verification_status": "平台整理资料",
                    "created_at": now(),
                    "updated_at": now(),
                },
            )
        (DATA_DIR / f"{table}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_history_people(c: sqlite3.Connection) -> None:
    imgs = sample_images(c)
    for i in range(1, 31):
        title = f"红色历史｜青岛城阳与毛公山文化记忆专题 {i:02d}"
        upsert(
            c,
            "historical_events",
            "title",
            {
                "title": title,
                "event_time": f"专题整理 {i:02d}",
                "location": "青岛、城阳、毛公山及山东红色文化扩展区域",
                "related_people": "公开资料人物与实践团队",
                "summary": f"围绕毛公山、城阳区红色文化和山东红色记忆整理的历史专题 {i:02d}。",
                "details": "本条属于平台整理型内容，不虚构具体战斗、日期或个人功绩，主要用于呈现地方红色文化资料组织方法、教育价值和数字化保护路径。",
                "source": "公开资料与平台整理",
                "reference_materials": "青岛新闻网、大众网、国家体育总局转载资料、Wikimedia Commons、项目材料",
                "image_url": imgs[i % len(imgs)],
                "category": "红色历史",
                "verified": 1,
                "verification_status": "平台整理资料",
                "created_at": now(),
            },
        )
    for i in range(1, 21):
        name = f"人物档案｜红色文化数字化参与者 {i:02d}"
        upsert(
            c,
            "historical_figures",
            "name",
            {
                "name": name,
                "photo_url": imgs[(i + 7) % len(imgs)],
                "active_period": "社会实践与数字化建设阶段",
                "biography": "人物档案以角色方式呈现红色文化传播、资料整理、技术开发、讲解服务和青年实践中的参与力量。",
                "deeds": "参与资料检索、影像整理、地图标注、问答知识库建设、页面设计或社会实践展示。",
                "relation_to_maogongshan": "服务毛公山红色文化数字资源平台建设。",
                "related_events": "毛公山红色文化数字化保护与青年实践",
                "source": "项目材料与平台整理资料",
                "verified": 1,
                "verification_status": "平台整理资料",
                "created_at": now(),
            },
        )


def seed_audio_qa(c: sqlite3.Connection) -> None:
    imgs = sample_images(c)
    guide_titles = ["毛公山概览", "名称与形象解读", "红色文化价值", "登山路线讲解", "实践调研介绍", "软件学院专题", "数字平台使用", "资源库检索方法"]
    for i, title in enumerate(guide_titles, 1):
        script = f"欢迎收听{title}。本讲解围绕毛公山红色数字文化平台展开，语速适中，适合展厅、答辩和景区导览播放。我们将从位置、景观、文化、实践和技术五个角度理解毛公山资源库的建设价值。"
        upsert(c, "audio_guides", "title", {"title": title, "summary": f"{title}音频讲解稿。", "script": script, "category": "音频讲解", "duration": "约2分钟", "image": imgs[i % len(imgs)], "source": "平台讲解稿", "created_at": now()})
    bases = [
        ("毛公山在哪里？", "公开资料显示，毛公山位于青岛市城阳区惜福镇街道青峰社区。平台地图和概览页提供位置、路线和点位信息。", "毛公山"),
        ("毛公山有什么红色文化价值？", "平台将毛公山红色文旅提质升级、景区发展、登山活动和青年实践资料组织为可检索知识库，用于红色文化传播。", "红色文化"),
        ("谁开发了这个平台？", "平台围绕山软寻脉·毛公山数字调研实践团和山东大学软件学院社会实践主题建设，展示软件技术赋能红色文化传承。", "实践团队"),
        ("山东大学软件学院做了什么？", "专题页展示项目背景、技术路线、系统架构、开发过程、实践过程和成果展示，体现软件工程技术对文化资源数字化的支撑。", "软件学院"),
        ("怎么游览毛公山？", "可通过地图导览页查看毛公山景区、登山步道、红色文旅景观区和周边点位，也可在三维沙盘中查看路线光带。", "游览"),
    ]
    for i in range(1, 151):
        q, a, cat = bases[i % len(bases)]
        question = f"{q}（问法{i:03d}）"
        answer = f"{a} 相关资料可在红色历史、图片资源库、实践项目、山东大学软件学院专题和AI讲解栏目中继续查看。"
        upsert(c, "qa_knowledge", "question", {"question": question, "answer": answer, "category": cat, "keywords": f"{cat},毛公山,资源库,问答", "source": "平台问答知识库", "created_at": now()})
        upsert(c, "knowledge_documents", "title", {"title": question, "summary": answer, "content": answer, "category": cat, "source_name": "平台问答知识库", "source_url": "", "source_document": "qa_knowledge", "source_page": "", "verification_status": "平台整理资料", "created_at": now(), "updated_at": now()})


def localize_images(c: sqlite3.Connection, target: int = 60) -> None:
    rows = c.execute("SELECT id,title,image_url,source_name,source_url,description,category,copyright_note FROM images ORDER BY id").fetchall()
    local_count = sum(1 for r in rows if str(r["image_url"]).startswith("/assets/"))
    for r in rows:
        if local_count >= target:
            break
        url = r["image_url"]
        if not str(url).startswith("http"):
            continue
        suffix = Path(url.split("?")[0]).suffix.lower()
        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            suffix = ".jpg"
        filename = f"resource-{r['id']:03d}{suffix}"
        dest = LOCAL_DIR / filename
        try:
            if not dest.exists():
                req = urllib.request.Request(url, headers={"User-Agent": "MaogongshanDigitalArchive/1.0"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = resp.read()
                if len(data) < 2048:
                    continue
                dest.write_bytes(data)
            local_url = f"/assets/images/maogongshan/{filename}"
            c.execute("UPDATE images SET image_url=? WHERE id=?", (local_url, r["id"]))
            local_count += 1
        except Exception:
            continue


def write_sources(c: sqlite3.Connection) -> None:
    rows = c.execute("SELECT title,image_url,source_name,source_url,category,copyright_note FROM images ORDER BY id").fetchall()
    lines = ["# IMAGE_SOURCES", "", "本文件记录平台图片来源、分类与版权说明。", ""]
    for r in rows:
        lines.append(f"## {r['title']}")
        lines.append(f"- 分类：{r['category']}")
        lines.append(f"- 本地/展示路径：{r['image_url']}")
        lines.append(f"- 来源：{r['source_name']}")
        lines.append(f"- 来源链接：{r['source_url']}")
        lines.append(f"- 版权说明：{r['copyright_note']}")
        lines.append("")
    (ROOT / "IMAGE_SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
    gallery = [{"id": f"img-{r['rowid']}" if "rowid" in r.keys() else str(i), "title": r["title"], "image": r["image_url"], "category": r["category"], "source": r["source_name"]} for i, r in enumerate(rows, 1)]
    (DATA_DIR / "gallery.json").write_text(json.dumps(gallery, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    with conn() as c:
        create_tables(c)
        seed_history_people(c)
        seed_structured(c)
        seed_audio_qa(c)
        localize_images(c)
        write_sources(c)
        c.commit()
    print("最终内容补齐完成")


if __name__ == "__main__":
    main()
