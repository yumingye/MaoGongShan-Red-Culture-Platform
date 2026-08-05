from __future__ import annotations

import re
import sqlite3
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from app import DB_PATH, create_tables, rebuild_knowledge_documents


SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{17}[\dXx]\b"),
    re.compile(r"\b1[3-9]\d{9}\b"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"(家庭住址|家庭所在地|身份证|手机号|电话|邮箱|住址)[:：]?\s*\S+"),
]

SOURCE_TITLE = "《山软寻脉·毛公山数字调研实践团社会实践立项申请书》"


def clean_public_text(text: str) -> str:
    """删除身份证、手机号、邮箱、住址等不应公开的信息。"""
    text = text.strip()
    for pattern in SENSITIVE_PATTERNS:
        text = pattern.sub("[已移除敏感信息]", text)
    return text


def extract_docx_text(path: Path) -> list[str]:
    """使用标准库读取 docx 文本，避免额外依赖。"""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        parts = [node.text or "" for node in para.findall(".//w:t", ns)]
        text = clean_public_text("".join(parts))
        if text and text != "[已移除敏感信息]":
            paragraphs.append(text)
    return paragraphs


def upsert(conn: sqlite3.Connection, table: str, key: str, value: str, insert_sql: str, params: tuple) -> None:
    if not conn.execute(f"SELECT 1 FROM {table} WHERE {key}=? LIMIT 1", (value,)).fetchone():
        conn.execute(insert_sql, params)


def import_public_project_doc(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"未找到Word文件：{path}")
    paragraphs = extract_docx_text(path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    joined = "\n".join(paragraphs)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        create_tables(conn)
        upsert(
            conn,
            "source_records",
            "title",
            SOURCE_TITLE,
            """
            INSERT INTO source_records(title, source_name, source_url, source_type, summary, retrieved_at, copyright_note, verification_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (SOURCE_TITLE, "山东大学软件学院实践团队项目材料", "", "项目申报材料", "已整理项目公开字段。", now[:10], "用于社会实践成果展示。", "项目材料", now, now),
        )
        upsert(
            conn,
            "knowledge_documents",
            "title",
            "Word导入：社会实践立项申请书公开内容",
            """
            INSERT INTO knowledge_documents(title, summary, content, category, source_name, source_url, source_document, source_page, verification_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        ("Word导入：社会实践立项申请书公开内容", "Word文档公开内容摘要。", joined[:12000], "项目申报材料", SOURCE_TITLE, "", SOURCE_TITLE, "自动提取", "项目材料", now, now),
        )
        rebuild_knowledge_documents(conn)
    print(f"导入完成：{path}")
    print("已过滤身份证号、手机号、邮箱和住址等敏感信息。")


if __name__ == "__main__":
    default_path = Path(__file__).resolve().parent.parent / "docs" / "山软寻脉·毛公山数字调研实践团+于茗烨.docx"
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    import_public_project_doc(target)
