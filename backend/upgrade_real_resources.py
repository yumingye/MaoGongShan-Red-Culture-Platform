from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "maogongshan.db"

RETRIEVED_AT = "2026-07-17"

IMG = {
    "mountain": "/assets/images/scenery/maogongshan-mountain.jpg",
    "plaque": "/assets/images/activity/maogongshan-3a-plaque.jpg",
    "qingfeng": "/assets/images/culture/qingfeng-community.jpg",
    "baifuan": "/assets/images/culture/baifuan.jpg",
    "grape": "/assets/images/activity/xifu-grape-harvest.jpg",
    "autumn": "/assets/images/scenery/xifu-autumn.jpg",
    "sunset": "/assets/images/scenery/maogongshan-sunset-rock.png",
    "red_park": "/assets/images/culture/maogongshan-red-park-2022.jpg",
    "park_route": "/assets/images/route/maogongshan-park-route-2022.jpg",
    "eco_farm": "/assets/images/scenery/maogongshan-eco-farm.jpg",
    "xifu_beauty": "/assets/images/scenery/xifu-beauty.jpg",
    "culture_tour": "/assets/images/culture/xifu-cultural-tourism.jpg",
}

QINGDAO_NEWS_PAGE = "https://news.qingdaonews.com/wap/2018-09/05/content_20207648.htm"
QINGDAO_RENEWAL_PAGE = "https://news.qingdaonews.com/wap/2022-05/13/content_23204186.htm"
DZWW_4A_PAGE = "https://qingdao.dzwww.com/xinwen/jiaoqu/202412/t20241225_15325574.htm"
QINGDAO_HIKING_2026_PAGE = "https://news.qingdaonews.com/wap/2026-04/09/content_23651172.htm"
SPORT_SOURCE = "https://www.sport.gov.cn/n14471/n14480/n14519/c866865/content.html"
WIKI_SOURCE = "https://zh.wikipedia.org/zh-cn/%E6%AF%9B%E5%85%AC%E5%B1%B1"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_real_tables(conn: sqlite3.Connection) -> None:
    """建立面向正式展示的资源表，保留旧表用于兼容已有接口。"""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS scenery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            summary TEXT,
            content TEXT,
            location TEXT,
            category TEXT,
            image_url TEXT,
            source_name TEXT,
            source_url TEXT,
            copyright_note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            period TEXT,
            location TEXT,
            summary TEXT,
            content TEXT,
            category TEXT,
            image_url TEXT,
            source_name TEXT,
            source_url TEXT,
            verification_status TEXT DEFAULT '公开资料',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS figures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            period TEXT,
            summary TEXT,
            contribution TEXT,
            image_url TEXT,
            source_name TEXT,
            source_url TEXT,
            verification_status TEXT DEFAULT '公开资料',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS digital_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            resource_type TEXT,
            summary TEXT,
            source_name TEXT,
            source_url TEXT,
            tags TEXT,
            copyright_note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            summary TEXT,
            start_point TEXT,
            end_point TEXT,
            route_type TEXT,
            source_name TEXT,
            source_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            image_url TEXT NOT NULL,
            source_name TEXT,
            source_url TEXT,
            description TEXT,
            captured_at TEXT,
            location TEXT,
            category TEXT,
            copyright_note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )


def upsert(conn: sqlite3.Connection, table: str, key: str, data: dict[str, str]) -> None:
    columns = list(data.keys())
    exists = conn.execute(f"SELECT 1 FROM {table} WHERE {key} = ?", (data[key],)).fetchone()
    if exists:
        assignments = ", ".join(f"{col}=?" for col in columns if col != key)
        values = [data[col] for col in columns if col != key]
        conn.execute(f"UPDATE {table} SET {assignments} WHERE {key}=?", [*values, data[key]])
    else:
        placeholders = ", ".join("?" for _ in columns)
        conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", [data[col] for col in columns])


