"""初始化或安全重建 SQLite 数据库。"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime

try:
    from .app import DB_PATH, init_db
    from .sync_public_team_members import sync_team_members
    from .sync_practice_writings import sync_practice_writings
    from .sync_enriched_content import sync_enriched_content
except ImportError:
    from app import DB_PATH, init_db
    from sync_public_team_members import sync_team_members
    from sync_practice_writings import sync_practice_writings
    from sync_enriched_content import sync_enriched_content


def backup_database() -> str | None:
    """在重建前备份现有数据库，返回备份文件路径。"""
    if not DB_PATH.exists():
        return None
    backup_dir = DB_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"{DB_PATH.stem}-{datetime.now():%Y%m%d-%H%M%S}.backup.db"
    shutil.copy2(DB_PATH, target)
    return str(target)


def main() -> None:
    parser = argparse.ArgumentParser(description="初始化毛公山平台 SQLite 数据库")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="先备份并删除现有数据库，再重新创建完整基础数据",
    )
    args = parser.parse_args()

    if args.reset and DB_PATH.exists():
        backup = backup_database()
        DB_PATH.unlink()
        print(f"已备份原数据库：{backup}")

    init_db()
    sync_team_members()
    sync_practice_writings()
    sync_enriched_content()
    print(f"数据库初始化完成：{DB_PATH}")


if __name__ == "__main__":
    main()
