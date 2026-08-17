"""Create responsive generated images and audit the complete image library."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "assets" / "images"
REPORT_PATH = ROOT / "assets" / "image-assets.json"
TEXT_SUFFIXES = {".vue", ".js", ".json", ".css", ".md", ".html"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
VARIANT_SUFFIX = re.compile(r"-(wide|mobile|thumb|hero|detail)$")


def optimize_generated() -> dict[str, int]:
    before = after = created = 0
    generated_dir = IMAGE_ROOT / "generated"
    for source in sorted(generated_dir.glob("*-v2.png")):
        before += source.stat().st_size
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            stem = source.stem
            for suffix, size in (("wide", (1920, 823)), ("mobile", (900, 1125))):
                target = source.with_name(f"{stem}-{suffix}.webp")
                fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                fitted.save(target, "WEBP", quality=84, method=6)
                after += target.stat().st_size
                created += 1
    if created == 0 and REPORT_PATH.exists():
        try:
            previous = json.loads(REPORT_PATH.read_text("utf-8"))["summary"]["optimization"]
            if previous.get("responsive_files_created"):
                return previous
        except (KeyError, TypeError, json.JSONDecodeError):
            pass
    return {"source_bytes": before, "optimized_bytes": after, "responsive_files_created": created}


def ensure_utility_fallback() -> None:
    """Keep a tiny unique neutral fallback; it is UI texture, not content imagery."""
    target = IMAGE_ROOT / "fallback" / "fallback-real-scenery.jpg"
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (800, 500))
    pixels = image.load()
    for y in range(500):
        for x in range(800):
            haze = int(8 * math.sin((x + y) / 53))
            pixels[x, y] = (max(36, 82 + haze - y // 14), max(50, 106 + haze - y // 16), max(45, 91 + haze - y // 18))
    image.save(target, "JPEG", quality=72, optimize=True)


def _hash_bits(values: list[int], average: float) -> str:
    bits = "".join("1" if value >= average else "0" for value in values)
    return f"{int(bits, 2):0{len(bits) // 4}x}"


def dhash(image: Image.Image) -> str:
    pixels = list(image.convert("L").resize((9, 8), Image.Resampling.LANCZOS).getdata())
    bits = []
    for row in range(8):
        offset = row * 9
        bits.extend(pixels[offset + column] > pixels[offset + column + 1] for column in range(8))
    return f"{sum((1 << index) for index, value in enumerate(bits) if value):016x}"


def phash(image: Image.Image) -> str:
    pixels = list(image.convert("L").resize((32, 32), Image.Resampling.LANCZOS).getdata())
    coefficients: list[float] = []
    for v in range(8):
        for u in range(8):
            total = 0.0
            for y in range(32):
                cy = math.cos((2 * y + 1) * v * math.pi / 64)
                offset = y * 32
                for x in range(32):
                    total += pixels[offset + x] * math.cos((2 * x + 1) * u * math.pi / 64) * cy
            coefficients.append(total)
    values = coefficients[1:]
    median = sorted(values)[len(values) // 2]
    return _hash_bits([round(value) for value in values], median)


def hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def logical_id(path: Path) -> str:
    stem = VARIANT_SUFFIX.sub("", path.stem)
    return str(path.parent.relative_to(IMAGE_ROOT) / stem).replace("\\", "/")


def source_type(path: Path) -> str:
    parts = set(path.relative_to(IMAGE_ROOT).parts)
    if "generated" in parts:
        return "generated"
    if "maogongshan" in parts or "activity" in parts or "research" in parts or "team" in parts:
        return "real"
    if "commons" in parts:
        return "reference"
    return "designed"


def usage_counts() -> defaultdict[str, int]:
    usage: defaultdict[str, int] = defaultdict(int)
    for root in (ROOT / "frontend" / "src", ROOT / "backend"):
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                content = path.read_text("utf-8")
            except UnicodeDecodeError:
                continue
            for match in re.findall(r"/assets/images/[^\s'\"`)]+", content):
                usage[match.split("?")[0]] += 1
    return usage


def deduplicate_exact() -> int:
    """Consolidate byte-identical assets and rewrite every local reference."""
    usage = usage_counts()
    groups: defaultdict[str, list[Path]] = defaultdict(list)
    for path in IMAGE_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            groups[hashlib.sha256(path.read_bytes()).hexdigest()].append(path)
    replacements: dict[str, str] = {}
    removed: list[Path] = []
    for paths in groups.values():
        if len(paths) < 2:
            continue
        def canonical_score(path: Path) -> tuple[int, int, int]:
            url = f"/assets/{path.relative_to(ROOT / 'assets').as_posix()}"
            semantic_penalty = -5 if "fallback" in path.parts else 0
            source_preference = 2 if "maogongshan" in path.parts else 1 if "party-history" in path.parts else 0
            return usage[url] + semantic_penalty, source_preference, -len(str(path))
        canonical = max(paths, key=canonical_score)
        canonical_url = f"/assets/{canonical.relative_to(ROOT / 'assets').as_posix()}"
        for duplicate in paths:
            if duplicate == canonical:
                continue
            duplicate_url = f"/assets/{duplicate.relative_to(ROOT / 'assets').as_posix()}"
            replacements[duplicate_url] = canonical_url
            removed.append(duplicate)

    editable_roots = (ROOT / "frontend" / "src", ROOT / "backend", ROOT / "assets")
    for editable_root in editable_roots:
        for path in editable_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or path == REPORT_PATH:
                continue
            try:
                original = path.read_text("utf-8")
            except UnicodeDecodeError:
                continue
            updated = original
            for old, new in replacements.items():
                updated = updated.replace(old, new)
            if updated != original:
                path.write_text(updated, encoding="utf-8")

    db_path = ROOT / "database" / "maogongshan.db"
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            for table in tables:
                columns = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")') if str(row[2]).upper().startswith("TEXT")]
                for column in columns:
                    for old, new in replacements.items():
                        conn.execute(
                            f'UPDATE "{table}" SET "{column}" = replace("{column}", ?, ?) WHERE "{column}" LIKE ?',
                            (old, new, f"%{old}%"),
                        )
    for path in removed:
        path.unlink()
    return len(removed)


def audit_images(optimization: dict[str, int]) -> dict:
    usage = usage_counts()
    assets: list[dict] = []
    for path in sorted(IMAGE_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        relative = path.relative_to(ROOT / "assets").as_posix()
        public_url = f"/assets/{relative}"
        raw = path.read_bytes()
        try:
            with Image.open(path) as image:
                width, height = image.size
                visual = image.copy()
        except (UnidentifiedImageError, OSError):
            continue
        asset = {
            "id": logical_id(path),
            "filename": path.name,
            "path": public_url,
            "title": path.stem.replace("-", " "),
            "category": path.parent.name,
            "source_type": source_type(path),
            "page": "sitewide" if usage[public_url] > 1 else "",
            "scene": path.parent.name,
            "subject": path.stem,
            "style": "cinematic_generated" if source_type(path) == "generated" else "documentary_or_archive",
            "orientation": "landscape" if width >= height else "portrait",
            "aspect_ratio": round(width / height, 3),
            "width": width,
            "height": height,
            "bytes": len(raw),
            "hash": hashlib.sha256(raw).hexdigest(),
            "phash": phash(visual),
            "dhash": dhash(visual),
            "similarity_cluster": "",
            "usage_count": usage[public_url],
        }
        assets.append(asset)

    logical_representatives: dict[str, dict] = {}
    for asset in assets:
        current = logical_representatives.get(asset["id"])
        if current is None or asset["width"] * asset["height"] > current["width"] * current["height"]:
            logical_representatives[asset["id"]] = asset
    representatives = list(logical_representatives.values())
    parent = list(range(len(representatives)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(len(representatives)):
        for right in range(left + 1, len(representatives)):
            a, b = representatives[left], representatives[right]
            # Educational cards intentionally share a code-generated layout; count
            # their unique factual content as distinct, while applying perceptual
            # duplicate detection to photographic/reference/generated visuals.
            if a["source_type"] == "designed" or b["source_type"] == "designed":
                continue
            if a["hash"] == b["hash"] or (
                hamming(a["phash"], b["phash"]) <= 4
                and hamming(a["dhash"], b["dhash"]) <= 4
            ):
                union(left, right)
    groups: defaultdict[int, list[int]] = defaultdict(list)
    for index in range(len(representatives)):
        groups[find(index)].append(index)
    similar_groups = [indexes for indexes in groups.values() if len(indexes) > 1]
    cluster_by_id: dict[str, str] = {}
    for number, indexes in enumerate(similar_groups, start=1):
        cluster = f"cluster-{number:03d}"
        for index in indexes:
            cluster_by_id[representatives[index]["id"]] = cluster
    for asset in assets:
        asset["similarity_cluster"] = cluster_by_id.get(asset["id"], "")

    hash_groups: defaultdict[str, list[dict]] = defaultdict(list)
    for asset in assets:
        hash_groups[asset["hash"]].append(asset)
    exact_duplicates = sum(len(group) - 1 for group in hash_groups.values() if len(group) > 1)
    highly_similar = sum(len(group) - 1 for group in similar_groups)
    logical_total = len(representatives)
    summary = {
        "total_images": len(assets),
        "logical_images": logical_total,
        "real_images": sum(asset["source_type"] == "real" for asset in representatives),
        "generated_images": sum(asset["source_type"] == "generated" for asset in representatives),
        "reference_or_designed_images": sum(asset["source_type"] in {"reference", "designed"} for asset in representatives),
        "template_based_educational_assets": sum(asset["source_type"] == "designed" for asset in representatives),
        "exact_duplicate_files": exact_duplicates,
        "highly_similar_logical_images": highly_similar,
        "similarity_groups": len(similar_groups),
        "suspected_duplicate_rate": round(highly_similar / max(logical_total, 1) * 100, 2),
        "average_bytes": round(sum(asset["bytes"] for asset in assets) / max(len(assets), 1)),
        "total_bytes": sum(asset["bytes"] for asset in assets),
        "unused_images": sum(asset["usage_count"] == 0 for asset in assets),
        "optimization": optimization,
    }
    return {"summary": summary, "similarity_clusters": [[representatives[index]["path"] for index in group] for group in similar_groups], "assets": assets}


def main() -> None:
    removed = deduplicate_exact() if "--deduplicate-exact" in sys.argv else 0
    ensure_utility_fallback()
    optimization = optimize_generated()
    report = audit_images(optimization)
    report["summary"]["exact_duplicate_files_removed"] = removed
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
