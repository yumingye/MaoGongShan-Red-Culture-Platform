"""同步可公开展示的实践团队成员信息。

脚本只保存姓名、学院、团队角色和工作分工，不包含身份证号、手机号、
私人邮箱、家庭所在地等敏感信息。可重复执行，按姓名更新而不重复插入。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

try:
    from .config import DB_PATH
except ImportError:
    from config import DB_PATH


SOURCE_TITLE = "用户提供的团队组成情况截图"
SOURCE_TYPE = "项目团队材料"
SOURCE_PAGE = "团队组成情况"
SOURCE_NOTE = (
    "依据团队组成材料整理姓名、学院、团队角色和工作分工。"
)
VERIFICATION_STATUS = "依据项目材料核对"

TEAM_MEMBERS = [
    {
        "name": "于茗烨",
        "college": "山东大学软件学院",
        "role": "队长、项目负责人",
        "responsibility": "负责项目总体统筹、活动组织协调、对外联络及调研报告审核。",
        "public_bio": "统筹团队实践安排与平台建设进度，协调资料整理、调研实施和成果呈现。",
    },
    {
        "name": "张金烨",
        "college": "山东大学材料科学与工程学院",
        "role": "副队长、实践组织",
        "responsibility": "协助队长开展实践活动，负责行程安排与现场组织。",
        "public_bio": "参与实践流程设计与执行协调，保障实地调研和团队活动有序开展。",
    },
    {
        "name": "陈序文",
        "college": "山东大学软件学院",
        "role": "技术负责人",
        "responsibility": "负责数字化资料整理、数据分析及成果展示制作。",
        "public_bio": "运用软件工程和数据处理方法，参与数字资源整理、分析与平台成果呈现。",
    },
    {
        "name": "凌健鑫",
        "college": "山东大学软件学院",
        "role": "调研负责人",
        "responsibility": "负责调研设计、问卷编制、访谈开展及调研数据整理。",
        "public_bio": "围绕毛公山文化资源设计调研流程，组织访谈和问卷资料的规范整理。",
    },
    {
        "name": "朴珍燮",
        "college": "山东大学低空科学与工程学院",
        "role": "宣传负责人",
        "responsibility": "负责摄影摄像、新闻稿撰写及新媒体运营。",
        "public_bio": "记录团队实践过程，整理图文影像资料并参与项目宣传内容制作。",
    },
    {
        "name": "赵乐镕",
        "college": "山东大学软件学院",
        "role": "后勤与安全负责人",
        "responsibility": "负责物资采购、经费管理、安全保障及签到统计。",
        "public_bio": "承担实践活动的物资、经费与安全保障工作，为团队现场执行提供支持。",
    },
]


def sync_team_members(database_path=DB_PATH) -> tuple[int, int]:
    """按姓名更新或插入公开成员记录，返回（新增数，更新数）。"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0
    updated = 0
    with sqlite3.connect(database_path) as conn:
        for member in TEAM_MEMBERS:
            cursor = conn.execute(
                """
                UPDATE team_members
                SET college = ?, role = ?, responsibility = ?, public_bio = ?,
                    source_title = ?, source_type = ?, source_page = ?,
                    source_note = ?, verification_status = ?, updated_at = ?
                WHERE name = ?
                """,
                (
                    member["college"],
                    member["role"],
                    member["responsibility"],
                    member["public_bio"],
                    SOURCE_TITLE,
                    SOURCE_TYPE,
                    SOURCE_PAGE,
                    SOURCE_NOTE,
                    VERIFICATION_STATUS,
                    now,
                    member["name"],
                ),
            )
            if cursor.rowcount:
                updated += 1
                continue

            conn.execute(
                """
                INSERT INTO team_members (
                    name, college, role, responsibility, public_bio,
                    source_title, source_type, source_page, source_note,
                    verification_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    member["name"],
                    member["college"],
                    member["role"],
                    member["responsibility"],
                    member["public_bio"],
                    SOURCE_TITLE,
                    SOURCE_TYPE,
                    SOURCE_PAGE,
                    SOURCE_NOTE,
                    VERIFICATION_STATUS,
                    now,
                    now,
                ),
            )
            inserted += 1
        conn.commit()
    return inserted, updated


if __name__ == "__main__":
    added, changed = sync_team_members()
    print(f"团队成员同步完成：新增 {added} 条，更新 {changed} 条。")
