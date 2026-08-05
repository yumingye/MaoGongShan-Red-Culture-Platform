"""补充视频资料入口，并清理 PowerShell 管道造成的问号脏数据。

本脚本可重复执行：按资源名称去重，不会重复插入同名记录。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / "database" / "maogongshan.db"


VIDEO_RESOURCES = [
    (
        "毛公山红色文化数字资源库宣传片脚本",
        "围绕平台首页、地图导览、全景图库、智能问答和山软青年专题设计的宣传短视频脚本，用于展示数字化保护红色文化资源的技术路径。",
        "实践团队整理",
        "/resources/category/video-script-maogongshan-platform",
        "短视频,项目成果,数字资源库",
    ),
    (
        "毛公山风光与登山路线短视频分镜",
        "以山体远景、登山步道、观景点、周边自然环境和地图路线为主线组织的短视频分镜资料，适合社会实践成果汇报使用。",
        "实践团队整理",
        "/resources/category/video-storyboard-route",
        "毛公山,登山路线,短视频",
    ),
    (
        "红色文化数字讲解视频提纲",
        "围绕毛公山红色文化价值、青岛城阳扩展资源、资料来源说明和考证边界形成的视频讲解提纲。",
        "实践团队整理",
        "/guide",
        "红色文化,讲解视频,资料来源",
    ),
    (
        "山软青年社会实践纪实视频方案",
        "记录山东大学软件学院学生资料查阅、实地调研、数据整理、前端开发、后端接口和答辩准备过程的视频方案。",
        "实践团队整理",
        "/school/topic/development",
        "山东大学软件学院,社会实践,开发过程",
    ),
    (
        "数字地图导览演示录屏方案",
        "用于录制地图点位筛选、静态地图降级、地点详情联动和调研路线展示的演示视频方案。",
        "实践团队整理",
        "/map",
        "数字地图,路线导览,演示录屏",
    ),
    (
        "智能问答功能演示视频方案",
        "用于展示本地检索式问答如何回答毛公山位置、资源查询、项目团队、数据来源和考证状态等问题。",
        "实践团队整理",
        "/chat",
        "智能问答,知识库,演示视频",
    ),
    (
        "全景图库浏览演示视频方案",
        "展示图片瀑布流、分类筛选、图片详情、来源说明和版权提示的录屏脚本。",
        "实践团队整理",
        "/scenery",
        "全景图库,图片来源,版权说明",
    ),
    (
        "成果答辩系统走查视频提纲",
        "按照首页、概览、历史、资源库、实践调研、山软青年、地图、问答、音频和三维沙盘顺序组织的答辩演示提纲。",
        "实践团队整理",
        "/help",
        "答辩演示,系统走查,项目成果",
    ),
]


def main() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM resources WHERE name LIKE '%?%' OR type LIKE '%?%'")
        for name, summary, source, file_url, tags in VIDEO_RESOURCES:
            exists = conn.execute("SELECT id FROM resources WHERE name=?", (name,)).fetchone()
            if exists:
                conn.execute(
                    "UPDATE resources SET type=?, summary=?, source=?, file_url=?, tags=? WHERE name=?",
                    ("视频资料", summary, source, file_url, tags, name),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO resources(name, type, summary, uploaded_at, source, file_url, tags, views)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (name, "视频资料", summary, now, source, file_url, tags),
                )
        count = conn.execute("SELECT COUNT(*) FROM resources WHERE type='视频资料'").fetchone()[0]
    print(f"视频资料数量：{count}")


if __name__ == "__main__":
    main()
