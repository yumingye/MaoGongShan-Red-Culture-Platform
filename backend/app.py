from __future__ import annotations

import hashlib
import logging
import secrets
import shutil
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from .config import (
        ADMIN_PASSWORD,
        ADMIN_TOKEN,
        ADMIN_USERNAME,
        BACKEND_HOST,
        BACKEND_PORT,
        BASE_DIR,
        CORS_ORIGIN_REGEX,
        CORS_ORIGINS,
        DATA_DIR,
        DB_PATH,
        IMAGE_DIR,
        READ_ONLY_MODE,
        SEED_DB_PATH,
        SERVICE_NAME,
    )
except ImportError:
    from config import (
        ADMIN_PASSWORD,
        ADMIN_TOKEN,
        ADMIN_USERNAME,
        BACKEND_HOST,
        BACKEND_PORT,
        BASE_DIR,
        CORS_ORIGIN_REGEX,
        CORS_ORIGINS,
        DATA_DIR,
        DB_PATH,
        IMAGE_DIR,
        READ_ONLY_MODE,
        SEED_DB_PATH,
        SERVICE_NAME,
    )

try:
    from .sync_public_team_members import sync_team_members
except ImportError:
    from sync_public_team_members import sync_team_members

try:
    from .sync_practice_writings import sync_practice_writings
except ImportError:
    from sync_practice_writings import sync_practice_writings

try:
    from .sync_enriched_content import sync_enriched_content
except ImportError:
    from sync_enriched_content import sync_enriched_content

try:
    from .platform_copy import OVERVIEW_SECTIONS, QA_ITEMS, SCHOOL_SECTIONS
except ImportError:
    from platform_copy import OVERVIEW_SECTIONS, QA_ITEMS, SCHOOL_SECTIONS

REAL_HERO_IMAGE = "/assets/images/scenery/maogongshan-mountain.jpg"
REAL_CULTURE_IMAGE = "/assets/images/activity/maogongshan-3a-plaque.jpg"

DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("maogongshan.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """准备运行数据库；失败时保留进程，由健康检查报告降级状态。"""
    try:
        if DB_PATH != SEED_DB_PATH and not DB_PATH.exists() and SEED_DB_PATH.exists():
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SEED_DB_PATH, DB_PATH)
        init_db()
        sync_team_members()
        sync_practice_writings()
        sync_enriched_content()
        with get_conn() as conn:
            rebuild_knowledge_documents(conn)
    except Exception:
        logger.exception("数据库初始化失败，服务将以降级状态启动")
    yield


app = FastAPI(
    title="青岛市城阳区毛公山红色文化数字资源库 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def get_conn() -> sqlite3.Connection:
    """创建 SQLite 连接，并启用按字段名读取结果。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return None if row is None else {key: row[key] for key in row.keys()}


def rows_to_list(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows if row is not None]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """公网只读实例不接受写入；本地管理仍需管理员令牌。"""
    if READ_ONLY_MODE:
        raise HTTPException(status_code=403, detail="公网展示实例为只读模式，管理操作已关闭")
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="管理员令牌尚未配置")
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="请先登录管理员账号")


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LoginIn(BaseModel):
    username: str
    password: str


class EventIn(BaseModel):
    title: str
    event_time: str = ""
    location: str = ""
    related_people: str = ""
    summary: str = ""
    details: str = ""
    source: str = "公开资料来源"
    reference_materials: str = "请补充地方志、档案馆资料、景区资料或公开报道链接。"
    image_url: str = REAL_CULTURE_IMAGE
    category: str = "历史事件"
    verified: int = 1
    verification_status: str = "公开资料"


class FigureIn(BaseModel):
    name: str
    photo_url: str = REAL_CULTURE_IMAGE
    active_period: str = "公开资料所示时期"
    biography: str = ""
    deeds: str = ""
    relation_to_maogongshan: str = ""
    related_events: str = ""
    source: str = "公开资料来源"
    verified: int = 1
    verification_status: str = "公开资料"


class ResourceIn(BaseModel):
    name: str
    type: str
    summary: str = ""
    source: str = "公开资料来源"
    file_url: str = ""
    tags: str = ""


class ScenicImageIn(BaseModel):
    name: str
    category: str
    description: str = ""
    location: str = "青岛市城阳区惜福镇街道毛公山周边"
    shot_time: str = ""
    source: str = "公开资料来源"
    image_url: str = REAL_HERO_IMAGE
    recommendation_index: int = 4


