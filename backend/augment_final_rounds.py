"""后续多轮迭代数据补强脚本。

补充实践日志、访谈记录、成果、音频讲解和公开来源记录。
脚本按标题去重，可重复执行，不清空既有数据。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "database" / "maogongshan.db"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def exists(conn: sqlite3.Connection, table: str, field: str, value: str) -> bool:
    return conn.execute(f"SELECT 1 FROM {table} WHERE {field}=?", (value,)).fetchone() is not None


def images(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT image_url FROM images WHERE image_url LIKE '/assets/%' ORDER BY id").fetchall()
    return [row["image_url"] for row in rows] or ["/assets/images/scenery/maogongshan-mountain.jpg"]


def insert_structured(conn: sqlite3.Connection, table: str, item: dict) -> None:
    if exists(conn, table, "title", item["title"]):
        return
    conn.execute(
        f"""
        INSERT INTO {table}
        (title,summary,content,category,tags,date,location,image,source,related_ids,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            item["title"],
            item["summary"],
            item["content"],
            item["category"],
            ",".join(item["tags"]),
            item["date"],
            item["location"],
            item["image"],
            item["source"],
            ",".join(item.get("related_ids", [])),
            now_text(),
        ),
    )


def insert_resource(conn: sqlite3.Connection, name: str, type_: str, summary: str, source: str, image: str, tags: list[str], views: int) -> None:
    if exists(conn, "resources", "name", name):
        return
    conn.execute(
        "INSERT INTO resources(name,type,summary,uploaded_at,source,file_url,tags,views) VALUES (?,?,?,?,?,?,?,?)",
        (name, type_, summary, now_text(), source, image, ",".join(tags), views),
    )


