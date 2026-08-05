"""整理项目提供的毛公山照片并安全导入资源库。

原始照片只读。脚本会：
1. 自动修正 EXIF 方向；
2. 为网页生成 WebP 缩略图、详情图和移动端图；
3. 为精选横向照片生成首页横幅；
4. 以标题为唯一键重复安全地写入 SQLite；
5. 同步生成前端统一图片清单。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

try:
    from .config import DB_PATH, PROJECT_ROOT
except ImportError:
    from config import DB_PATH, PROJECT_ROOT


PHOTO_LIBRARY = [
    (1, "mountain-view-west", "层峦远眺", "毛公山自然风景", "自然风光", "从林木间远眺毛公山周边层叠山势。", "毛公山山林与远山实景"),
    (2, "peak-red-flags", "红旗映山峰", "毛公山自然风景", "自然风光", "山峰、松林与红旗共同构成毛公山景区的山地景观。", "毛公山山峰与红旗实景"),
    (3, "research-biography-display", "人物资料展板调研", "社会实践与调研活动", "实践记录", "实践团队在红色文化展陈空间查看人物资料展板。", "实践团队查看人物资料展板"),
    (4, "research-history-gallery-a", "历史图片展陈调研", "社会实践与调研活动", "实践记录", "团队成员在现场阅读历史图片与文字展陈。", "实践团队查看历史图片展陈"),
    (5, "scenic-entry", "毛公山景区入口", "毛公山景区建筑", "景区建筑", "毛公山景区入口及开放时间提示的现场记录。", "毛公山景区入口实景"),
    (6, "research-party-history-display-a", "党史展陈现场记录", "社会实践与调研活动", "实践记录", "团队成员对党史图文展板进行现场观察和资料采集。", "实践团队查看党史图文展板"),
    (7, "revolutionary-route-marker", "革命道路主题石刻", "毛公山景区建筑", "红色文化", "毛公山景区步道旁的“革命道路”主题石刻。", "毛公山革命道路主题石刻"),
    (8, "stone-step-trail", "山间石阶步道", "毛公山自然风景", "登山道路", "沿山势铺设的石阶步道与路旁植被。", "毛公山山间石阶步道"),
    (9, "forest-trail-view", "林间步道", "毛公山自然风景", "登山道路", "穿行于山林之间的登山步道，植被层次丰富。", "毛公山林间登山步道"),
    (10, "research-party-history-display-b", "红色文化展板采集", "社会实践与调研活动", "实践记录", "实践团队记录红色文化展板的结构与内容呈现方式。", "实践团队采集红色文化展板资料"),
    (11, "exhibition-calligraphy", "主题书法展陈", "红色文化与党史", "红色文化", "红色文化展陈空间内的主题书法作品，具体文字释义以现场展签为准。", "红色文化主题书法展陈"),
    (12, "exhibition-people-life", "人民生活主题展陈", "红色文化与党史", "历史资料", "以历史图片和实物资料呈现人民生活主题的展陈区域。", "人民生活主题历史资料展陈"),
    (13, "valley-view", "山谷绿意", "毛公山自然风景", "自然风光", "山坡林木、远山与云层形成开阔的山谷景观。", "毛公山山谷与林木实景"),
    (14, "hillside-city-view", "山腰远眺", "毛公山自然风景", "自然风光", "从山腰远眺周边城区和山林的开阔视野。", "毛公山山腰远眺实景"),
    (16, "forest-rocks", "林木与山石", "毛公山自然风景", "自然风光", "林间巨石与自然植被共同形成的山地景观。", "毛公山林木与山石实景"),
    (17, "winding-trail", "蜿蜒山路", "毛公山自然风景", "登山道路", "沿林木和山坡延伸的蜿蜒登山道路。", "毛公山蜿蜒登山道路"),
    (18, "team-platform-group", "实践团队山顶合影", "山东大学软件学院团队", "团队风采", "实践团队在毛公山观景平台开展现场记录并合影。未对照片中的成员身份作个人识别。", "实践团队在毛公山观景平台合影"),
    (19, "culture-poetry-wall", "山间文化诗墙", "毛公山景区建筑", "景区建筑", "山间步道旁的文化文字景观，具体内容以现场实物为准。", "毛公山山间文化诗墙"),
    (20, "forest-service-point", "林间休憩节点", "毛公山景区建筑", "景区建筑", "登山道路旁设置的林间休憩与导览节点。", "毛公山林间休憩节点"),
    (21, "exhibition-artworks", "历史主题画作展陈", "红色文化与党史", "红色文化", "展馆内陈列的历史主题画作，属于艺术创作类展陈。", "红色文化历史主题画作展陈"),
    (22, "red-culture-exhibition-entrance", "红色文化展陈入口", "毛公山景区建筑", "景区建筑", "毛公山红色文化展陈空间入口的现场记录。", "毛公山红色文化展陈空间入口"),
    (23, "research-mao-display", "主题人物展陈调研", "社会实践与调研活动", "实践记录", "团队成员查看主题人物与历史资料展陈。", "实践团队查看主题人物展陈"),
    (24, "research-document-wall", "历史文献墙调研", "社会实践与调研活动", "实践记录", "团队成员阅读大幅历史文献墙并记录资料组织方式。", "实践团队阅读历史文献展墙"),
    (26, "exhibition-history-table", "历史资料陈列台", "红色文化与党史", "历史资料", "图文、地图和实物复制件组合构成的历史资料陈列台。", "红色文化历史资料陈列台"),
    (27, "exhibition-mass-line", "历史场景艺术展板", "红色文化与党史", "红色文化", "展馆内以艺术画面呈现历史场景的主题展板，不作为历史现场照片使用。", "红色文化历史场景艺术展板"),
    (28, "figure-profile-display-a", "人物事迹资料展板一", "人物故事", "人物故事", "展馆内的人物事迹资料展板，人物姓名与事迹以现场展板原文为准。", "红色文化人物事迹资料展板"),
    (29, "historical-materials-cabinet", "历史资料陈列柜", "红色文化与党史", "历史资料", "用于展示文献复制件和相关资料的历史资料陈列柜。", "红色文化历史资料陈列柜"),
    (30, "mao-source-display", "名称由来主题展板", "红色文化与党史", "红色文化", "介绍毛公山名称与文化叙事的现场主题展板，具体表述以展陈原文为准。", "毛公山名称由来主题展板"),
    (31, "mountain-road", "山间道路", "毛公山自然风景", "登山道路", "连接山林景观节点的景区道路。", "毛公山山间道路实景"),
    (32, "exhibition-artifacts", "历史主题实物展陈", "红色文化与党史", "历史资料", "历史主题画作与实物复制件共同组成的展陈区域。", "红色文化历史主题实物展陈"),
    (33, "summit-terrace-panorama", "观景平台全景", "首页轮播图", "毛公山全景", "从毛公山观景平台眺望山体、城区与远方天际。", "毛公山观景平台全景实拍"),
    (37, "green-stone-path", "绿荫石板路", "毛公山自然风景", "登山道路", "被浓密植被环绕的山间石板道路。", "毛公山绿荫石板道路"),
    (38, "qingdao-liberation-exhibition", "青岛解放主题展陈", "红色文化与党史", "历史资料", "展馆内关于青岛解放相关历史资料的主题展陈。", "青岛解放相关历史资料展陈"),
    (39, "qingdao-liberation-material", "青岛解放资料图板", "红色文化与党史", "历史资料", "以历史图片和文字介绍青岛解放的资料图板。", "青岛解放历史资料图板"),
    (40, "culture-wall-path", "山间文化墙步道", "毛公山景区建筑", "景区建筑", "文化墙、木质护栏与山林步道组成的景观节点。", "毛公山山间文化墙步道"),
    (41, "layered-mountain-view", "云下群山", "毛公山自然风景", "自然风光", "云层下的近景林木与远处山脉层次。", "毛公山云下群山实景"),
    (43, "pine-ridge-view", "松林山脊", "毛公山自然风景", "自然风光", "松林、裸露山石与山脊构成的自然景观。", "毛公山松林山脊实景"),
    (44, "outdoor-poetry-wall", "户外主题文字墙", "毛公山景区建筑", "景区建筑", "景区户外主题文字墙与周边环境的现场记录。", "毛公山户外主题文字墙"),
    (45, "historical-photo-wall", "历史照片资料墙", "红色文化与党史", "历史资料", "由多幅历史资料图片构成的展馆照片墙。", "红色文化历史照片资料墙"),
    (46, "figure-profile-display-b", "人物事迹资料展板二", "人物故事", "人物故事", "展馆内的人物事迹资料展板，未根据画面猜测人物身份。", "红色文化人物事迹资料展板"),
    (47, "exhibition-sculpture", "历史主题场景雕塑", "红色文化与党史", "红色文化", "展馆内用于辅助讲述历史文化的场景雕塑，属于当代展陈艺术。", "红色文化历史主题场景雕塑"),
    (48, "figure-profile-display-c", "人物事迹资料展板三", "人物故事", "人物故事", "展馆内的人物事迹资料展板，人物信息以现场展签为准。", "红色文化人物事迹资料展板"),
]

SKIPPED_NEAR_DUPLICATES = {
    15: "与 4 号历史图片展陈调研照片构图高度相似",
    25: "与 10 号红色文化展板采集照片构图高度相似",
    34: "与 4 号历史图片展陈调研照片构图高度相似",
    35: "与 6 号党史展陈现场记录照片构图高度相似",
    36: "与 33 号观景平台全景构图高度相似",
    42: "与 18 号实践团队山顶合影画面相同",
}

HERO_SLUGS = [
    "summit-terrace-panorama",
    "mountain-view-west",
    "peak-red-flags",
    "hillside-city-view",
    "mountain-road",
]

CATEGORY_DIRS = {
    "毛公山自然风景": "scenery",
    "毛公山景区建筑": "architecture",
    "红色文化与党史": "red-culture",
    "社会实践与调研活动": "research",
    "山东大学软件学院团队": "team",
    "首页轮播图": "banners",
    "新闻与活动": "news",
    "人物故事": "people",
}


def source_files(source_dir: Path) -> dict[int, Path]:
    files = sorted(
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    return {index: path for index, path in enumerate(files, start=1)}


def save_bounded(image: Image.Image, path: Path, bounds: tuple[int, int], quality: int) -> None:
    output = image.copy()
    output.thumbnail(bounds, Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    output.save(path, "WEBP", quality=quality, method=6)


def save_hero(image: Image.Image, path: Path) -> None:
    output = ImageOps.fit(
        image,
        (1920, 960),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.48),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    output.save(path, "WEBP", quality=87, method=6)


def migrate_images_table(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(images)")}
    additions = {
        "slug": "TEXT",
        "alt": "TEXT",
        "thumbnail_url": "TEXT",
        "mobile_url": "TEXT",
        "detail_url": "TEXT",
        "original_file": "TEXT",
        "source_type": "TEXT",
        "verification_status": "TEXT",
        "sort_order": "INTEGER DEFAULT 0",
    }
    for column, definition in additions.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE images ADD COLUMN {column} {definition}")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_images_slug ON images(slug)")


def upsert_image(conn: sqlite3.Connection, item: dict) -> int:
    columns = [
        "title", "image_url", "source_name", "source_url", "description",
        "captured_at", "location", "category", "copyright_note", "created_at",
        "updated_at", "slug", "alt", "thumbnail_url", "mobile_url", "detail_url",
        "original_file", "source_type", "verification_status", "sort_order",
    ]
    existing = conn.execute("SELECT id FROM images WHERE slug=?", (item["slug"],)).fetchone()
    values = [item[column] for column in columns]
    if existing:
        assignments = ", ".join(f"{column}=?" for column in columns)
        conn.execute(f"UPDATE images SET {assignments} WHERE id=?", [*values, existing[0]])
        return int(existing[0])
    placeholders = ", ".join("?" for _ in columns)
    cursor = conn.execute(
        f"INSERT INTO images ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    return int(cursor.lastrowid)


def update_research_log_images(conn: sqlite3.Connection, manifest: list[dict]) -> None:
    research_images = [item["detail_url"] for item in manifest if item["group"] == "社会实践与调研活动"]
    if not research_images:
        return
    rows = conn.execute("SELECT id FROM research_logs ORDER BY date DESC, id DESC").fetchall()
    for index, row in enumerate(rows):
        conn.execute(
            "UPDATE research_logs SET image=? WHERE id=?",
            (research_images[index % len(research_images)], row[0]),
        )


def process(source_dir: Path, public_root: Path, database: Path) -> dict:
    files = source_files(source_dir)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manifest: list[dict] = []
    asset_root = public_root / "assets" / "images"
    copyright_note = "项目提供的本地照片资料；公开传播或商业使用前请由项目团队确认授权范围。"

    for order, (index, slug, title, group, category, description, alt) in enumerate(PHOTO_LIBRARY, start=1):
        source = files[index]
        directory = CATEGORY_DIRS[group]
        output_dir = asset_root / directory
        with Image.open(source) as raw:
            image = ImageOps.exif_transpose(raw).convert("RGB")
            detail_path = output_dir / f"{slug}-detail.webp"
            thumb_path = output_dir / f"{slug}-thumb.webp"
            mobile_path = output_dir / f"{slug}-mobile.webp"
            save_bounded(image, detail_path, (2200, 2200), 87)
            save_bounded(image, thumb_path, (760, 760), 82)
            save_bounded(image, mobile_path, (1080, 1440), 84)
            if slug in HERO_SLUGS:
                save_hero(image, asset_root / "banners" / f"{slug}-hero.webp")

        web_prefix = f"/assets/images/{directory}/{slug}"
        item = {
            "id": 0,
            "slug": slug,
            "title": title,
            "group": group,
            "category": category,
            "description": description,
            "alt": alt,
            "image_url": f"{web_prefix}-detail.webp",
            "detail_url": f"{web_prefix}-detail.webp",
            "thumbnail_url": f"{web_prefix}-thumb.webp",
            "mobile_url": f"{web_prefix}-mobile.webp",
            "hero_url": f"/assets/images/banners/{slug}-hero.webp" if slug in HERO_SLUGS else "",
            "source_name": "项目提供的毛公山照片资料",
            "source_url": "",
            "source_type": "项目本地照片",
            "original_file": source.name,
            "captured_at": "原始照片未标注",
            "location": "毛公山景区及红色文化展陈空间",
            "copyright_note": copyright_note,
            "verification_status": "项目素材",
            "sort_order": order,
            "created_at": now,
            "updated_at": now,
            "detail_link": "",
        }
        manifest.append(item)

    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as conn:
        migrate_images_table(conn)
        for item in manifest:
            item["id"] = upsert_image(conn, item)
            item["detail_link"] = f"/photos/{item['slug']}"
        update_research_log_images(conn, manifest)
        conn.commit()

    payload = {
        "generated_at": now,
        "source_directory": "毛公山照片",
        "total_source_images": len(files),
        "used_images": len(manifest),
        "skipped_images": [
            {"index": index, "file": files[index].name, "reason": reason}
            for index, reason in SKIPPED_NEAR_DUPLICATES.items()
        ],
        "hero_slugs": HERO_SLUGS,
        "images": manifest,
    }
    frontend_manifest = PROJECT_ROOT / "frontend" / "src" / "data" / "maogongshanPhotos.json"
    backend_manifest = PROJECT_ROOT / "database" / "maogongshan_photos.json"
    for target in (frontend_manifest, backend_manifest):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def sync_manifest_records(conn: sqlite3.Connection) -> int:
    """从随项目打包的清单恢复照片记录，不依赖原始照片目录。"""
    manifest_path = PROJECT_ROOT / "database" / "maogongshan_photos.json"
    if not manifest_path.exists():
        return 0
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    migrate_images_table(conn)
    count = 0
    for item in payload.get("images", []):
        record = dict(item)
        record["detail_link"] = f"/photos/{record['slug']}"
        upsert_image(conn, record)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=PROJECT_ROOT / "毛公山照片",
        help="原始照片目录",
    )
    parser.add_argument(
        "--public-root",
        type=Path,
        default=PROJECT_ROOT,
        help="包含 assets 目录的项目根目录（保留旧参数名以兼容原命令）",
    )
    parser.add_argument("--database", type=Path, default=DB_PATH)
    args = parser.parse_args()
    if not args.source.exists():
        raise SystemExit(f"未找到原始照片目录：{args.source}")
    result = process(args.source.resolve(), args.public_root.resolve(), args.database.resolve())
    print(
        json.dumps(
            {
                "total_source_images": result["total_source_images"],
                "used_images": result["used_images"],
                "skipped_images": len(result["skipped_images"]),
                "database": str(args.database.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