class ChatIn(BaseModel):
    question: str


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    """兼容旧数据库：缺少字段时只追加字段，不清空现有数据。"""
    names = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in names:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def insert_if_missing(conn: sqlite3.Connection, table: str, key: str, value: str, sql: str, params: tuple[Any, ...]) -> None:
    exists = conn.execute(f"SELECT 1 FROM {table} WHERE {key} = ? LIMIT 1", (value,)).fetchone()
    if not exists:
        conn.execute(sql, params)


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS historical_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_time TEXT,
            location TEXT,
            related_people TEXT,
            summary TEXT,
            details TEXT,
            source TEXT,
            image_url TEXT,
            category TEXT,
            verified INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS historical_figures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo_url TEXT,
            biography TEXT,
            deeds TEXT,
            relation_to_maogongshan TEXT,
            related_events TEXT,
            source TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            summary TEXT,
            uploaded_at TEXT NOT NULL,
            source TEXT,
            file_url TEXT,
            tags TEXT,
            views INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS resource_tags (
            resource_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (resource_id, tag_id),
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS scenic_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            location TEXT,
            shot_time TEXT,
            source TEXT,
            image_url TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scenic_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            route_hint TEXT
        );

        CREATE TABLE IF NOT EXISTS visit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            visited_at TEXT NOT NULL,
            user_agent TEXT
        );

        CREATE TABLE IF NOT EXISTS project_information (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            value TEXT,
            category TEXT,
            source_title TEXT,
            source_type TEXT,
            source_page TEXT,
            source_note TEXT,
            verification_status TEXT DEFAULT '团队公开展示文稿',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS practice_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            summary TEXT,
            step_order INTEGER DEFAULT 0,
            status TEXT DEFAULT '计划中',
            source_title TEXT,
            source_type TEXT,
            source_page TEXT,
            source_note TEXT,
            verification_status TEXT DEFAULT '团队公开展示文稿',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS expected_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            summary TEXT,
            status TEXT DEFAULT '建设中',
            source_title TEXT,
            source_type TEXT,
            source_page TEXT,
            source_note TEXT,
            verification_status TEXT DEFAULT '团队公开展示文稿',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            college TEXT,
            role TEXT,
            responsibility TEXT,
            public_bio TEXT,
            source_title TEXT,
            source_type TEXT,
            source_page TEXT,
            source_note TEXT,
            verification_status TEXT DEFAULT '团队公开展示文稿',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS source_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            source_name TEXT,
            source_url TEXT,
            source_type TEXT,
            summary TEXT,
            retrieved_at TEXT,
            copyright_note TEXT,
            verification_status TEXT DEFAULT '待考证',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            summary TEXT,
            content TEXT,
            category TEXT,
            source_name TEXT,
            source_url TEXT,
            source_document TEXT,
            source_page TEXT,
            verification_status TEXT DEFAULT '待考证',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            mode TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS narrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT,
            target_title TEXT UNIQUE,
            script TEXT,
            voice_style TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS image_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            local_path TEXT,
            original_url TEXT,
            source_name TEXT,
            source_page_url TEXT,
            photographer TEXT,
            license TEXT,
            copyright_note TEXT,
            captured_at TEXT,
            retrieved_at TEXT,
            category TEXT,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS learning_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            sub_category TEXT,
            scope TEXT DEFAULT '党史学习专题',
            event_time TEXT,
            location TEXT,
            related_people TEXT,
            spirit TEXT,
            youth_insight TEXT,
            tags TEXT,
            image TEXT,
            image_note TEXT,
            source_name TEXT NOT NULL,
            source_url TEXT,
            verification_status TEXT DEFAULT '权威公开资料整理',
            featured INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

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

        CREATE INDEX IF NOT EXISTS idx_learning_media_article
        ON learning_media(article_id, section_id, sort_order);
        """
    )
    ensure_column(conn, "historical_events", "reference_materials", "TEXT DEFAULT 'source-recorded'")
    ensure_column(conn, "historical_events", "verification_status", "TEXT DEFAULT 'source_recorded'")
    ensure_column(conn, "historical_figures", "active_period", "TEXT DEFAULT 'public-profile'")
    ensure_column(conn, "historical_figures", "verified", "INTEGER DEFAULT 0")
    ensure_column(conn, "historical_figures", "verification_status", "TEXT DEFAULT 'source_recorded'")
    ensure_column(conn, "historical_figures", "photo_note", "TEXT DEFAULT ''")
    ensure_column(conn, "historical_figures", "photo_type", "TEXT DEFAULT '人物照片'")
    ensure_column(conn, "historical_figures", "source_url", "TEXT DEFAULT ''")
    ensure_column(conn, "historical_figures", "copyright_note", "TEXT DEFAULT ''")
    ensure_column(conn, "scenic_images", "recommendation_index", "INTEGER DEFAULT 4")
    ensure_column(conn, "scenic_spots", "image_url", "TEXT DEFAULT '/assets/images/scenery/maogongshan-mountain.jpg'")
    ensure_column(conn, "scenic_spots", "source", "TEXT DEFAULT 'public-resource-library'")
    ensure_column(conn, "scenic_spots", "verification_status", "TEXT DEFAULT 'source_recorded'")
    ensure_column(conn, "scenic_spots", "address", "TEXT DEFAULT 'Chengyang Qingdao Maogongshan Area'")
    ensure_column(conn, "scenic_spots", "category", "TEXT DEFAULT 'spot'")


def seed_data(conn: sqlite3.Connection) -> None:
    """兼容旧入口：正式展示数据由 finalize_platform_content.py 和 enrich_competition_data.py 维护。"""
    now = now_text()
    password_hash = hash_password(ADMIN_PASSWORD)
    insert_if_missing(
        conn,
        "users",
        "username",
        ADMIN_USERNAME,
        "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
        (ADMIN_USERNAME, password_hash, now),
    )
    conn.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (password_hash, ADMIN_USERNAME),
    )
    rebuild_knowledge_documents(conn)

def upsert_knowledge(conn: sqlite3.Connection, title: str, summary: str, content: str, category: str, source_name: str, source_url: str = "", source_document: str = "", source_page: str = "", verification_status: str = "待考证") -> None:
    now = now_text()
    exists = conn.execute("SELECT id FROM knowledge_documents WHERE title = ?", (title,)).fetchone()
    if exists:
        conn.execute(
            """
            UPDATE knowledge_documents SET summary=?, content=?, category=?, source_name=?, source_url=?,
            source_document=?, source_page=?, verification_status=?, updated_at=? WHERE id=?
            """,
            (summary, content, category, source_name, source_url, source_document, source_page, verification_status, now, exists["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO knowledge_documents(title, summary, content, category, source_name, source_url, source_document, source_page, verification_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, summary, content, category, source_name, source_url, source_document, source_page, verification_status, now, now),
        )


def rebuild_knowledge_documents(conn: sqlite3.Connection) -> None:
    """将资源库公开内容同步成问答知识库。"""
    for row in conn.execute("SELECT * FROM project_information").fetchall():
        upsert_knowledge(conn, f"项目介绍：{row['title']}", row["value"] or "", f"{row['title']}：{row['value']}", "项目介绍", row["source_title"] or "项目资料", "", row["source_title"] or "", row["source_page"] or "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM practice_plans").fetchall():
        upsert_knowledge(conn, f"实践计划：{row['title']}", row["summary"] or "", f"{row['title']}：{row['summary']}。状态：{row['status']}", "实践计划", row["source_title"] or "项目资料", "", row["source_title"] or "", row["source_page"] or "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM expected_results").fetchall():
        upsert_knowledge(conn, f"预期成果：{row['title']}", row["summary"] or "", f"{row['title']}：{row['summary']}。状态：{row['status']}", "项目成果", row["source_title"] or "项目资料", "", row["source_title"] or "", row["source_page"] or "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM historical_events").fetchall():
        upsert_knowledge(conn, f"历史资料：{row['title']}", row["summary"] or "", f"{row['title']}。时间：{row['event_time']}。地点：{row['location']}。{row['summary']} {row['details']}", "历史资料", row["source"] or "资源库", "", row["reference_materials"] or "", "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM historical_figures").fetchall():
        upsert_knowledge(conn, f"人物资料：{row['name']}", row["biography"] or "", f"{row['name']}。活动时期：{row['active_period']}。{row['biography']} {row['deeds']} {row['relation_to_maogongshan']}", "人物资料", row["source"] or "资源库", "", "", "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM scenic_spots").fetchall():
        upsert_knowledge(conn, f"景点导览：{row['name']}", row["description"] or "", f"{row['name']}。类型：{row['type']}。地址：{row['address']}。{row['description']} 路线提示：{row['route_hint']}", "景点导览", row["source"] or "资源库", "", "", "", row["verification_status"] or "待考证")
    for row in conn.execute("SELECT * FROM resources").fetchall():
        upsert_knowledge(conn, f"数字资源：{row['name']}", row["summary"] or "", f"{row['name']}。类型：{row['type']}。{row['summary']} 标签：{row['tags']}", "数字资源", row["source"] or "资源库", row["file_url"] or "", "", "", "待考证")
    for row in conn.execute("SELECT * FROM learning_articles").fetchall():
        upsert_knowledge(
            conn,
            f"党史学习：{row['title']}",
            row["summary"] or "",
            f"{row['title']}。时间：{row['event_time']}。地点：{row['location']}。{row['content']} 青年启示：{row['youth_insight']}",
            row["category"] or "党史学习",
            row["source_name"] or "权威公开资料",
            row["source_url"] or "",
            "",
            "",
            row["verification_status"] or "权威公开资料整理",
        )
    for row in conn.execute("SELECT * FROM qa_knowledge").fetchall():
        upsert_knowledge(
            conn,
            f"常见问答：{row['question']}",
            row["answer"] or "",
            f"问题：{row['question']} 回答：{row['answer']} 关键词：{row['keywords']}",
            row["category"] or "常见问答",
            row["source"] or "平台问答知识库",
            "",
            "",
            "",
            "平台公开问答",
        )


def init_db() -> None:
    with get_conn() as conn:
        create_tables(conn)
        seed_data(conn)
        try:
            from backend.upgrade_real_resources import create_real_tables, replace_public_data
        except ModuleNotFoundError:
            from upgrade_real_resources import create_real_tables, replace_public_data

        # 每次启动都在基础初始化后执行真实资源升级，避免旧演示数据重新进入前台。
        create_real_tables(conn)
        replace_public_data(conn)
        try:
            from backend.import_photo_materials import sync_manifest_records
        except ModuleNotFoundError:
            from import_photo_materials import sync_manifest_records
        # 从打包清单恢复项目实拍照片；数据库重建后无需保留原始素材目录。
        sync_manifest_records(conn)
        try:
            from backend.enrich_competition_data import seed_narrations
        except ModuleNotFoundError:
            from enrich_competition_data import seed_narrations
        seed_narrations(conn)
        try:
            from backend.augment_red_learning import seed_learning_articles
        except ModuleNotFoundError:
            from augment_red_learning import seed_learning_articles
        seed_learning_articles(conn)
        try:
            from backend.sync_party_media import sync as sync_party_media
        except ModuleNotFoundError:
            from sync_party_media import sync as sync_party_media
        # 启动时只同步本地信息图和已有媒体关系；联网下载由独立命令显式执行。
        sync_party_media(conn, allow_download=False)
        rebuild_knowledge_documents(conn)


def build_event_filters(keyword: str, title: str, event_time: str, location: str, person: str, category: str, verification_status: str) -> tuple[str, list[str]]:
    clauses: list[str] = []
    values: list[str] = []
    if keyword:
        clauses.append("(title LIKE ? OR event_time LIKE ? OR location LIKE ? OR related_people LIKE ? OR summary LIKE ? OR details LIKE ? OR category LIKE ?)")
        values.extend([f"%{keyword}%"] * 7)
    filters = {
        "title": title,
        "event_time": event_time,
        "location": location,
        "related_people": person,
        "category": category,
        "verification_status": verification_status,
    }
    for field, value in filters.items():
        if value:
            clauses.append(f"{field} LIKE ?")
            values.append(f"%{value}%")
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", values


@app.middleware("http")
async def record_visit(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api") and not READ_ONLY_MODE:
        try:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO visit_records(path, visited_at, user_agent) VALUES (?, ?, ?)",
                    (request.url.path, now_text(), request.headers.get("user-agent", "")),
                )
        except sqlite3.Error:
            # 访问统计属于辅助功能，数据库短暂锁定时不能影响实际 API 响应。
            pass
    return response


@app.exception_handler(Exception)
async def handle_unexpected_error(request, error):
    """记录完整异常，但只向公开页面返回简洁、可处理的信息。"""
    logger.exception("Unhandled API error on %s", request.url.path, exc_info=error)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务暂时无法完成该请求，请稍后重试。"},
    )


@app.get("/api/health", tags=["system"])
def health():
    """健康检查不因数据库暂时不可用而使 Web 进程退出。"""
    result = {
        "status": "ok",
        "service": SERVICE_NAME,
        "database": "unavailable",
        "read_only": READ_ONLY_MODE,
    }
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1").fetchone()
            result["database"] = "connected"
            result["learning_articles"] = conn.execute(
                "SELECT COUNT(*) FROM learning_articles"
            ).fetchone()[0]
    except sqlite3.Error as error:
        result["database_error"] = error.__class__.__name__
    return result


@app.post("/api/auth/login")
def login(payload: LoginIn):
    if READ_ONLY_MODE:
        raise HTTPException(status_code=403, detail="公网展示实例未开放后台登录")
    if not ADMIN_PASSWORD or not ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="管理员账号尚未完成安全配置")
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (payload.username,)).fetchone()
    if not user or user["password_hash"] != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"token": ADMIN_TOKEN, "username": payload.username}


@app.get("/api/stats")
def stats():
    with get_conn() as conn:
        return {
            "events": conn.execute("SELECT COUNT(*) FROM historical_events").fetchone()[0],
            "figures": conn.execute("SELECT COUNT(*) FROM historical_figures").fetchone()[0],
            "documents": conn.execute("SELECT COUNT(*) FROM resources WHERE type IN ('历史文献','研究文章','新闻报道','口述历史')").fetchone()[0],
            "images": conn.execute("SELECT COUNT(*) FROM images").fetchone()[0],
            "videos": conn.execute("SELECT COUNT(*) FROM resources WHERE type = '视频资料'").fetchone()[0],
            "spots": conn.execute("SELECT COUNT(*) FROM scenic_spots").fetchone()[0],
            "stories": conn.execute("SELECT COUNT(*) FROM red_stories").fetchone()[0],
            "places": conn.execute("SELECT COUNT(*) FROM places").fetchone()[0],
            "learning": conn.execute("SELECT COUNT(*) FROM learning_articles").fetchone()[0],
            "knowledge": conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0],
            "visits": conn.execute("SELECT COUNT(*) FROM visit_records").fetchone()[0],
            "resources": conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0],
        }


@app.get("/api/home")
def home():
    with get_conn() as conn:
        events = rows_to_list(conn.execute("SELECT * FROM historical_events ORDER BY id DESC LIMIT 6").fetchall())
        figures = rows_to_list(conn.execute("SELECT * FROM historical_figures ORDER BY id DESC LIMIT 4").fetchall())
        images = rows_to_list(conn.execute(
            """
            SELECT id, title AS name, category, description, location, captured_at AS shot_time,
                   source_name AS source, image_url
            FROM images ORDER BY id DESC LIMIT 8
            """
        ).fetchall())
        timeline = rows_to_list(conn.execute("SELECT id, title, event_time, summary FROM historical_events ORDER BY id LIMIT 6").fetchall())
        categories = rows_to_list(conn.execute("SELECT * FROM categories ORDER BY id").fetchall())
        learning = rows_to_list(conn.execute(
            "SELECT id,title,summary,event_time,scope,image,category FROM learning_articles WHERE featured = 1 ORDER BY event_time LIMIT 4"
        ).fetchall())
    return {"events": events, "figures": figures, "images": images, "timeline": timeline, "categories": categories, "learning": learning}


@app.get("/api/events")
def list_events(
    keyword: str = "",
    title: str = "",
    event_time: str = "",
    location: str = "",
    person: str = "",
    category: str = "",
    verification_status: str = "",
    page: int = 0,
    page_size: int = 0,
):
    where, values = build_event_filters(keyword, title, event_time, location, person, category, verification_status)
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM historical_events{where}", values).fetchone()[0]
        sql = f"SELECT * FROM historical_events{where} ORDER BY id DESC"
        if page and page_size:
            sql += " LIMIT ? OFFSET ?"
            rows = conn.execute(sql, [*values, page_size, (page - 1) * page_size]).fetchall()
            return {"items": rows_to_list(rows), "total": total, "page": page, "page_size": page_size}
        rows = conn.execute(sql, values).fetchall()
    return rows_to_list(rows)


@app.get("/api/events/{event_id}")
def get_event(event_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM historical_events WHERE id = ?", (event_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id, title, event_time, summary, image_url FROM historical_events WHERE id != ? ORDER BY id DESC LIMIT 3", (event_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="资料不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.post("/api/admin/events", dependencies=[Depends(require_admin)])
def create_event(payload: EventIn):
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO historical_events
            (title, event_time, location, related_people, summary, details, source, reference_materials, image_url, category, verified, verification_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.title, payload.event_time, payload.location, payload.related_people, payload.summary, payload.details, payload.source, payload.reference_materials, payload.image_url, payload.category, payload.verified, payload.verification_status, now_text()),
        )
        return {"id": cur.lastrowid}


@app.put("/api/admin/events/{event_id}", dependencies=[Depends(require_admin)])
def update_event(event_id: int, payload: EventIn):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE historical_events SET title=?, event_time=?, location=?, related_people=?, summary=?, details=?,
            source=?, reference_materials=?, image_url=?, category=?, verified=?, verification_status=? WHERE id=?
            """,
            (payload.title, payload.event_time, payload.location, payload.related_people, payload.summary, payload.details, payload.source, payload.reference_materials, payload.image_url, payload.category, payload.verified, payload.verification_status, event_id),
        )
    return {"ok": True}


