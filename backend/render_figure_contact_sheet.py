"""生成带姓名的人物照片总览图，供人工目视核对。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

try:
    from .config import DB_PATH, PROJECT_ROOT
except ImportError:
    from config import DB_PATH, PROJECT_ROOT


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT name, photo_url FROM historical_figures ORDER BY id"
    ).fetchall()
    conn.close()

    columns = 6
    tile_width, tile_height = 220, 286
    rows_count = (len(rows) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_width, rows_count * tile_height), "#f3ede2")
    draw = ImageDraw.Draw(sheet)
    label_font = font(24)

    for index, row in enumerate(rows):
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        image_path = PROJECT_ROOT / "frontend" / "public" / str(row["photo_url"]).lstrip("/")
        with Image.open(image_path) as source:
            portrait = ImageOps.fit(
                ImageOps.exif_transpose(source).convert("RGB"),
                (190, 225),
                method=Image.Resampling.LANCZOS,
            )
        sheet.paste(portrait, (x + 15, y + 12))
        draw.text((x + 15, y + 246), row["name"], font=label_font, fill="#4e1116")

    output = PROJECT_ROOT / "docs" / "screenshots" / "figure-portraits-contact-sheet.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=90, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
