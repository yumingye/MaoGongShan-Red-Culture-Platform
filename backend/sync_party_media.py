"""下载经核验的党史照片、生成专题信息图并同步章节媒体表。

脚本可重复执行。同一 media_key 使用 UPSERT 更新，不会重复导入。
"""

from __future__ import annotations

import html
import hashlib
import io
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

try:
    from backend.augment_red_learning import ARTICLES
    from backend.party_media_catalog import CURATED_COMMONS_MEDIA, CURATED_FIGURES, FIGURE_PROFILES
except ModuleNotFoundError:
    from augment_red_learning import ARTICLES
    from party_media_catalog import CURATED_COMMONS_MEDIA, CURATED_FIGURES, FIGURE_PROFILES


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "maogongshan.db"
ASSET_DIR = ROOT / "assets" / "images" / "party-history"
MANIFEST_PATH = ROOT / "frontend" / "public" / "data" / "party-media-manifest.json"
PUBLIC_PREFIX = "/assets/images/party-history"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

STAGE_INFO = [
    ("may-fourth", "五四运动与马克思主义传播", "1919—1921", "北京并影响全国", "思想启蒙与建党准备"),
    ("party-founding", "中国共产党创建与建党初期", "1921—1923", "上海、嘉兴及早期党组织活动地区", "党的创建与工人运动"),
    ("great-revolution", "大革命时期", "1924—1927", "全国多地", "统一战线、北伐与群众运动"),
    ("agrarian-revolution", "土地革命战争时期", "1927—1937", "革命根据地与长征沿线", "武装斗争、根据地建设与战略转移"),
    ("war-resistance", "全民族抗日战争时期", "1937—1945", "中国各抗日战场", "抗日民族统一战线与民族解放"),
    ("liberation-war", "解放战争时期", "1945—1949", "全国主要战场与解放区", "人民解放与新中国筹建"),
    ("socialist-construction", "社会主义革命和建设时期", "1949—1978", "全国", "制度建设、工业化与艰辛探索"),
    ("reform-opening", "改革开放和社会主义现代化建设新时期", "1978—2012", "全国", "改革开放与现代化建设"),
    ("new-era", "中国特色社会主义新时代", "2012年至今", "全国", "新时代发展与中国式现代化"),
]

OVERVIEW_INFO = [
    ("timeline", "中国共产党历史学习时间轴", "1919年至今", "全国", "时间、事件、人物、地点对应"),
    ("party-history", "红色党史学习", "分期学习", "全国党史学习专题", "阶段、会议、事件与来源"),
    ("red-events", "红色事件", "重大历史节点", "全国党史学习专题", "时间、地点、人物与过程"),
    ("red-spirit", "中国共产党人精神谱系", "不同历史时期", "全国红色文化拓展", "形成背景、实践主体与当代价值"),
    ("red-expansion", "红色文化拓展馆", "跨区域专题", "全国、山东、青岛与高校实践", "边界清晰、来源可追溯"),
    ("video-hub", "红色影像馆", "图文动态微课", "数字学习空间", "画面、字幕、专题与来源对应"),
]


def safe_name(value: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return stem or "party-media"


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, text_font, fill, line_gap=12):
    x, y = xy
    line = ""
    for char in text:
        candidate = line + char
        if draw.textbbox((0, 0), candidate, font=text_font)[2] > width and line:
            draw.text((x, y), line, font=text_font, fill=fill)
            y += text_font.size + line_gap
            line = char
        else:
            line = candidate
    if line:
        draw.text((x, y), line, font=text_font, fill=fill)
        y += text_font.size + line_gap
    return y


def create_infographic(item: dict) -> Path:
    target = ASSET_DIR / f"info-{safe_name(item['slug'])}.jpg"
    canvas = Image.new("RGB", (1600, 1000), "#f4ead4")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1600, 150), fill="#65151a")
    draw.rectangle((0, 150, 28, 1000), fill="#c59a43")
    draw.ellipse((1260, 650, 1700, 1090), outline="#c7aa72", width=4)
    draw.ellipse((1320, 710, 1640, 1030), outline="#d9c59d", width=3)
    draw.text((72, 44), "党史学习专题 · 项目自制信息图", font=font(34, True), fill="#f8e8b4")
    y = draw_wrapped(draw, item["title"], (74, 215), 1320, font(72, True), "#4f1116", 16)
    y += 32
    draw.rounded_rectangle((74, y, 1450, y + 105), radius=18, fill="#fffaf0", outline="#d6bd8b", width=3)
    draw.text((108, y + 25), f"时间：{item['event_time']}    地点：{item['location']}", font=font(28), fill="#51463d")
    y += 155
    y = draw_wrapped(draw, item["summary"], (82, y), 1260, font(31), "#39322c", 17)
    y += 36
    draw.text((82, y), f"关键词：{item['spirit']}", font=font(28, True), fill="#8c2025")
    draw.text((82, 925), "性质：项目自制图解，不是历史现场照片。正文史实以页面所列权威公开来源为准。", font=font(23), fill="#74675c")
    canvas.save(target, quality=88, optimize=True)
    return target


