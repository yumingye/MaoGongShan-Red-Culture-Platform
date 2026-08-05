"""扫描原始照片并生成可视化联系表。

该脚本只读取原始照片，不会修改、移动或删除任何文件。扫描结果用于后续
人工确认分类、重复照片和图片方向。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def difference_hash(image: Image.Image, size: int = 8) -> str:
    gray = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    bits = []
    for row in range(size):
        offset = row * (size + 1)
        for column in range(size):
            bits.append(pixels[offset + column] > pixels[offset + column + 1])
    value = sum(1 << index for index, enabled in enumerate(bits) if enabled)
    return f"{value:0{size * size // 4}x}"


def hash_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def scan_images(source: Path) -> list[dict]:
    records: list[dict] = []
    paths = sorted(
        path
        for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    for index, path in enumerate(paths, start=1):
        record: dict = {
            "index": index,
            "file": path.name,
            "relative_path": path.relative_to(source).as_posix(),
            "bytes": path.stat().st_size,
            "valid": False,
            "error": "",
        }
        try:
            with Image.open(path) as raw:
                original_size = raw.size
                orientation = raw.getexif().get(274)
                image = ImageOps.exif_transpose(raw).convert("RGB")
                image.load()
                record.update(
                    {
                        "valid": True,
                        "format": raw.format,
                        "original_width": original_size[0],
                        "original_height": original_size[1],
                        "width": image.width,
                        "height": image.height,
                        "orientation": orientation,
                        "sha256": sha256(path),
                        "dhash": difference_hash(image),
                    }
                )
        except Exception as exc:  # noqa: BLE001 - 扫描报告需要保留具体错误
            record["error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)
    return records


def duplicate_report(records: list[dict]) -> tuple[list[list[str]], list[dict]]:
    exact: dict[str, list[str]] = {}
    valid_records = [record for record in records if record["valid"]]
    for record in valid_records:
        exact.setdefault(record["sha256"], []).append(record["file"])
    exact_groups = [files for files in exact.values() if len(files) > 1]

    near_groups: list[dict] = []
    for index, left in enumerate(valid_records):
        for right in valid_records[index + 1 :]:
            if left["sha256"] == right["sha256"]:
                continue
            distance = hash_distance(left["dhash"], right["dhash"])
            if distance <= 5:
                near_groups.append(
                    {
                        "left": left["file"],
                        "right": right["file"],
                        "distance": distance,
                    }
                )
    return exact_groups, near_groups


def create_contact_sheets(
    source: Path, records: list[dict], output: Path, per_sheet: int = 16
) -> list[str]:
    output.mkdir(parents=True, exist_ok=True)
    font = load_font(17)
    small_font = load_font(14)
    columns = 4
    cell_width = 360
    cell_height = 285
    image_width = 334
    image_height = 220
    sheets: list[str] = []
    valid_records = [record for record in records if record["valid"]]
    page_count = math.ceil(len(valid_records) / per_sheet)

    for page in range(page_count):
        rows = math.ceil(per_sheet / columns)
        canvas = Image.new(
            "RGB", (columns * cell_width, rows * cell_height), "#ece8df"
        )
        draw = ImageDraw.Draw(canvas)
        subset = valid_records[page * per_sheet : (page + 1) * per_sheet]
        for position, record in enumerate(subset):
            row, column = divmod(position, columns)
            left = column * cell_width
            top = row * cell_height
            draw.rounded_rectangle(
                (left + 7, top + 7, left + cell_width - 7, top + cell_height - 7),
                radius=10,
                fill="#ffffff",
                outline="#c7bca9",
                width=2,
            )
            with Image.open(source / record["relative_path"]) as raw:
                image = ImageOps.exif_transpose(raw).convert("RGB")
                image.thumbnail(
                    (image_width, image_height), Image.Resampling.LANCZOS
                )
                x = left + (cell_width - image.width) // 2
                y = top + 15 + (image_height - image.height) // 2
                canvas.paste(image, (x, y))
            short_name = Path(record["file"]).stem[:12]
            label = f"{record['index']:02d}  {short_name}"
            dimensions = f"{record['width']}×{record['height']}  {record['bytes'] / 1024 / 1024:.1f} MB"
            draw.text((left + 14, top + 241), label, fill="#241f1a", font=font)
            draw.text(
                (left + 14, top + 264), dimensions, fill="#71665c", font=small_font
            )
        filename = f"contact-sheet-{page + 1}.jpg"
        canvas.save(output / filename, "JPEG", quality=90, optimize=True)
        sheets.append(filename)
    return sheets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="原始照片目录")
    parser.add_argument("output", type=Path, help="扫描报告输出目录")
    args = parser.parse_args()

    records = scan_images(args.source)
    exact_groups, near_groups = duplicate_report(records)
    sheets = create_contact_sheets(args.source, records, args.output)
    report = {
        "source": str(args.source.resolve()),
        "total": len(records),
        "valid": sum(record["valid"] for record in records),
        "invalid": sum(not record["valid"] for record in records),
        "exact_duplicate_groups": exact_groups,
        "near_duplicate_candidates": near_groups,
        "contact_sheets": sheets,
        "images": records,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "scan-report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "report": str(report_path),
                "total": report["total"],
                "valid": report["valid"],
                "invalid": report["invalid"],
                "exact_duplicate_groups": len(exact_groups),
                "near_duplicate_candidates": len(near_groups),
                "contact_sheets": sheets,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