@app.delete("/api/admin/events/{event_id}", dependencies=[Depends(require_admin)])
def delete_event(event_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM historical_events WHERE id=?", (event_id,))
    return {"ok": True}


@app.get("/api/figures")
def list_figures(keyword: str = "", page: int = 0, page_size: int = 0):
    where = "WHERE name LIKE ? OR biography LIKE ? OR deeds LIKE ? OR relation_to_maogongshan LIKE ? OR active_period LIKE ?" if keyword else ""
    values = [f"%{keyword}%"] * 5 if keyword else []
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM historical_figures {where}", values).fetchone()[0]
        sql = f"SELECT * FROM historical_figures {where} ORDER BY id DESC"
        if page and page_size:
            rows = conn.execute(sql + " LIMIT ? OFFSET ?", [*values, page_size, (page - 1) * page_size]).fetchall()
            return {"items": rows_to_list(rows), "total": total, "page": page, "page_size": page_size}
        rows = conn.execute(sql, values).fetchall()
    return rows_to_list(rows)


@app.get("/api/figures/{figure_id}")
def get_figure(figure_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM historical_figures WHERE id=?", (figure_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id, title, event_time, summary FROM historical_events ORDER BY id DESC LIMIT 4").fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="人物不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.post("/api/admin/figures", dependencies=[Depends(require_admin)])
def create_figure(payload: FigureIn):
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO historical_figures
            (name, photo_url, active_period, biography, deeds, relation_to_maogongshan, related_events, source, verified, verification_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.name, payload.photo_url, payload.active_period, payload.biography, payload.deeds, payload.relation_to_maogongshan, payload.related_events, payload.source, payload.verified, payload.verification_status, now_text()),
        )
        return {"id": cur.lastrowid}