def create_stage_infographics() -> None:
    for slug, title, period, location, focus in STAGE_INFO:
        create_infographic({
            "slug": f"stage-{slug}", "title": title, "event_time": period,
            "location": location, "summary": f"本图概括{title}的时间范围、主要空间和学习线索，关键词为：{focus}。",
            "spirit": focus,
        })
    for slug, title, period, location, focus in OVERVIEW_INFO:
        create_infographic({
            "slug": f"overview-{slug}", "title": title, "event_time": period,
            "location": location, "summary": f"本图作为{title}栏目导览，强调{focus}，不替代任何具体事件的历史照片。",
            "spirit": focus,
        })


def create_figure_card(name: str, years: str, identity: str) -> Path:
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    target = ASSET_DIR / f"figure-profile-{digest}.jpg"
    canvas = Image.new("RGB", (1000, 1250), "#eee1c8")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1000, 190), fill="#5c1117")
    draw.rectangle((0, 190, 22, 1250), fill="#c59a43")
    draw.text((62, 62), "人物档案 · 项目自制图解", font=font(36, True), fill="#f5dda2")
    draw.text((70, 270), name, font=font(92, True), fill="#561218")
    draw.text((74, 405), years, font=font(38), fill="#9a6c27")
    draw.line((74, 485, 900, 485), fill="#c8ac77", width=4)
    draw_wrapped(draw, identity, (74, 545), 820, font(35), "#37312c", 18)
    draw.rounded_rectangle((74, 880, 900, 1080), radius=20, fill="#fff9ec", outline="#ceb681", width=3)
    draw_wrapped(draw, "本图为项目自制人物档案图解，不是本人照片、雕塑或艺术肖像。人物生卒年份和身份说明以页面所列公开资料为准。", (108, 920), 750, font(25), "#5c5147", 14)
    canvas.save(target, quality=89, optimize=True)
    return target


def commons_info(filename: str) -> dict:
    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1600,
        "titles": f"File:{filename}",
    })
    request = urllib.request.Request(f"{COMMONS_API}?{params}", headers={"User-Agent": "MaogongshanCulturePlatform/1.0 (educational project)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    page = next(iter(payload["query"]["pages"].values()))
    info = page["imageinfo"][0]
    metadata = info.get("extmetadata", {})
    clean = lambda key: re.sub(r"<[^>]+>", "", html.unescape(metadata.get(key, {}).get("value", ""))).strip()
    return {
        "download_url": info.get("thumburl") or info["url"],
        "source_url": info.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(filename)}",
        "artist": clean("Artist"),
        "license": clean("LicenseShortName") or clean("UsageTerms"),
        "date": clean("DateTimeOriginal") or clean("DateTime"),
    }


def download_curated() -> dict[str, dict]:
    downloaded = {}
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for slug, item in CURATED_COMMONS_MEDIA.items():
        try:
            info = commons_info(item["filename"])
            suffix = Path(urllib.parse.urlparse(info["download_url"]).path).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
                suffix = ".jpg"
            target = ASSET_DIR / f"{safe_name(slug)}{suffix}"
            request = urllib.request.Request(info["download_url"], headers={"User-Agent": "MaogongshanCulturePlatform/1.0 (educational project)"})
            with urllib.request.urlopen(request, timeout=60) as response:
                target.write_bytes(response.read())
            downloaded[slug] = {**item, **info, "local_path": f"{PUBLIC_PREFIX}/{target.name}"}
        except Exception as exc:
            print(f"[warn] {slug} 真实照片下载失败，将保留项目自制信息图：{exc}")
    return downloaded


def existing_curated() -> dict[str, dict]:
    existing = {}
    for slug, item in CURATED_COMMONS_MEDIA.items():
        matches = [path for path in ASSET_DIR.glob(f"{safe_name(slug)}.*") if not path.name.startswith("info-")]
        if not matches:
            continue
        source_url = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(item['filename'])}"
        existing[slug] = {
            **item,
            "local_path": f"{PUBLIC_PREFIX}/{matches[0].name}",
            "source_url": source_url,
            "artist": "文件页所列作者",
            "license": "以 Wikimedia Commons 文件页标注为准",
        }
    return existing


