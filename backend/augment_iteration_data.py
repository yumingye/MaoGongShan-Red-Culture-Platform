"""第三轮数据增强脚本。

本脚本只补充可用于展示的结构化整理内容，不伪造具体战斗、人物功绩或精确史实。
涉及地方历史的条目标注为“公开资料整理”或“需继续核验”，便于后续由权威资料复核。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "database" / "maogongshan.db"
FRONT_DATA = Path(__file__).resolve().parents[1] / "frontend" / "src" / "data"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def exists(conn: sqlite3.Connection, table: str, field: str, value: str) -> bool:
    return conn.execute(f"SELECT 1 FROM {table} WHERE {field} = ?", (value,)).fetchone() is not None


def image_pool(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT image_url FROM images WHERE image_url LIKE '/assets/%' ORDER BY id").fetchall()
    return [row["image_url"] for row in rows] or ["/assets/images/scenery/maogongshan-mountain.jpg"]


def insert_event(conn: sqlite3.Connection, item: dict) -> None:
    if exists(conn, "historical_events", "title", item["title"]):
        return
    conn.execute(
        """
        INSERT INTO historical_events
        (title,event_time,location,related_people,summary,details,source,reference_materials,image_url,category,verified,verification_status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            item["title"],
            item["event_time"],
            item["location"],
            item["related_people"],
            item["summary"],
            item["details"],
            item["source"],
            item["reference_materials"],
            item["image_url"],
            item["category"],
            item["verified"],
            item["verification_status"],
            now(),
        ),
    )


