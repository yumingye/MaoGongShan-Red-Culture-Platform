"""检查红色人物是否全部使用可读取的本人真人照片。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PIL import Image

try:
    from .config import DB_PATH, PROJECT_ROOT
    from .party_media_catalog import FIGURE_PROFILES
except ImportError:
    from config import DB_PATH, PROJECT_ROOT
    from party_media_catalog import FIGURE_PROFILES


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT name, photo_url, photo_type, photo_note, source_url, copyright_note
        FROM historical_figures ORDER BY name
        """
    ).fetchall()
    conn.close()

    problems: list[str] = []
    expected_names = set(FIGURE_PROFILES)
    actual_names = {row["name"] for row in rows}
    if actual_names != expected_names:
        problems.append(f"人物集合不一致：缺少 {sorted(expected_names - actual_names)}")

    for row in rows:
        relative = str(row["photo_url"] or "").lstrip("/")
        image_path = PROJECT_ROOT / "frontend" / "public" / relative
        if row["photo_type"] != "人物照片":
            problems.append(f"{row['name']} 照片类型为 {row['photo_type']}")
        if "figure-profile-" in relative:
            problems.append(f"{row['name']} 仍使用项目自制档案图")
        if not image_path.exists():
            problems.append(f"{row['name']} 图片不存在：{relative}")
            continue
        try:
            with Image.open(image_path) as image:
                image.verify()
        except Exception as exc:
            problems.append(f"{row['name']} 图片无法读取：{exc}")
        if "commons.wikimedia.org/wiki/File:" not in str(row["source_url"] or ""):
            problems.append(f"{row['name']} 缺少 Commons 原始文件页")
        if not str(row["photo_note"] or "").strip():
            problems.append(f"{row['name']} 缺少照片说明")
        if "许可" not in str(row["copyright_note"] or ""):
            problems.append(f"{row['name']} 缺少许可说明")

    if problems:
        raise SystemExit("人物照片检查失败：\n- " + "\n- ".join(problems))
    print(f"人物照片检查通过：{len(rows)} 位人物均使用已核对的本地真人照片。")


if __name__ == "__main__":
    main()