def sync_figures(conn: sqlite3.Connection, allow_download: bool) -> int:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(historical_figures)").fetchall()}
    additions = {
        "photo_note": "TEXT DEFAULT ''",
        "photo_type": "TEXT DEFAULT '人物照片'",
        "source_url": "TEXT DEFAULT ''",
        "copyright_note": "TEXT DEFAULT ''",
    }
    for name, definition in additions.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE historical_figures ADD COLUMN {name} {definition}")

    # 清理旧脚本误写入人物表的案例卡和团队岗位；团队资料由 team_members 表维护。
    verified_names = tuple(FIGURE_PROFILES.keys())
    placeholders = ",".join("?" for _ in verified_names)
    conn.execute(f"DELETE FROM historical_figures WHERE name NOT IN ({placeholders})", verified_names)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    curated_by_name = {item["name"]: (slug, item) for slug, item in CURATED_FIGURES.items()}
    for name, profile in FIGURE_PROFILES.items():
        active_period, identity, deeds, related_events = profile
        metadata = {}
        curated = curated_by_name.get(name)
        if curated:
            slug, item = curated
            target = ASSET_DIR / f"figure-{safe_name(slug)}.jpg"
            if allow_download:
                try:
                    metadata = commons_info(item["filename"])
                    source_bytes = b""
                    last_error = None
                    for attempt in range(3):
                        try:
                            request = urllib.request.Request(metadata["download_url"], headers={"User-Agent": "MaogongshanCulturePlatform/1.0 (educational project)"})
                            with urllib.request.urlopen(request, timeout=90) as response:
                                source_bytes = response.read()
                            break
                        except Exception as exc:
                            last_error = exc
                            time.sleep(1.5 * (attempt + 1))
                    if not source_bytes:
                        raise RuntimeError(f"连续下载失败：{last_error}")
                    with Image.open(io.BytesIO(source_bytes)) as source_image:
                        portrait = ImageOps.exif_transpose(source_image).convert("RGB")
                        portrait.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
                        portrait.save(target, format="JPEG", quality=88, optimize=True, progressive=True)
                except Exception as exc:
                    print(f"[warn] {name}人物照片下载失败：{exc}")
            if not target.exists():
                target = create_figure_card(name, active_period, identity)
                photo_type = "项目自制人物档案"
                photo_note = f"{name}人物档案项目自制图解，不是人物照片。"
                source_url = "https://www.12371.cn/"
                copyright_note = "项目自制图解，可用于本项目学习展示。"
            else:
                photo_type = item["photo_type"]
                photo_note = item["photo_note"]
                source_url = metadata.get("source_url") or f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(item['filename'])}"
                copyright_note = f"照片许可：{metadata.get('license') or '以 Wikimedia Commons 文件页标注为准'}。"
        else:
            target = create_figure_card(name, active_period, identity)
            photo_type = "项目自制人物档案"
            photo_note = f"{name}人物档案项目自制图解，不是本人照片、雕塑或影视形象。"
            source_url = "https://www.12371.cn/"
            copyright_note = "项目自制图解，可用于本项目学习展示；不得标注为人物历史照片。"
        photo_url = f"{PUBLIC_PREFIX}/{target.name}"
        source = "共产党员网公开党史与英模资料索引、权威公开资料整理"
        values = (
            photo_url, active_period, f"{name}，{active_period}，{identity}。本档案用于全国党史学习与英模精神拓展。", deeds,
            "全国党史学习拓展人物，与毛公山地方历史不建立未经资料证明的直接关系。",
            related_events, source, 1, "人物基础信息与媒体性质已核对",
            photo_note, photo_type, source_url, copyright_note,
        )
        existing = conn.execute("SELECT id FROM historical_figures WHERE name=? ORDER BY id LIMIT 1", (name,)).fetchone()
        if existing:
            conn.execute("""
                UPDATE historical_figures SET photo_url=?,active_period=?,biography=?,deeds=?,relation_to_maogongshan=?,
                    related_events=?,source=?,verified=?,verification_status=?,photo_note=?,photo_type=?,source_url=?,copyright_note=?
                WHERE id=?
            """, (*values, existing[0]))
        else:
            conn.execute("""
                INSERT INTO historical_figures(name,photo_url,active_period,biography,deeds,relation_to_maogongshan,
                    related_events,source,verified,verification_status,photo_note,photo_type,source_url,copyright_note,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (name, *values, now))
        count += 1
    return count


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS learning_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_key TEXT UNIQUE NOT NULL,
            article_id INTEGER NOT NULL,
            article_slug TEXT NOT NULL,
            section_id TEXT NOT NULL,
            event_id TEXT,
            person_ids TEXT,
            title TEXT NOT NULL,
            image_url TEXT NOT NULL,
            location TEXT,
            year TEXT,
            media_type TEXT NOT NULL,
            caption TEXT NOT NULL,
            alt TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_url TEXT,
            copyright_note TEXT NOT NULL,
            is_historical_photo INTEGER DEFAULT 0,
            verification_status TEXT NOT NULL,
            fallback_image TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(article_id) REFERENCES learning_articles(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_learning_media_article ON learning_media(article_id, section_id, sort_order);
    """)


