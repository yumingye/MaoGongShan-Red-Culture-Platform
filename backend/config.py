"""后端集中配置。

所有可变配置均来自环境变量；相对路径统一以项目根目录为基准解析，
确保项目移动到其他电脑后仍可从任意工作目录启动。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")


def project_path(value: str, default: Path) -> Path:
    """把环境变量中的相对路径安全解析到项目根目录。"""
    raw_path = Path(value).expanduser() if value else default
    return raw_path if raw_path.is_absolute() else (PROJECT_ROOT / raw_path).resolve()


BASE_DIR = BACKEND_DIR
DATA_DIR = project_path(os.getenv("DATA_DIR", ""), PROJECT_ROOT / "database")
SEED_DB_PATH = PROJECT_ROOT / "database" / "maogongshan.db"


def database_path(value: str) -> Path:
    """兼容普通文件路径和 sqlite:/// URL。"""
    normalized = value.removeprefix("sqlite:///") if value else ""
    return project_path(normalized, SEED_DB_PATH)


DB_PATH = database_path(os.getenv("DATABASE_URL", ""))
IMAGE_DIR = project_path(
    os.getenv("UPLOAD_DIR", ""),
    BACKEND_DIR / "static" / "images",
)

BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))
SERVICE_NAME = os.getenv("SERVICE_NAME", "maogongshan-api")
READ_ONLY_MODE = os.getenv("READ_ONLY_MODE", "false").lower() in {"1", "true", "yes", "on"}
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "").strip().removeprefix("https://").removeprefix("http://").rstrip("/")
CORS_ORIGIN_REGEX = rf"^https://{re.escape(FRONTEND_HOST)}$" if FRONTEND_HOST else None