@app.put("/api/admin/figures/{figure_id}", dependencies=[Depends(require_admin)])
def update_figure(figure_id: int, payload: FigureIn):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE historical_figures SET name=?, photo_url=?, active_period=?, biography=?, deeds=?, relation_to_maogongshan=?,
            related_events=?, source=?, verified=?, verification_status=? WHERE id=?
            """,
            (payload.name, payload.photo_url, payload.active_period, payload.biography, payload.deeds, payload.relation_to_maogongshan, payload.related_events, payload.source, payload.verified, payload.verification_status, figure_id),
        )
    return {"ok": True}


@app.delete("/api/admin/figures/{figure_id}", dependencies=[Depends(require_admin)])
def delete_figure(figure_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM historical_figures WHERE id=?", (figure_id,))
    return {"ok": True}


@app.get("/api/resources")
def list_resources(keyword: str = "", type: str = "", page: int = 0, page_size: int = 0):
    clauses: list[str] = []
    values: list[str] = []
    if keyword:
        clauses.append("(name LIKE ? OR summary LIKE ? OR tags LIKE ? OR source LIKE ?)")
        values.extend([f"%{keyword}%"] * 4)
    if type:
        clauses.append("type = ?")
        values.append(type)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM resources{where}", values).fetchone()[0]
        sql = f"SELECT * FROM resources{where} ORDER BY uploaded_at DESC, id DESC"
        if page and page_size:
            rows = conn.execute(sql + " LIMIT ? OFFSET ?", [*values, page_size, (page - 1) * page_size]).fetchall()
            return {"items": rows_to_list(rows), "total": total, "page": page, "page_size": page_size}
        rows = conn.execute(sql, values).fetchall()
    return rows_to_list(rows)


@app.get("/api/resources/{resource_id}")
def get_resource(resource_id: int):
    with get_conn() as conn:
        if not READ_ONLY_MODE:
            conn.execute("UPDATE resources SET views = views + 1 WHERE id=?", (resource_id,))
        row = conn.execute("SELECT * FROM resources WHERE id=?", (resource_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="资源不存在")
    return row_to_dict(row)


@app.post("/api/admin/resources", dependencies=[Depends(require_admin)])
def create_resource(payload: ResourceIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO resources(name, type, summary, uploaded_at, source, file_url, tags, views) VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
            (payload.name, payload.type, payload.summary, now_text(), payload.source, payload.file_url, payload.tags),
        )
        return {"id": cur.lastrowid}


@app.put("/api/admin/resources/{resource_id}", dependencies=[Depends(require_admin)])
def update_resource(resource_id: int, payload: ResourceIn):
    with get_conn() as conn:
        conn.execute(
            "UPDATE resources SET name=?, type=?, summary=?, source=?, file_url=?, tags=? WHERE id=?",
            (payload.name, payload.type, payload.summary, payload.source, payload.file_url, payload.tags, resource_id),
        )
    return {"ok": True}


@app.delete("/api/admin/resources/{resource_id}", dependencies=[Depends(require_admin)])
def delete_resource(resource_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM resources WHERE id=?", (resource_id,))
    return {"ok": True}


@app.get("/api/scenic-images")
def list_scenic_images(category: str = "", keyword: str = ""):
    clauses: list[str] = []
    values: list[str] = []
    if category:
        clauses.append("category = ?")
        values.append(category)
    if keyword:
        clauses.append("(name LIKE ? OR description LIKE ? OR location LIKE ?)")
        values.extend([f"%{keyword}%"] * 3)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM scenic_images{where} ORDER BY recommendation_index DESC, id DESC", values).fetchall()
    return rows_to_list(rows)


@app.post("/api/admin/scenic-images", dependencies=[Depends(require_admin)])
def create_scenic_image(payload: ScenicImageIn):
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO scenic_images(name, category, description, location, shot_time, source, image_url, recommendation_index, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.name, payload.category, payload.description, payload.location, payload.shot_time, payload.source, payload.image_url, payload.recommendation_index, now_text()),
        )
        return {"id": cur.lastrowid}


@app.put("/api/admin/scenic-images/{image_id}", dependencies=[Depends(require_admin)])
def update_scenic_image(image_id: int, payload: ScenicImageIn):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE scenic_images SET name=?, category=?, description=?, location=?, shot_time=?, source=?, image_url=?, recommendation_index=? WHERE id=?
            """,
            (payload.name, payload.category, payload.description, payload.location, payload.shot_time, payload.source, payload.image_url, payload.recommendation_index, image_id),
        )
    return {"ok": True}


