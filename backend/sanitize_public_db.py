"""清理可公开发布的 SQLite 数据库副本。

该脚本仅应针对打包目录中的数据库副本执行，不会删除文化资源数据。
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PRIVATE_RUNTIME_TABLES = ("chat_records", "visit_records")


def sanitize(database: Path) -> None:
    if not database.exists():
        raise FileNotFoundError(f"数据库不存在：{database}")

    with sqlite3.connect(database) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        for table in PRIVATE_RUNTIME_TABLES:
            if table in tables:
                conn.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.execute("VACUUM")


def main() -> None:
    parser = argparse.ArgumentParser(description="清理 GitHub 发布数据库中的运行记录")
    parser.add_argument("--database", required=True, type=Path)
    args = parser.parse_args()
    sanitize(args.database.resolve())
    print(f"公开数据库已清理：{args.database.resolve()}")


if __name__ == "__main__":
    main()