def upsert_media(conn: sqlite3.Connection, values: tuple) -> None:
    conn.execute("""
        INSERT INTO learning_media(
            media_key,article_id,article_slug,section_id,event_id,person_ids,title,image_url,location,year,
            media_type,caption,alt,source_name,source_url,copyright_note,is_historical_photo,
            verification_status,fallback_image,sort_order,created_at,updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(media_key) DO UPDATE SET
            article_id=excluded.article_id, article_slug=excluded.article_slug, section_id=excluded.section_id,
            event_id=excluded.event_id, person_ids=excluded.person_ids, title=excluded.title,
            image_url=excluded.image_url, location=excluded.location, year=excluded.year,
            media_type=excluded.media_type, caption=excluded.caption, alt=excluded.alt,
            source_name=excluded.source_name, source_url=excluded.source_url,
            copyright_note=excluded.copyright_note, is_historical_photo=excluded.is_historical_photo,
            verification_status=excluded.verification_status, fallback_image=excluded.fallback_image,
            sort_order=excluded.sort_order, updated_at=excluded.updated_at
    """, values)


def sync(conn: sqlite3.Connection, allow_download: bool = True) -> dict:
    ensure_table(conn)
    downloaded = download_curated() if allow_download else existing_curated()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_stage_infographics()
    count = 0
    for item in ARTICLES:
        article = conn.execute("SELECT id FROM learning_articles WHERE slug=?", (item["slug"],)).fetchone()
        if not article:
            continue
        info_path = create_infographic(item)
        info_public = f"{PUBLIC_PREFIX}/{info_path.name}"
        caption = f"《{item['title']}》项目自制信息图，概括时间、地点和主题关键词；用于辅助理解，不是历史现场照片。"
        upsert_media(conn, (
            f"{item['slug']}:overview", article[0], item["slug"], "内容导语", item["slug"], item["related_people"],
            f"{item['title']}专题信息图", info_public, item["location"], item["event_time"], "项目自制", caption,
            caption, "山软寻脉实践团队", "/project", "项目自制图解，可用于本项目学习展示；不得标注为历史照片。",
            0, "项目自制内容已核对", info_public, 0, now, now,
        ))
        cover = info_public
        cover_note = caption
        curated = downloaded.get(item["slug"])
        if curated:
            source_name = f"Wikimedia Commons · {curated.get('artist') or '文件上传者'}"
            copyright_note = f"许可：{curated.get('license') or '以来源页标注为准'}；本地副本用于教学展示，署名与许可信息见来源页。"
            upsert_media(conn, (
                f"{item['slug']}:curated", article[0], item["slug"], curated["section_id"], item["slug"], item["related_people"],
                curated["title"], curated["local_path"], curated["location"], curated["year"], curated["media_type"],
                curated["caption"], curated["caption"], source_name, curated["source_url"], copyright_note, 0,
                "主题、地点与许可已核对", info_public, 10, now, now,
            ))
            cover = curated["local_path"]
            cover_note = curated["caption"]
            count += 1
        conn.execute("UPDATE learning_articles SET image=?, image_note=?, updated_at=? WHERE id=?", (cover, cover_note, now, article[0]))
    figures = sync_figures(conn, allow_download)
    export_manifest(conn)
    return {"articles": len(ARTICLES), "curated_downloads": count, "verified_figures": figures}


def export_manifest(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    articles = [dict(row) for row in conn.execute(
        "SELECT id,slug,title,event_time,location,related_people,image,image_note,source_name,source_url FROM learning_articles ORDER BY id"
    ).fetchall()]
    media = [dict(row) for row in conn.execute(
        "SELECT media_key,article_id,article_slug,section_id,event_id,person_ids,title,image_url,location,year,media_type,caption,alt,source_name,source_url,copyright_note,is_historical_photo,verification_status,fallback_image FROM learning_media ORDER BY article_id,sort_order,id"
    ).fetchall()]
    figures = [dict(row) for row in conn.execute(
        "SELECT id,name,photo_url,active_period,related_events,source,verification_status,photo_note,photo_type,source_url,copyright_note FROM historical_figures ORDER BY id"
    ).fetchall()]
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps({"articles": articles, "media": media, "figures": figures}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as connection:
        if "--local" in sys.argv:
            result = sync(connection, allow_download=False)
        elif "--figures-only" in sys.argv:
            result = {"verified_figures": sync_figures(connection, allow_download=True)}
            export_manifest(connection)
        else:
            result = sync(connection, allow_download=True)
    print(json.dumps(result, ensure_ascii=False))
