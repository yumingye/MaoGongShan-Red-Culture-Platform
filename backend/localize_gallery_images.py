"""将图库外链图片替换为本地真实图片路径，避免全景图库出现空图。

说明：
- 不删除来源信息，只替换前台展示用 image_url。
- 使用项目中已经存在的本地图片轮换兜底。
- 脚本可重复执行。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


PUBLIC_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PUBLIC_DIR / "database" / "maogongshan.db"
IMAGE_ROOT = PUBLIC_DIR / "assets" / "images"


def local_image_paths() -> list[str]:
    files = []
    for folder in ["maogongshan", "scenery", "culture", "activity", "route", "commons"]:
        base = IMAGE_ROOT / folder
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if file.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                rel = "/" + file.relative_to(PUBLIC_DIR).as_posix()
                files.append(rel)
    if not files:
        raise RuntimeError("未找到可用于图库兜底的本地图片")
    return files


def main() -> None:
    paths = local_image_paths()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, image_url FROM images WHERE image_url LIKE 'http%' ORDER BY id"
        ).fetchall()
        for index, (image_id, _url) in enumerate(rows):
            conn.execute(
                "UPDATE images SET image_url=?, updated_at=datetime('now') WHERE id=?",
                (paths[index % len(paths)], image_id),
            )
        remaining = conn.execute(
            "SELECT COUNT(*) FROM images WHERE image_url LIKE 'http%'"
        ).fetchone()[0]
    print(f"已本地化图库外链：{len(rows)} 条；剩余外链：{remaining}")


if __name__ == "__main__":
    main()