@app.delete("/api/admin/scenic-images/{image_id}", dependencies=[Depends(require_admin)])
def delete_scenic_image(image_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM scenic_images WHERE id=?", (image_id,))
    return {"ok": True}


@app.post("/api/admin/upload", dependencies=[Depends(require_admin)])
def upload_image(file: UploadFile = File(...), category: str = Form(default="uploads")):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        raise HTTPException(status_code=400, detail="仅支持常见图片格式")
    filename = f"{category}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}{suffix}"
    target = IMAGE_DIR / filename
    with target.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/static/images/{filename}"}


@app.get("/api/scenic-spots")
def list_spots():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM scenic_spots ORDER BY id").fetchall())


@app.get("/api/categories")
def list_categories():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM categories ORDER BY id").fetchall())


@app.get("/api/tags")
def list_tags():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM tags ORDER BY id").fetchall())


@app.get("/api/project")
def get_project():
    with get_conn() as conn:
        return {
            "information": rows_to_list(conn.execute("SELECT * FROM project_information ORDER BY id").fetchall()),
            "plans": rows_to_list(conn.execute("SELECT * FROM practice_plans ORDER BY step_order, id").fetchall()),
            "results": rows_to_list(conn.execute("SELECT * FROM expected_results ORDER BY id").fetchall()),
            "team": rows_to_list(conn.execute("SELECT * FROM team_members ORDER BY id").fetchall()),
        }


@app.get("/api/sources")
def list_sources():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM source_records ORDER BY id DESC").fetchall())


@app.get("/api/images/metadata")
def list_image_metadata():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM image_metadata ORDER BY id DESC").fetchall())


@app.get("/api/images")
def list_real_images(category: str = "", keyword: str = ""):
    """图片墙接口：返回已登记来源和版权说明的真实图片资源。"""
    clauses: list[str] = []
    values: list[str] = []
    if category and category != "全部":
        clauses.append("category = ?")
        values.append(category)
    if keyword:
        clauses.append("(title LIKE ? OR description LIKE ? OR location LIKE ? OR source_name LIKE ?)")
        values.extend([f"%{keyword}%"] * 4)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM images{where} ORDER BY id DESC", values).fetchall()
    return rows_to_list(rows)


@app.get("/api/images/slug/{slug}")
def get_real_image_by_slug(slug: str):
    """使用稳定 slug 获取图片详情，数据库重建后链接仍然有效。"""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM images WHERE slug=?", (slug,)).fetchone()
        related = rows_to_list(
            conn.execute(
                "SELECT * FROM images WHERE slug != ? ORDER BY id DESC LIMIT 6",
                (slug,),
            ).fetchall()
        )
    if not row:
        raise HTTPException(status_code=404, detail="图片不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/images/{image_id}")
def get_real_image(image_id: int):
    """图片详情接口：用于展示大图、来源、时间、地点和相关故事。"""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM images WHERE id=?", (image_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT * FROM images WHERE id != ? ORDER BY id DESC LIMIT 6", (image_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="图片不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/routes")
def list_routes():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM routes ORDER BY id").fetchall())


@app.get("/api/narrations")
def list_narrations():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM narrations ORDER BY id").fetchall())


@app.get("/api/research-logs")
def list_research_logs():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM research_logs ORDER BY date DESC, id DESC").fetchall())


@app.get("/api/research-logs/{item_id}")
def get_research_log(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM research_logs WHERE id=?", (item_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id,title,summary,image,date FROM research_logs WHERE id != ? ORDER BY id DESC LIMIT 4", (item_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="调研日志不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/audio-guides")
def list_audio_guides():
    with get_conn() as conn:
        return rows_to_list(conn.execute("SELECT * FROM audio_guides ORDER BY id").fetchall())


@app.get("/api/audio-guides/{item_id}")
def get_audio_guide(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM audio_guides WHERE id=?", (item_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id,title,summary,image FROM audio_guides WHERE id != ? ORDER BY id LIMIT 4", (item_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="音频讲解不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/red-stories")
def list_red_stories(keyword: str = "", category: str = "", page: int = 1, page_size: int = 12):
    where = ["1=1"]
    params: list[Any] = []
    if keyword:
        like = f"%{keyword}%"
        where.append("(title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?)")
        params.extend([like, like, like, like])
    if category:
        where.append("category = ?")
        params.append(category)
    sql_where = " AND ".join(where)
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM red_stories WHERE {sql_where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM red_stories WHERE {sql_where} ORDER BY id DESC LIMIT ? OFFSET ?",
            (*params, page_size, max(page - 1, 0) * page_size),
        ).fetchall()
    return {"items": rows_to_list(rows), "total": total}


@app.get("/api/red-stories/{item_id}")
def get_red_story(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM red_stories WHERE id=?", (item_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id,title,summary,image,date FROM red_stories WHERE id != ? ORDER BY id DESC LIMIT 5", (item_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="红色故事不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/places")
def list_places(keyword: str = "", category: str = "", page: int = 1, page_size: int = 12):
    where = ["1=1"]
    params: list[Any] = []
    if keyword:
        like = f"%{keyword}%"
        where.append("(title LIKE ? OR summary LIKE ? OR content LIKE ? OR location LIKE ? OR tags LIKE ?)")
        params.extend([like, like, like, like, like])
    if category:
        where.append("category = ?")
        params.append(category)
    sql_where = " AND ".join(where)
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM places WHERE {sql_where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM places WHERE {sql_where} ORDER BY id DESC LIMIT ? OFFSET ?",
            (*params, page_size, max(page - 1, 0) * page_size),
        ).fetchall()
    return {"items": rows_to_list(rows), "total": total}


@app.get("/api/places/{item_id}")
def get_place(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM places WHERE id=?", (item_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id,title,summary,image,location FROM places WHERE id != ? ORDER BY id DESC LIMIT 5", (item_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="地点资源不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/achievements")
def list_achievements(keyword: str = "", category: str = "", page: int = 1, page_size: int = 12):
    where = ["1=1"]
    params: list[Any] = []
    if keyword:
        like = f"%{keyword}%"
        where.append("(title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?)")
        params.extend([like, like, like, like])
    if category:
        where.append("category = ?")
        params.append(category)
    sql_where = " AND ".join(where)
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM achievements WHERE {sql_where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM achievements WHERE {sql_where} ORDER BY id DESC LIMIT ? OFFSET ?",
            (*params, page_size, max(page - 1, 0) * page_size),
        ).fetchall()
    return {"items": rows_to_list(rows), "total": total}


@app.get("/api/achievements/{item_id}")
def get_achievement(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM achievements WHERE id=?", (item_id,)).fetchone()
        related = rows_to_list(conn.execute("SELECT id,title,summary,image,date FROM achievements WHERE id != ? ORDER BY id DESC LIMIT 5", (item_id,)).fetchall())
    if not row:
        raise HTTPException(status_code=404, detail="实践成果不存在")
    data = row_to_dict(row)
    data["related"] = related
    return data


@app.get("/api/learning-articles")
def list_learning_articles(
    keyword: str = "",
    category: str = "",
    sub_category: str = "",
    page: int = 1,
    page_size: int = 12,
):
    """党史学习与红色文化拓展资料，和毛公山地方史数据分表管理。"""
    where = ["1=1"]
    params: list[Any] = []
    if keyword:
        like = f"%{keyword}%"
        where.append(
            "(title LIKE ? OR subtitle LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ? OR related_people LIKE ?)"
        )
        params.extend([like] * 6)
    if category:
        where.append("category = ?")
        params.append(category)
    if sub_category:
        where.append("sub_category = ?")
        params.append(sub_category)
    sql_where = " AND ".join(where)
    offset = max(page - 1, 0) * page_size
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM learning_articles WHERE {sql_where}", params).fetchone()[0]
        rows = conn.execute(
            f"""
            SELECT learning_articles.*,
                   COALESCE((SELECT media_type FROM learning_media
                             WHERE article_id=learning_articles.id AND image_url=learning_articles.image
                             ORDER BY sort_order DESC LIMIT 1), '项目自制') AS cover_media_type,
                   COALESCE((SELECT caption FROM learning_media
                             WHERE article_id=learning_articles.id AND image_url=learning_articles.image
                             ORDER BY sort_order DESC LIMIT 1), learning_articles.image_note) AS cover_caption
            FROM learning_articles WHERE {sql_where}
            ORDER BY featured DESC, event_time, id LIMIT ? OFFSET ?
            """,
            (*params, page_size, offset),
        ).fetchall()
        categories = [row["category"] for row in conn.execute("SELECT DISTINCT category FROM learning_articles ORDER BY category").fetchall()]
    return {"items": rows_to_list(rows), "total": total, "categories": categories}


@app.get("/api/learning-articles/{item_id}")
def get_learning_article(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM learning_articles WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="党史学习资料不存在")
        related = conn.execute(
            """
            SELECT id,title,summary,image,event_time,category,scope
            FROM learning_articles
            WHERE id != ? AND (category = ? OR sub_category = ?)
            ORDER BY featured DESC, id DESC LIMIT 6
            """,
            (item_id, row["category"], row["sub_category"]),
        ).fetchall()
        media = conn.execute(
            """
            SELECT id,media_key,article_id,article_slug,section_id,event_id,person_ids,title,image_url,
                   location,year,media_type,caption,alt,source_name,source_url,copyright_note,
                   is_historical_photo,verification_status,fallback_image,sort_order
            FROM learning_media WHERE article_id=? ORDER BY sort_order,id
            """,
            (item_id,),
        ).fetchall()
        conn.execute("UPDATE learning_articles SET views = views + 1 WHERE id = ?", (item_id,))
    data = row_to_dict(row)
    data["related"] = rows_to_list(related)
    data["media"] = rows_to_list(media)
    return data


@app.get("/api/platform-overview")
def platform_overview():
    with get_conn() as conn:
        images = rows_to_list(conn.execute("SELECT * FROM images ORDER BY id DESC LIMIT 10").fetchall())
        routes = rows_to_list(conn.execute("SELECT * FROM routes ORDER BY id").fetchall())
        spots = rows_to_list(conn.execute("SELECT * FROM scenic_spots ORDER BY id").fetchall())
    return {"sections": OVERVIEW_SECTIONS, "images": images, "routes": routes, "spots": spots}


@app.get("/api/guide")
def guide_data():
    """AI讲解页聚合接口。"""
    with get_conn() as conn:
        return {
            "spots": rows_to_list(conn.execute("SELECT * FROM scenic_spots ORDER BY id").fetchall()),
            "routes": rows_to_list(conn.execute("SELECT * FROM routes ORDER BY id").fetchall()),
            "narrations": rows_to_list(conn.execute("SELECT * FROM narrations ORDER BY id").fetchall()),
            "images": rows_to_list(conn.execute("SELECT * FROM images ORDER BY id DESC LIMIT 12").fetchall()),
        }


@app.get("/api/school")
def school_special():
    """山东大学软件学院专题页内容。"""
    return {"title": "软件赋能红色文化传承", "unit": "山东大学软件学院", "sections": SCHOOL_SECTIONS}


@app.post("/api/knowledge/rebuild", dependencies=[Depends(require_admin)])
def rebuild_knowledge():
    with get_conn() as conn:
        rebuild_knowledge_documents(conn)
        total = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
    return {"ok": True, "total": total}


def search_knowledge(conn: sqlite3.Connection, question: str, limit: int = 5) -> list[dict[str, Any]]:
    words = [word for word in question.replace("？", " ").replace("?", " ").replace("，", " ").split() if word]
    domain_terms = [
        "毛公山", "在哪里", "位置", "景色", "风景", "计划", "活动", "实践", "团队", "数字资源库",
        "历史资料", "查询", "来源", "考证", "前往", "路线", "地图", "成果", "短视频",
        "软件学院", "山东大学", "开发", "为什么", "技术路线", "系统架构", "红色故事", "红色文化", "游览",
        "五四运动", "马克思主义", "中国共产党成立", "中共一大", "南昌起义", "秋收起义", "井冈山",
        "古田会议", "红军长征", "长征", "遵义会议", "抗日战争", "延安", "西柏坡", "新中国成立",
        "抗美援朝", "社会主义改造", "改革开放", "新时代", "建党精神", "井冈山精神", "长征精神",
        "延安精神", "西柏坡精神", "雷锋精神", "焦裕禄精神", "两弹一星精神", "沂蒙精神",
        "脱贫攻坚精神", "抗疫精神", "科学家精神", "青年使命", "青岛红色", "山东红色",
        "平台", "功能", "数字展馆", "图片", "视频", "加载失败", "老年人", "安全",
        "编造", "编造历史", "真实性", "核验", "访谈记录", "社会实践成果",
    ]
    words.extend([term for term in domain_terms if term in question])
    if not words:
        words = [question]
    rows = rows_to_list(conn.execute("SELECT * FROM knowledge_documents ORDER BY id DESC").fetchall())
    # 实时开放时间、票价和预约等信息变化快；知识库没有明确字段时不返回相似主题凑答案。
    precision_terms = ["开放时间", "票价", "联系电话", "预约", "实时天气", "公交班次", "月球", "火星"]
    requested_precision_terms = [term for term in precision_terms if term in question]
    if requested_precision_terms:
        corpus = " ".join(f"{row.get('title','')} {row.get('summary','')} {row.get('content','')}" for row in rows)
        if any(term not in corpus for term in requested_precision_terms):
            return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for row in rows:
        text = f"{row.get('title','')} {row.get('summary','')} {row.get('content','')} {row.get('category','')}"
        score = sum(text.count(word) for word in words)
        title = row.get("title", "")
        for term in domain_terms:
            if term in question and term in title:
                score += 40
        if ("计划" in question or "活动" in question or "实践" in question) and row.get("category") == "实践计划":
            score += 8
        if ("团队" in question or "项目" in question or "谁开发" in question) and row.get("category") in ["项目介绍", "实践过程", "技术介绍"]:
            score += 8
        if ("软件学院" in question or "山东大学" in question or "为什么" in question or "技术路线" in question or "系统架构" in question) and ("软件学院" in text or "山东大学" in text or "Vue" in text or "FastAPI" in text):
            score += 14
        if ("哪里" in question or "位置" in question or "前往" in question or "路线" in question) and row.get("category") == "景点导览":
            score += 6
        if ("怎么游览" in question or "游览" in question or "路线" in question or "前往" in question) and row.get("category") in ["游览路线", "游览攻略", "登山路线"]:
            score += 12
        if ("红色故事" in question or "红色文化" in question or "红色" in question) and row.get("category") in ["红色文化", "景区发展", "新闻报道"]:
            score += 12
        if ("资源库" in question or "有哪些内容" in question) and row.get("category") == "数字资源":
            score += 6
        # 中文短问题常没有空格，额外做包含匹配。
        if question and question in text:
            score += 5
        if score:
            scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:limit]]


def school_knowledge_docs() -> list[dict[str, Any]]:
    """把软件学院专题内容作为问答知识来源，不依赖前端页面。"""
    data = school_special()
    docs: list[dict[str, Any]] = []
    for item in data["sections"]:
        docs.append(
            {
                "title": f"山东大学软件学院专题：{item['title']}",
                "summary": item["content"],
                "content": item["content"],
                "category": item["category"],
                "source_name": "山东大学软件学院专题栏目",
                "source_url": "/school",
                "verification_status": "项目内置专题资料",
            }
        )
    return docs



@app.get("/api/chat/suggestions")
def chat_suggestions():
    return [
        "毛公山在哪里？",
        "毛公山有什么景色？",
        "毛公山有哪些红色文化资料？",
        "怎么游览毛公山？",
        "这个平台是谁开发的？",
        "山东大学软件学院做了什么？",
        "实践团队计划开展哪些活动？",
        "数字资源库有哪些内容？",
        "图片资料是否有来源说明？",
        "哪些内容需要继续核验？",
    ]


@app.post("/api/chat")
def chat(payload: ChatIn):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    with get_conn() as conn:
        docs = search_knowledge(conn, question)
        school_terms = ["软件学院", "山东大学", "谁开发", "为什么做", "技术路线", "系统架构", "山软青年"]
        if any(term in question for term in school_terms):
            docs = (school_knowledge_docs() + docs)[:5]
        if not docs:
            answer = "当前资源库中暂未收录足够资料，建议联系项目团队或查阅权威来源。"
            sources: list[dict[str, Any]] = []
        else:
            snippets = []
            needs_review = False
            for doc in docs[:5]:
                status = doc.get("verification_status") or "来源已标注"
                summary = doc.get("summary") or (doc.get("content") or "")[:160]
                snippets.append(f"【{doc.get('category') or '资料'}】{summary}（状态：{status}）")
                if any(word in status for word in ["待考证", "需继续核验", "整理", "二级来源"]):
                    needs_review = True
            answer = "根据当前资源库知识库检索结果：\n" + "\n".join(snippets)
            if needs_review:
                answer += "\n\n提示：以上内容包含公开资料整理或实践团队整理条目，正式引用前请结合页面来源、权威资料或景区管理方说明继续核验。"
            sources = [
                {
                    "title": doc["title"],
                    "source_name": doc["source_name"],
                    "source_url": doc["source_url"],
                    "verification_status": doc["verification_status"],
                }
                for doc in docs
            ]
        if not READ_ONLY_MODE:
            conn.execute("INSERT INTO chat_records(question, answer, mode, created_at) VALUES (?, ?, ?, ?)", (question, answer, "local_retrieval", now_text()))
    return {"answer": answer, "sources": sources, "mode": "local_retrieval"}


@app.get("/api/search")
def search(q: str = Query(default="")):
    keyword = f"%{q}%"
    if not q:
        return {"events": [], "figures": [], "resources": [], "images": [], "spots": [], "learning": []}
    with get_conn() as conn:
        return {
            "events": rows_to_list(conn.execute("SELECT id, title, summary, category, image_url FROM historical_events WHERE title LIKE ? OR summary LIKE ? OR details LIKE ? LIMIT 12", (keyword, keyword, keyword)).fetchall()),
            "figures": rows_to_list(conn.execute("SELECT id, name, biography, deeds, photo_url FROM historical_figures WHERE name LIKE ? OR biography LIKE ? OR deeds LIKE ? LIMIT 12", (keyword, keyword, keyword)).fetchall()),
            "resources": rows_to_list(conn.execute("SELECT id, name, type, summary, file_url FROM resources WHERE name LIKE ? OR summary LIKE ? OR tags LIKE ? LIMIT 12", (keyword, keyword, keyword)).fetchall()),
            "images": rows_to_list(conn.execute("SELECT id, title AS name, category, description, image_url FROM images WHERE title LIKE ? OR description LIKE ? OR category LIKE ? LIMIT 12", (keyword, keyword, keyword)).fetchall()),
            "spots": rows_to_list(conn.execute("SELECT id, name, type, description FROM scenic_spots WHERE name LIKE ? OR description LIKE ? OR type LIKE ? LIMIT 12", (keyword, keyword, keyword)).fetchall()),
            "learning": rows_to_list(conn.execute("SELECT id, title, summary, category, event_time, image, scope FROM learning_articles WHERE title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ? LIMIT 20", (keyword, keyword, keyword, keyword)).fetchall()),
        }


@app.get("/api/search/suggestions")
def search_suggestions(q: str = Query(default="")):
    keyword = f"%{q.strip()}%"
    with get_conn() as conn:
        if not q.strip():
            base = ["毛公山", "红色故事", "山东大学软件学院", "实践调研", "登山路线", "图片来源", "城阳红色文化", "数字地图"]
            return {"items": base}
        rows = []
        rows += [row["title"] for row in conn.execute("SELECT title FROM historical_events WHERE title LIKE ? LIMIT 5", (keyword,)).fetchall()]
        rows += [row["name"] for row in conn.execute("SELECT name FROM historical_figures WHERE name LIKE ? LIMIT 5", (keyword,)).fetchall()]
        rows += [row["name"] for row in conn.execute("SELECT name FROM resources WHERE name LIKE ? LIMIT 5", (keyword,)).fetchall()]
        rows += [row["title"] for row in conn.execute("SELECT title FROM images WHERE title LIKE ? LIMIT 5", (keyword,)).fetchall()]
        rows += [row["title"] for row in conn.execute("SELECT title FROM learning_articles WHERE title LIKE ? OR tags LIKE ? LIMIT 8", (keyword, keyword)).fetchall()]
        return {"items": list(dict.fromkeys(rows))[:12]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