def replace_public_data(conn: sqlite3.Connection) -> None:
    """用可追溯公开资料替换前台演示数据和占位图片。"""
    now = now_text()
    copyright_note = "来源页面公开发布，已记录出处；用于课程展示和社会实践项目展示，商业传播前请联系来源单位确认授权。"
    source_qd = "青岛新闻网"
    source_dz = "大众网·海报新闻"
    source_sport = "国家体育总局群众体育司转载资料"
    source_wiki = "维基百科毛公山条目"

    images = [
        ("毛公山山体实景", IMG["mountain"], source_qd, QINGDAO_NEWS_PAGE, "青岛新闻网毛公山 3A 景区挂牌报道配图，展现毛公山山体和自然风貌。", "2018-09-05", "青岛市城阳区惜福镇街道", "毛公山全景"),
        ("毛公山国家3A级景区挂牌活动", IMG["plaque"], source_qd, QINGDAO_NEWS_PAGE, "2018 年毛公山景区获评国家 3A 级旅游景区相关公开报道配图。", "2018-09-05", "青岛市城阳区毛公山景区", "历史活动"),
        ("青峰社区景观", IMG["qingfeng"], source_qd, QINGDAO_NEWS_PAGE, "惜福镇青峰社区相关景观图片，可作为毛公山周边环境资料。", "2018-09-05", "青岛市城阳区惜福镇街道青峰社区", "周边环境"),
        ("百福庵周边景观", IMG["baifuan"], source_qd, QINGDAO_NEWS_PAGE, "毛公山所在惜福镇街道周边文化与旅游环境公开报道配图。", "2018-09-05", "青岛市城阳区惜福镇街道", "周边文化"),
        ("惜福镇葡萄采摘活动", IMG["grape"], source_qd, QINGDAO_NEWS_PAGE, "惜福镇乡村旅游和周边活动公开报道配图。", "2018-09-05", "青岛市城阳区惜福镇街道", "周边活动"),
        ("惜福镇秋日风景", IMG["autumn"], source_qd, QINGDAO_NEWS_PAGE, "惜福镇秋日自然环境公开报道配图，可用于毛公山周边风光展示。", "2018-09-05", "青岛市城阳区惜福镇街道", "四季风光"),
        ("毛公山夕照岩石景观", IMG["sunset"], source_dz, DZWW_4A_PAGE, "大众网报道配图，展示毛公山夕照、山体岩石和自然景观。", "2024-12-25", "青岛市城阳区惜福镇街道毛公山景区", "自然风光"),
        ("毛公山红色文旅景观", IMG["red_park"], source_qd, QINGDAO_RENEWAL_PAGE, "青岛新闻网城市更新报道配图，展示毛公山红色文旅提质升级相关景观。", "2022-05-13", "青岛市城阳区惜福镇街道毛公山景区", "红色文化"),
        ("毛公山景区游览路线景观", IMG["park_route"], source_qd, QINGDAO_RENEWAL_PAGE, "青岛新闻网城市更新报道配图，展示毛公山景区路线与环境提升。", "2022-05-13", "青岛市城阳区惜福镇街道毛公山景区", "登山道路"),
        ("惜福镇生态农场景观", IMG["eco_farm"], source_qd, QINGDAO_NEWS_PAGE, "青岛新闻网公开报道配图，展示惜福镇周边生态与乡村文旅环境。", "2018-09-05", "青岛市城阳区惜福镇街道", "周边自然景观"),
        ("惜福镇自然风貌", IMG["xifu_beauty"], source_qd, QINGDAO_NEWS_PAGE, "青岛新闻网公开报道配图，展示惜福镇自然与文旅环境。", "2018-09-05", "青岛市城阳区惜福镇街道", "周边自然景观"),
        ("惜福镇文化旅游活动", IMG["culture_tour"], source_qd, QINGDAO_NEWS_PAGE, "青岛新闻网公开报道配图，展示惜福镇文化旅游活动与周边环境。", "2018-09-05", "青岛市城阳区惜福镇街道", "实践记录"),
    ]
    for item in images:
        upsert(
            conn,
            "images",
            "title",
            {
                "title": item[0],
                "image_url": item[1],
                "source_name": item[2],
                "source_url": item[3],
                "description": item[4],
                "captured_at": item[5],
                "location": item[6],
                "category": item[7],
                "copyright_note": copyright_note,
                "created_at": now,
                "updated_at": now,
            },
        )
        upsert(
            conn,
            "image_metadata",
            "title",
            {
                "title": item[0],
                "local_path": item[1],
                "original_url": item[1],
                "source_name": item[2],
                "source_page_url": item[3],
                "photographer": "来源页面未署名",
                "license": "公开报道配图，商用需授权",
                "copyright_note": copyright_note,
                "captured_at": item[5],
                "retrieved_at": RETRIEVED_AT,
                "category": item[7],
                "description": item[4],
                "created_at": now,
                "updated_at": now,
            },
        )

    scenery_rows = [
        ("毛公山山体景观", "毛公山位于青岛市城阳区惜福镇街道青峰社区，是当地山地景观和红色文化展示的重要点位。", "公开资料显示，毛公山所在区域依托山体景观、乡村环境和登山活动形成旅游与研学资源。", "青岛市城阳区惜福镇街道青峰社区", "山体景观", IMG["mountain"], source_wiki, WIKI_SOURCE),
        ("青峰社区周边环境", "青峰社区是公开资料中毛公山所在社区，适合展示毛公山周边乡村与社区环境。", "社区环境、旅游服务和登山步道资料可共同构成毛公山数字导览内容。", "青岛市城阳区惜福镇街道青峰社区", "周边环境", IMG["qingfeng"], source_qd, QINGDAO_NEWS_PAGE),
        ("惜福镇文旅环境", "惜福镇街道拥有毛公山、百福庵、乡村采摘等多类文旅资源。", "公开报道将毛公山 3A 景区挂牌与惜福镇全域旅游、乡村旅游发展放在同一文旅背景下介绍。", "青岛市城阳区惜福镇街道", "周边文化", IMG["baifuan"], source_qd, QINGDAO_NEWS_PAGE),
        ("惜福镇秋日风光", "秋季山地与乡村景色适合作为毛公山周边自然风貌展示。", "图片来自公开报道页面，项目中用于表现毛公山周边自然环境。", "青岛市城阳区惜福镇街道", "四季风光", IMG["autumn"], source_qd, QINGDAO_NEWS_PAGE),
        ("毛公山夕照自然景观", "大众网报道图片展示毛公山夕照与山体岩石景观。", "该图片适合作为毛公山自然景观、日落光影和山体特色展示资源。", "青岛市城阳区惜福镇街道毛公山景区", "自然风光", IMG["sunset"], source_dz, DZWW_4A_PAGE),
        ("毛公山红色文旅景观", "青岛新闻网报道毛公山红色文旅项目提质升级。", "公开报道提到毛公山景区完成红色文旅项目提升，成为惜福镇文旅资源的重要组成部分。", "青岛市城阳区惜福镇街道毛公山景区", "红色文化", IMG["red_park"], source_qd, QINGDAO_RENEWAL_PAGE),
        ("毛公山登山游览路线", "毛公山景区兼具登山健身、文旅导览和红色文化展示功能。", "结合国家登山健身步道资料和公开报道，可作为路线导览、AI导游和地图点位资料。", "青岛市城阳区惜福镇街道毛公山景区", "登山道路", IMG["park_route"], source_qd, QINGDAO_RENEWAL_PAGE),
    ]
    for name, summary, content, location, category, image_url, source_name, source_url in scenery_rows:
        upsert(conn, "scenery", "name", {"name": name, "summary": summary, "content": content, "location": location, "category": category, "image_url": image_url, "source_name": source_name, "source_url": source_url, "copyright_note": copyright_note, "created_at": now, "updated_at": now})

    history_rows = [
        ("毛公山景区获评国家3A级旅游景区", "2018年9月", "青岛市城阳区惜福镇街道毛公山景区", "青岛新闻网报道，毛公山景区 2018 年获评国家 3A 级旅游景区。", "该报道将毛公山景区挂牌与惜福镇街道旅游资源、社区环境和乡村旅游发展相联系，适合作为景区发展类公开资料收录。", "景区发展", IMG["plaque"], source_qd, QINGDAO_NEWS_PAGE, "公开报道"),
        ("毛公山国家登山健身步道相关资料", "公开资料收录时间：2018年", "青岛市城阳区惜福镇街道青峰社区", "国家体育总局群众体育司转载资料介绍青岛市城阳区毛公山国家登山健身步道。", "资料显示该步道位于城阳区惜福镇街道青峰社区，属于全民健身和户外活动资源。项目中将其作为路线与导览资料收录。", "登山路线", IMG["mountain"], source_sport, SPORT_SOURCE, "公开转载资料"),
        ("毛公山所在地与名称条目", "公开百科资料", "青岛市城阳区惜福镇街道青峰社区", "公开百科条目介绍毛公山位于山东省青岛市城阳区惜福镇街道青峰社区。", "百科资料可作为位置索引线索，正式参赛或发表前建议继续核对政府、景区或地方志来源。", "基础介绍", IMG["mountain"], source_wiki, WIKI_SOURCE, "公开百科资料"),
        ("毛公山红色文旅项目提质升级", "2022年5月", "青岛市城阳区惜福镇街道毛公山景区", "青岛新闻网报道，惜福镇街道推进毛公山红色文旅项目提质升级。", "公开报道提到毛公山景区完成红色文旅项目提质升级，并介绍道路更新、停车场、智慧化景区、旅游配套等内容；该资料适合作为景区更新和红色文旅建设资料。", "红色文化", IMG["red_park"], source_qd, QINGDAO_RENEWAL_PAGE, "公开报道"),
        ("毛公山景区晋升国家4A级旅游景区", "2024年12月", "青岛市城阳区惜福镇街道毛公山景区", "大众网报道，毛公山景区晋升国家4A级旅游景区。", "公开报道介绍毛公山景区自然景观与文化资源，并指出其成为国家4A级旅游景区；该条目可用于景区等级发展时间轴。", "景区发展", IMG["sunset"], source_dz, DZWW_4A_PAGE, "公开报道"),
        ("毛公山登山节与游览交通信息", "2026年4月", "青岛市城阳区惜福镇街道毛公山景区", "青岛新闻网报道 2026 青岛毛公山登山节，并给出公交、自驾等出行提示。", "报道介绍市民可乘坐 111 路、106 路、109 路至宫家村车站，或自驾导航至毛公山景区，为路线推荐和AI导游提供公开资料依据。", "实践活动", IMG["park_route"], source_qd, QINGDAO_HIKING_2026_PAGE, "公开报道"),
    ]
    for row in history_rows:
        upsert(
            conn,
            "history",
            "title",
            {
                "title": row[0],
                "period": row[1],
                "location": row[2],
                "summary": row[3],
                "content": row[4],
                "category": row[5],
                "image_url": row[6],
                "source_name": row[7],
                "source_url": row[8],
                "verification_status": row[9],
                "created_at": now,
                "updated_at": now,
            },
        )

    # 清理旧演示事件，写入真实公开资料。
    conn.execute("DELETE FROM historical_events WHERE title LIKE '%示例%' OR title LIKE '%示意%' OR source LIKE '%演示%' OR image_url LIKE '%.svg%'")
    for row in history_rows:
        upsert(
            conn,
            "historical_events",
            "title",
            {
                "title": row[0],
                "event_time": row[1],
                "location": row[2],
                "related_people": "公开报道未涉及具体历史人物",
                "summary": row[3],
                "details": row[4],
                "source": f"{row[7]}：{row[8]}",
                "reference_materials": row[8],
                "image_url": row[6],
                "category": row[5],
                "verified": 1,
                "verification_status": row[9],
                "created_at": now,
            },
        )

    conn.execute("DELETE FROM scenic_images WHERE name LIKE '%示例%' OR name LIKE '%示意%' OR description LIKE '%模拟%' OR description LIKE '%占位%' OR image_url LIKE '%.svg%'")
    for item in images:
        upsert(
            conn,
            "scenic_images",
            "name",
            {
                "name": item[0],
                "category": item[7],
                "description": item[4],
                "location": item[6],
                "shot_time": item[5],
                "source": f"{item[2]}：{item[3]}",
                "image_url": item[1],
                "recommendation_index": 5,
                "created_at": now,
            },
        )

    conn.execute("DELETE FROM resources WHERE name LIKE '%示例%' OR name LIKE '%占位%' OR summary LIKE '%演示%'")
    digital_rows = [
        ("青岛新闻网：毛公山3A景区挂牌报道", "新闻报道", "报道毛公山景区获评国家3A级旅游景区，并配有多张毛公山及惜福镇相关图片。", source_qd, QINGDAO_NEWS_PAGE, "毛公山,3A景区,公开报道"),
        ("青岛新闻网：毛公山红色文旅项目提质升级", "新闻报道", "报道惜福镇街道推进毛公山红色文旅项目提质升级、道路更新、停车配套和智慧化景区建设。", source_qd, QINGDAO_RENEWAL_PAGE, "红色文旅,城市更新,智慧景区"),
        ("大众网：毛公山晋升国家4A级旅游景区", "新闻报道", "报道毛公山景区晋升国家4A级旅游景区，并配有毛公山自然景观图片。", source_dz, DZWW_4A_PAGE, "4A景区,自然风光,景区发展"),
        ("青岛新闻网：2026青岛毛公山登山节", "实践活动", "报道2026青岛毛公山登山节，并给出公交、自驾等游览交通信息。", source_qd, QINGDAO_HIKING_2026_PAGE, "登山节,实践活动,出行提示"),
        ("国家体育总局：毛公山国家登山健身步道资料", "景区资料", "资料介绍青岛市城阳区毛公山国家登山健身步道，可用于路线导览和体育旅游信息。", source_sport, SPORT_SOURCE, "登山步道,全民健身,路线"),
        ("维基百科：毛公山条目", "基础资料", "提供毛公山位置、行政区划等基础索引信息，正式引用前建议与官方资料交叉核对。", source_wiki, WIKI_SOURCE, "位置,百科,基础资料"),
    ]
    for title, rtype, summary, source_name, source_url, tags in digital_rows:
        upsert(conn, "digital_resources", "title", {"title": title, "resource_type": rtype, "summary": summary, "source_name": source_name, "source_url": source_url, "tags": tags, "copyright_note": copyright_note, "created_at": now, "updated_at": now})
        upsert(conn, "resources", "name", {"name": title, "type": rtype, "summary": summary, "uploaded_at": now, "source": f"{source_name}：{source_url}", "file_url": source_url, "tags": tags, "views": 0})

    conn.execute("DELETE FROM scenic_spots WHERE name LIKE '%示例%' OR name LIKE '%示意%' OR description LIKE '%演示%' OR image_url LIKE '%.svg%'")
    spots = [
        ("毛公山景区", "核心景区", "毛公山位于青岛市城阳区惜福镇街道青峰社区，是项目重点展示的山地与红色文化资源点。", 36.281, 120.501, "青岛市城阳区惜福镇街道青峰社区", IMG["mountain"], source_wiki, "公开资料"),
        ("毛公山国家登山健身步道", "登山路线", "公开资料介绍的国家登山健身步道，适合在地图导览中展示登山路线和户外活动信息。", 36.281, 120.501, "青岛市城阳区惜福镇街道青峰社区", IMG["mountain"], source_sport, "公开转载资料"),
        ("青峰社区", "周边社区", "毛公山所在社区及周边环境，是理解景区服务、社区文旅和实践调研的重要点位。", 36.279, 120.500, "青岛市城阳区惜福镇街道青峰社区", IMG["qingfeng"], source_qd, "公开报道"),
        ("百福庵周边", "周边文化资源", "惜福镇街道周边文旅资源之一，可与毛公山形成区域文化导览。", 36.276, 120.493, "青岛市城阳区惜福镇街道", IMG["baifuan"], source_qd, "公开报道"),
        ("毛公山红色文旅景观区", "红色文化资源点", "青岛新闻网报道中的红色文旅提质升级项目，可作为红色文化导览核心点位。", 36.281, 120.501, "青岛市城阳区惜福镇街道毛公山景区", IMG["red_park"], source_qd, "公开报道"),
        ("毛公山游览步道", "登山路线", "结合登山健身步道资料和登山节报道整理的游览路线点位。", 36.282, 120.503, "青岛市城阳区惜福镇街道毛公山景区", IMG["park_route"], source_qd, "公开报道"),
    ]
    for name, category, desc, lat, lon, address, image_url, source, status in spots:
        upsert(
            conn,
            "scenic_spots",
            "name",
            {
                "name": name,
                "type": category,
                "description": desc,
                "latitude": lat,
                "longitude": lon,
                "route_hint": "建议以高德地图实时导航结果为准。",
                "image_url": image_url,
                "source": source,
                "verification_status": status,
                "address": address,
                "category": category,
            },
        )

    route_rows = [
        ("毛公山国家登山健身步道", "依托国家体育总局转载资料整理，展示毛公山登山健身步道信息。", "青峰社区周边", "毛公山山体及观景区域", "登山健身", source_sport, SPORT_SOURCE),
        ("惜福镇毛公山周边文旅路线", "结合公开报道中的毛公山、青峰社区、百福庵和乡村活动资源形成周边游览线索。", "毛公山景区", "惜福镇周边文旅点位", "文旅参观", source_qd, QINGDAO_NEWS_PAGE),
        ("毛公山红色文旅研学路线", "围绕毛公山红色文旅景观、登山路线、景区服务配套和项目调研资源组织研学路线。", "毛公山景区入口", "红色文旅景观区与观景点", "红色研学", source_qd, QINGDAO_RENEWAL_PAGE),
        ("毛公山登山节推荐路线", "依据2026青岛毛公山登山节公开报道整理，适合作为AI导游游览建议。", "景区入口或公交到达点", "毛公山登山步道与观景区域", "活动路线", source_qd, QINGDAO_HIKING_2026_PAGE),
    ]
    for name, summary, start, end, route_type, source_name, source_url in route_rows:
        upsert(conn, "routes", "name", {"name": name, "summary": summary, "start_point": start, "end_point": end, "route_type": route_type, "source_name": source_name, "source_url": source_url, "created_at": now, "updated_at": now})

    # 人物模块不再虚构红色人物，改为公开团队与资料角色；前台显示为“人物与团队”。
    conn.execute("DELETE FROM historical_figures WHERE name LIKE '%示例%' OR photo_url LIKE '%.svg%'")
    upsert(
        conn,
        "historical_figures",
        "name",
        {
            "name": "山软寻脉·毛公山数字调研实践团",
            "photo_url": IMG["plaque"],
            "active_period": "2026年社会实践项目",
            "biography": "山东大学软件学院社会实践团队，围绕毛公山红色文化数字化保护与传播开展资源整理、调研和平台建设。",
            "deeds": "建设毛公山红色文化数字资源库，整理公开资料、图片元数据、路线和项目调研成果。",
            "relation_to_maogongshan": "项目以毛公山及其周边红色文化、自然风景和数字传播为实践对象。",
            "related_events": "毛公山红色文化数字资源库建设",
            "source": "项目申报材料公开展示字段",
            "verified": 1,
            "verification_status": "项目材料",
            "created_at": now,
        },
    )
    upsert(
        conn,
        "figures",
        "name",
        {
            "name": "山软寻脉·毛公山数字调研实践团",
            "period": "2026年社会实践项目",
            "summary": "山东大学软件学院社会实践团队，负责资源库建设、资料整理和数字化展示。",
            "contribution": "围绕毛公山公开资料与实地调研成果建设数字资源库。",
            "image_url": IMG["plaque"],
            "source_name": "项目申报材料公开字段",
            "source_url": "",
            "verification_status": "项目材料",
            "created_at": now,
            "updated_at": now,
        },
    )

    sources = [
        ("青岛新闻网毛公山3A景区挂牌报道", source_qd, QINGDAO_NEWS_PAGE, "新闻报道", "毛公山景区挂牌国家 3A 级旅游景区公开报道及配图。", copyright_note, "公开报道"),
        ("青岛新闻网毛公山红色文旅提质升级报道", source_qd, QINGDAO_RENEWAL_PAGE, "新闻报道", "介绍毛公山红色文旅项目提质升级、道路与停车设施、智慧化景区等内容。", copyright_note, "公开报道"),
        ("大众网毛公山4A景区报道", source_dz, DZWW_4A_PAGE, "新闻报道", "报道毛公山景区晋升国家4A级旅游景区，并配有自然景观图片。", copyright_note, "公开报道"),
        ("青岛新闻网2026毛公山登山节报道", source_qd, QINGDAO_HIKING_2026_PAGE, "新闻报道", "报道2026青岛毛公山登山节，包含公交、自驾等游览交通提示。", copyright_note, "公开报道"),
        ("国家体育总局毛公山国家登山健身步道资料", source_sport, SPORT_SOURCE, "转载资料", "青岛市城阳区毛公山国家登山健身步道资料。", copyright_note, "公开转载资料"),
        ("维基百科毛公山条目", source_wiki, WIKI_SOURCE, "百科资料", "毛公山基础位置与条目索引。", "CC BY-SA 条款下的百科内容，引用时需遵循对应许可。", "公开百科资料"),
    ]
    for title, source_name, source_url, source_type, summary, note, status in sources:
        upsert(conn, "source_records", "title", {"title": title, "source_name": source_name, "source_url": source_url, "source_type": source_type, "summary": summary, "retrieved_at": RETRIEVED_AT, "copyright_note": note, "verification_status": status, "created_at": now, "updated_at": now})

    rebuild_knowledge(conn)


