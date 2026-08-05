"""备份平台 SQLite 数据库。"""

from __future__ import annotations

import shutil
from datetime import datetime

try:
    from .config import DB_PATH
except ImportError:
    from config import DB_PATH


def backup_database() -> str | None:
    """独立备份数据库，不加载 FastAPI 应用。"""
    if not DB_PATH.exists():
        return None
    backup_dir = DB_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"{DB_PATH.stem}-{datetime.now():%Y%m%d-%H%M%S}.backup.db"
    shutil.copy2(DB_PATH, target)
    return str(target)


if __name__ == "__main__":
    target = backup_database()
    print(f"数据库备份完成：{target}" if target else "数据库尚不存在，无需备份。")