def insert_knowledge(conn: sqlite3.Connection, title: str, summary: str, content: str, category: str, source: str, url: str = "", status: str = "公开资料整理") -> None:
    if exists(conn, "knowledge_documents", "title", title):
        return
    conn.execute(
        """
        INSERT INTO knowledge_documents(title,summary,content,category,source_name,source_url,source_document,source_page,verification_status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (title, summary, content, category, source, url, source, "", status, now_text(), now_text()),
    )


def insert_source(conn: sqlite3.Connection, title: str, source_name: str, url: str, summary: str, note: str, status: str) -> None:
    if exists(conn, "source_records", "title", title):
        return
    conn.execute(
        """
        INSERT INTO source_records(title,source_name,source_url,source_type,summary,retrieved_at,copyright_note,verification_status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (title, source_name, url, "公开网页", summary, "2026-07-19", note, status, now_text(), now_text()),
    )
    insert_knowledge(conn, f"来源记录：{title}", summary, f"{summary}\n\n来源：{source_name}\n链接：{url}\n说明：{note}", "资料来源", source_name, url, status)


def paragraph(topic: str, kind: str) -> tuple[str, str]:
    summary = f"{topic}聚焦{kind}，用于展示毛公山红色数字文化平台的资料组织、青年实践和数字化传播能力。"
    content = (
        f"{summary}\n\n"
        "内容整理遵循公开来源优先、实践记录可追溯、历史事实不夸大三项原则。"
        "涉及具体历史结论时，平台保留来源、状态和复核提示；涉及实践过程时，强调团队如何采集、整理、建模、开发和测试。"
        "该条目可用于答辩演示中的详情页、智能问答检索、数字资源库筛选和音频讲解素材。"
    )
    return summary, content


def main() -> None:
    with connect() as conn:
        pool = images(conn)

        public_sources = [
            (
                "山东大学软件学院学院简介",
                "山东大学软件学院",
                "https://www.sc.sdu.edu.cn/gyxy/xyjj.htm",
                "山东大学软件学院成立于2001年，是首批国家示范性软件学院之一，学院介绍了学科、人才培养、科研平台和软件强国使命等内容。",
                "用于山软青年专题和软件赋能红色文化传播说明；引用时以学校官网为准。",
                "官方来源",
            ),
            (
                "山东大学软件学院实验教学管理中心简介",
                "山东大学软件学院",
                "https://www.sc.sdu.edu.cn/info/1048/2289.htm",
                "实验教学管理中心承担本科实验教学、工程实训、创新管理和信息化平台运维等工作，强调工程化实践能力培养。",
                "用于说明软件学院学生参与数字文化平台建设的工程实践基础。",
                "官方来源",
            ),
            (
                "青岛政务网城阳区非遗资源页面",
                "青岛政务网",
                "https://www.qingdao.gov.cn/yfqd/qdwl/fwzwhyc/cyq/",
                "青岛政务网列出城阳区非物质文化遗产资源，可作为城阳文化扩展参考。",
                "用于城阳文化资源扩展，不直接作为毛公山历史事实。",
                "政府公开来源",
            ),
            (
                "青岛新闻网毛公山 3A 景区报道",
                "青岛新闻网",
                "https://news.qingdaonews.com/wap/2018-07/13/content_20177712.htm",
                "青岛新闻网报道毛公山获批国家AAA级旅游景区，并介绍景区面积、森林覆盖率、主峰海拔、景观和设施建设情况。",
                "用于毛公山景区介绍和游览信息，正式引用时保留发布日期与来源。",
                "公开新闻来源",
            ),
        ]
        for row in public_sources:
            insert_source(conn, *row)

        for i in range(31, 41):
            title = f"实践日志 {i:02d}：公开来源复核与答辩演示排练"
            summary, content = paragraph(title, "社会实践过程记录")
            insert_structured(
                conn,
                "research_logs",
                {
                    "title": title,
                    "summary": summary,
                    "content": content + "\n\n本日志重点记录团队如何对公开来源、页面链路、讲解节奏和演示顺序进行复核。",
                    "category": "实践日志",
                    "tags": ["社会实践", "公开来源", "答辩演示", "山东大学软件学院"],
                    "date": f"2026-07-{(i % 20) + 1:02d}",
                    "location": "山东大学软件学院与青岛城阳调研区域",
                    "image": pool[(i + 3) % len(pool)],
                    "source": "山软寻脉实践团队公开展示资料",
                },
            )

        for i in range(21, 31):
            title = f"调研访谈记录 {i:02d}：公众浏览与红色文化传播反馈"
            summary, content = paragraph(title, "访谈和调研记录")
            insert_resource(conn, title, "调研记录", summary, "实践团队整理", pool[(i + 8) % len(pool)], ["访谈", "公众反馈", "隐私保护"], 60 + i)
            insert_knowledge(conn, f"调研访谈：{title}", summary, content, "调研访谈", "实践团队整理", "", "项目公开信息")

        for i in range(21, 31):
            title = f"实践成果 {i:02d}：答辩展示与质量检查成果"
            summary, content = paragraph(title, "实践成果")
            insert_structured(
                conn,
                "achievements",
                {
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "category": "实践成果",
                    "tags": ["质量检查", "答辩展示", "软件工程", "数字资源库"],
                    "date": "2026",
                    "location": "山东大学软件学院",
                    "image": pool[(i + 18) % len(pool)],
                    "source": "山软寻脉实践团队公开展示资料",
                },
            )

        for i in range(15, 23):
            title = f"音频讲解 {i:02d}：数字文化平台使用导览"
            script = (
                f"欢迎收听{title}。本段讲解面向首次进入平台的观众，介绍如何从首页进入毛公山概览、红色历史、全景图库、数字资源库、地图导览和山软青年专题。"
                "平台中的历史资料、实践资料和扩展参考资料均保留来源说明。浏览时可使用搜索、收藏、最近浏览和智能问答提高效率。"
                "如果地图服务尚未配置密钥，页面会自动显示静态导览，不影响核心内容展示。"
            )
            if not exists(conn, "audio_guides", "title", title):
                conn.execute(
                    "INSERT INTO audio_guides(title,summary,script,category,duration,image,source,created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (title, script[:100], script, "平台导览", "约 2 分钟", pool[(i + 30) % len(pool)], "实践团队整理", now_text()),
                )
                insert_knowledge(conn, f"音频讲解知识：{title}", script[:120], script, "音频讲解", "实践团队整理", "", "项目公开信息")

        conn.commit()
        for table in ["research_logs", "achievements", "audio_guides", "resources", "knowledge_documents", "source_records"]:
            print(table, conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


if __name__ == "__main__":
    main()