def rebuild_knowledge(conn: sqlite3.Connection) -> None:
    now = now_text()
    conn.execute("DELETE FROM knowledge_documents WHERE title LIKE '%示例%' OR title LIKE '%待补充%'")
    for row in conn.execute("SELECT title, period, location, summary, content, category, source_name, source_url, verification_status FROM history").fetchall():
        upsert(conn, "knowledge_documents", "title", {"title": row["title"], "summary": row["summary"], "content": f"{row['period']}，{row['location']}。{row['content']}", "category": row["category"], "source_name": row["source_name"], "source_url": row["source_url"], "source_document": "联网公开资料", "source_page": "", "verification_status": row["verification_status"], "created_at": now, "updated_at": now})
    for row in conn.execute("SELECT name, summary, content, category, source_name, source_url FROM scenery").fetchall():
        upsert(conn, "knowledge_documents", "title", {"title": row["name"], "summary": row["summary"], "content": row["content"], "category": row["category"], "source_name": row["source_name"], "source_url": row["source_url"], "source_document": "联网公开资料", "source_page": "", "verification_status": "公开资料", "created_at": now, "updated_at": now})
    for row in conn.execute("SELECT title, resource_type, summary, source_name, source_url FROM digital_resources").fetchall():
        upsert(conn, "knowledge_documents", "title", {"title": row["title"], "summary": row["summary"], "content": row["summary"], "category": row["resource_type"], "source_name": row["source_name"], "source_url": row["source_url"], "source_document": "联网公开资料", "source_page": "", "verification_status": "公开资料", "created_at": now, "updated_at": now})
    for row in conn.execute("SELECT title, description, category, source_name, source_url, location FROM images").fetchall():
        upsert(conn, "knowledge_documents", "title", {"title": f"图片资源：{row['title']}", "summary": row["description"], "content": f"{row['title']}。分类：{row['category']}。地点：{row['location']}。{row['description']}", "category": "图片资源", "source_name": row["source_name"], "source_url": row["source_url"], "source_document": "联网公开图片资料", "source_page": "", "verification_status": "公开资料", "created_at": now, "updated_at": now})
    for row in conn.execute("SELECT name, summary, start_point, end_point, route_type, source_name, source_url FROM routes").fetchall():
        upsert(conn, "knowledge_documents", "title", {"title": f"游览路线：{row['name']}", "summary": row["summary"], "content": f"{row['name']}。路线类型：{row['route_type']}。起点：{row['start_point']}。终点：{row['end_point']}。{row['summary']}", "category": "游览路线", "source_name": row["source_name"], "source_url": row["source_url"], "source_document": "联网公开资料", "source_page": "", "verification_status": "公开资料", "created_at": now, "updated_at": now})


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"数据库不存在：{DB_PATH}")
    with connect() as conn:
        create_real_tables(conn)
        replace_public_data(conn)
        conn.commit()
    print("真实资源升级完成")


if __name__ == "__main__":
    main()