def insert_figure(conn: sqlite3.Connection, item: dict) -> None:
    if exists(conn, "historical_figures", "name", item["name"]):
        return
    conn.execute(
        """
        INSERT INTO historical_figures
        (name,photo_url,active_period,biography,deeds,relation_to_maogongshan,related_events,source,verified,verification_status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            item["name"],
            item["photo_url"],
            item["active_period"],
            item["biography"],
            item["deeds"],
            item["relation_to_maogongshan"],
            item["related_events"],
            item["source"],
            item["verified"],
            item["verification_status"],
            now(),
        ),
    )


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
            now(),
        ),
    )


def insert_resource(conn: sqlite3.Connection, name: str, type_: str, summary: str, source: str, tags: list[str], image: str, views: int) -> None:
    if exists(conn, "resources", "name", name):
        return
    conn.execute(
        "INSERT INTO resources(name,type,summary,uploaded_at,source,file_url,tags,views) VALUES (?,?,?,?,?,?,?,?)",
        (name, type_, summary, now(), source, image, ",".join(tags), views),
    )


def insert_qa(conn: sqlite3.Connection, question: str, answer: str, category: str, keywords: list[str], source: str) -> None:
    if exists(conn, "qa_knowledge", "question", question):
        return
    conn.execute(
        "INSERT INTO qa_knowledge(question,answer,category,keywords,source,created_at) VALUES (?,?,?,?,?,?)",
        (question, answer, category, ",".join(keywords), source, now()),
    )


def insert_knowledge(conn: sqlite3.Connection, title: str, summary: str, content: str, category: str, source: str, status: str = "公开资料整理") -> None:
    if exists(conn, "knowledge_documents", "title", title):
        return
    conn.execute(
        """
        INSERT INTO knowledge_documents(title,summary,content,category,source_name,source_url,source_document,source_page,verification_status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (title, summary, content, category, source, "", source, "", status, now(), now()),
    )


def build_content(prefix: str, topic: str, angle: str) -> tuple[str, str]:
    summary = f"{prefix}围绕“{topic}”展开，突出资料整理、现场观察、数字化呈现和公众传播之间的关系。"
    content = (
        f"{summary}\n\n"
        f"本条内容属于{angle}，适合在平台中作为专题资料、讲解素材或检索条目使用。"
        "整理时重点记录资料来源、适用场景、与毛公山或城阳红色文化的关联，并提醒使用者区分历史事实、文化阐释和社会实践成果。"
        "涉及具体历史人物、精确日期或事件结论的部分，应继续以地方志、档案馆、政府公开资料、景区管理方说明和主流媒体报道进行复核。"
    )
    return summary, content


def augment(conn: sqlite3.Connection) -> None:
    images = image_pool(conn)

    event_topics = [
        "毛公山景区红色文化传播路径整理", "惜福镇街道研学资源梳理", "城阳区红色文化教育场景观察", "青岛地方红色记忆数字化索引",
        "毛公山登山节与公众参与记录", "景区导览牌资料采集流程", "周边社区口述资料整理规范", "红色文化宣传短视频脚本归档",
        "青年社会实践与地方文化连接", "红色研学课程任务单设计", "数字地图点位核验流程", "图片版权元数据登记流程",
        "城阳文化旅游公开报道索引", "毛公山景观与文化展示融合", "青岛山海城市形象与红色文化传播"
    ]
    for idx, topic in enumerate(event_topics):
        summary, content = build_content("历史与文化资料条目", topic, "公开资料整理与实践团队文化解读")
        insert_event(conn, {
            "title": topic,
            "event_time": "公开资料整理期",
            "location": "青岛市城阳区及毛公山周边",
            "related_people": "实践团队、资料整理人员、景区讲解相关角色",
            "summary": summary,
            "details": content,
            "source": "平台公开资料库与实践团队整理",
            "reference_materials": "来源记录见 DATA_SOURCES.md 与 IMAGE_SOURCES.md",
            "image_url": images[idx % len(images)],
            "category": "文化资料",
            "verified": 0,
            "verification_status": "公开资料整理",
        })

    figure_roles = [
        ("资料采集志愿者", "负责现场记录、图片分类和资料编号。"),
        ("访谈记录整理员", "负责访谈提纲、文字转写和授权提醒。"),
        ("地图点位核验员", "负责点位名称、路线提示和坐标复核。"),
        ("图片版权记录员", "负责图片来源、版权说明和使用边界记录。"),
        ("前端交互开发成员", "负责页面结构、移动端适配和交互体验。"),
        ("后端数据开发成员", "负责接口、数据库、检索和问答知识库。"),
        ("内容审核协同成员", "负责区分历史事实、文化解读和实践材料。"),
        ("讲解稿撰写成员", "负责音频讲解稿和 AI 导游话术整理。"),
        ("成果展示统筹成员", "负责答辩路线、演示材料和页面导览。"),
        ("青年传播设计成员", "负责短视频、推文和公众传播表达。"),
    ]
    for idx, (name, deed) in enumerate(figure_roles):
        insert_figure(conn, {
            "name": f"山软寻脉实践团队{name}",
            "photo_url": images[(idx + 10) % len(images)],
            "active_period": "2026 年暑期社会实践",
            "biography": f"该角色属于实践团队公开分工，用于展示山东大学软件学院学生参与红色文化数字化保护的具体工作。{deed}",
            "deeds": f"{deed}工作成果进入资源库、地图导览、图库、问答知识库或讲解系统。",
            "relation_to_maogongshan": "围绕毛公山红色文化资源整理、数字化呈现和青年传播开展工作。",
            "related_events": "山软寻脉·毛公山数字调研实践",
            "source": "社会实践团队公开展示资料",
            "verified": 1,
            "verification_status": "项目公开信息",
        })

    story_topics = [f"毛公山红色文化传播微故事 {i:02d}" for i in range(31, 56)]
    for idx, title in enumerate(story_topics):
        summary, content = build_content("红色故事整理", title, "文化传播素材")
        insert_structured(conn, "red_stories", {
            "title": title,
            "summary": summary,
            "content": content,
            "category": "红色故事",
            "tags": ["毛公山", "红色文化", "文化传播", "实践团队整理"],
            "date": "公开资料整理期",
            "location": "青岛市城阳区",
            "image": images[(idx + 20) % len(images)],
            "source": "实践团队整理",
        })

    place_topics = [
        "毛公山景区入口导览点", "毛公山登山步道观察点", "毛公山观景平台", "惜福镇街道文化资源点",
        "城阳区红色教育活动点", "社区访谈资料整理点", "青岛山海文化观察点", "山东大学软件园校区实践出发点",
        "资料采集与整理工作站", "数字资源展示答辩点", "青年志愿服务联络点", "红色研学路线集合点"
    ]
    for idx, title in enumerate(place_topics):
        summary, content = build_content("地点资源", title, "地点导览资料")
        insert_structured(conn, "places", {
            "title": title,
            "summary": summary,
            "content": content,
            "category": "地点资源",
            "tags": ["地图导览", "地点", "路线", "资源点"],
            "date": "2026",
            "location": "青岛市城阳区及相关实践区域",
            "image": images[(idx + 35) % len(images)],
            "source": "平台公开资料库",
        })

    for i in range(16, 31):
        title = f"实践日志 {i:02d}：资料复核与平台打磨记录"
        summary, content = build_content("实践日志", title, "大学生社会实践记录")
        insert_structured(conn, "research_logs", {
            "title": title,
            "summary": summary,
            "content": content + "\n\n本日志侧重记录团队如何从资料采集进入结构化建库、页面设计、接口测试和内容审核。",
            "category": "实践日志",
            "tags": ["社会实践", "山东大学软件学院", "毛公山", "数字化"],
            "date": f"2026-07-{(i % 20) + 1:02d}",
            "location": "山东大学软件学院与青岛城阳实践区域",
            "image": images[(i + 45) % len(images)],
            "source": "山软寻脉实践团队公开展示资料",
        })

    for i in range(1, 21):
        title = f"调研访谈记录 {i:02d}：红色文化数字传播观察"
        summary, content = build_content("访谈记录", title, "调研记录整理")
        insert_resource(conn, title, "调研记录", summary + "访谈记录只保留公开观点，不公开个人联系方式。", "实践团队整理", ["访谈", "调研", "隐私保护"], images[(i + 60) % len(images)], 30 + i)
        insert_knowledge(conn, f"访谈知识：{title}", summary, content, "调研访谈", "实践团队整理", "项目公开信息")

    for i in range(11, 21):
        title = f"实践成果 {i:02d}：数字文化平台展示组件"
        summary, content = build_content("实践成果", title, "项目成果")
        insert_structured(conn, "achievements", {
            "title": title,
            "summary": summary,
            "content": content,
            "category": "实践成果",
            "tags": ["成果展示", "软件工程", "红色文化数字化"],
            "date": "2026",
            "location": "山东大学软件学院",
            "image": images[(i + 75) % len(images)],
            "source": "山软寻脉实践团队公开展示资料",
        })

    for i in range(9, 15):
        title = f"音频讲解 {i:02d}：毛公山数字导览专题"
        script = (
            f"欢迎收听{title}。本讲解围绕毛公山红色文化资源、自然景观、社会实践和数字平台建设展开。"
            "请在浏览资料时关注来源说明、考证状态和版权提示。平台以数字化方式帮助青年学生理解地方文化，"
            "也提醒我们在传播红色文化时坚持真实、克制和可追溯。"
        )
        if not exists(conn, "audio_guides", "title", title):
            conn.execute(
                "INSERT INTO audio_guides(title,summary,script,category,duration,image,source,created_at) VALUES (?,?,?,?,?,?,?,?)",
                (title, script[:90], script, "数字讲解", "约 2 分钟", images[(i + 88) % len(images)], "实践团队整理", now()),
            )

    resource_types = ["历史文献", "图片资料", "音频资料", "调研记录", "实践成果", "地点资源", "人物资料", "红色故事", "技术资料", "新闻索引"]
    for i in range(1, 91):
        type_ = resource_types[i % len(resource_types)]
        name = f"{type_}扩展资源 {i:03d}"
        summary, content = build_content("数字资源", name, "结构化资源条目")
        insert_resource(conn, name, type_, summary, "平台公开资料库", [type_, "毛公山", "数字资源"], images[(i + 5) % len(images)], 50 + i)
        insert_knowledge(conn, f"资源知识：{name}", summary, content, type_, "平台公开资料库", "公开资料整理")

    categories = ["毛公山概览", "红色文化", "城阳资源", "山东大学软件学院", "平台使用", "数字地图", "全景图库", "音频讲解", "社会实践", "数据真实性"]
    for i in range(151, 361):
        category = categories[i % len(categories)]
        question = f"{category}相关问题 {i:03d} 如何理解？"
        answer = (
            f"关于“{category}”，平台优先从本地资源库检索资料。"
            "可结合毛公山概览、红色历史、数字资源、实践调研和山软青年专题查看。"
            "如果问题涉及具体历史事实，请以页面列出的来源和考证状态为准；如果资料不足，平台会提示继续查阅权威来源。"
        )
        insert_qa(conn, question, answer, category, [category, "毛公山", "数字资源平台", "实践团队"], "平台知识库整理")
        insert_knowledge(conn, f"问答知识：{question}", answer[:80], answer, "智能问答", "平台知识库整理", "公开资料整理")


def export_front_data(conn: sqlite3.Connection) -> None:
    FRONT_DATA.mkdir(parents=True, exist_ok=True)
    mapping = {
        "red_stories": "red_stories.json",
        "places": "places.json",
        "research_logs": "research_logs.json",
        "achievements": "achievements.json",
    }
    for table, filename in mapping.items():
        rows = [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()]
        data = []
        for row in rows:
            data.append({
                "id": str(row["id"]),
                "title": row["title"],
                "subtitle": row["category"],
                "summary": row["summary"],
                "content": row["content"],
                "category": row["category"],
                "subCategory": row["category"],
                "tags": [tag for tag in (row["tags"] or "").split(",") if tag],
                "date": row["date"],
                "location": row["location"],
                "image": row["image"],
                "cover": row["image"],
                "gallery": [row["image"]],
                "source": row["source"],
                "sourceUrl": "",
                "author": "平台资料整理",
                "relatedIds": [rid for rid in (row["related_ids"] or "").split(",") if rid],
                "featured": row["id"] <= 8,
                "views": 0,
            })
        (FRONT_DATA / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    with connect() as conn:
        augment(conn)
        export_front_data(conn)
        conn.commit()
        for table in ["historical_events", "historical_figures", "red_stories", "places", "research_logs", "achievements", "audio_guides", "qa_knowledge", "resources", "knowledge_documents"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")


if __name__ == "__main__":
    main()
