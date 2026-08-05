from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / "database" / "maogongshan.db"


SPOTS = [
    (
        "毛公山观景平台",
        "观景点",
        "用于展示山体轮廓、周边村落与城阳山地景观的观景节点，适合设置摄影与讲解停留点。",
        36.283,
        120.502,
        "示意坐标，实地参观请以景区标识和地图平台为准。",
        "/assets/images/maogongshan/resource-018.jpg",
        "项目资源库整理",
        "待坐标复核",
        "青岛市城阳区惜福镇街道毛公山景区",
        "观景点",
    ),
    (
        "毛公山入口服务点",
        "服务设施",
        "面向游客集散、路线咨询和导览说明的入口服务节点，可承接停车、问询和安全提醒内容。",
        36.280,
        120.499,
        "示意坐标，建议以高德地图实时导航为准。",
        "/assets/images/scenery/maogongshan-mountain.jpg",
        "项目资源库整理",
        "待坐标复核",
        "青岛市城阳区惜福镇街道毛公山景区周边",
        "服务设施",
    ),
    (
        "红色文化讲解停留点",
        "红色文化资源点",
        "适合开展红色文化主题讲解、团队合影、研学活动记录与数字资源采集的停留点。",
        36.282,
        120.500,
        "示意坐标，正式发布前需实地复核。",
        "/assets/images/culture/maogongshan-red-park-2022.jpg",
        "项目资源库整理",
        "待坐标复核",
        "毛公山红色文旅景观区",
        "红色文化资源点",
    ),
    (
        "登山步道中段",
        "登山路线",
        "登山步道中段可用于展示坡度变化、植被环境和分段游览建议。",
        36.284,
        120.504,
        "示意坐标，建议结合景区步道标识使用。",
        "/assets/images/route/maogongshan-park-route-2022.jpg",
        "项目资源库整理",
        "待坐标复核",
        "毛公山登山步道",
        "登山路线",
    ),
    (
        "自然植被观察点",
        "自然景观",
        "用于展示毛公山山地植被、季节变化与生态环境的自然观察点。",
        36.285,
        120.505,
        "示意坐标，正式发布前需实地复核。",
        "/assets/images/scenery/xifu-autumn.jpg",
        "项目资源库整理",
        "待坐标复核",
        "毛公山自然景观区域",
        "自然景观",
    ),
    (
        "实践调研集合点",
        "实践调研点",
        "适合展示实践团队集合、任务分工、访谈准备和资料采集流程的调研组织点。",
        36.279,
        120.498,
        "示意坐标，团队活动应以实际集合通知为准。",
        "/assets/images/activity/xifu-grape-harvest.jpg",
        "山软寻脉实践团队整理",
        "实践整理",
        "青峰社区及毛公山周边",
        "实践调研点",
    ),
    (
        "周边文旅联动点",
        "周边景点",
        "用于连接惜福镇、青峰社区和周边文旅资源，展示毛公山与区域文化旅游的联动关系。",
        36.276,
        120.496,
        "示意坐标，周边游览请以公开地图为准。",
        "/assets/images/culture/xifu-cultural-tourism.jpg",
        "项目资源库整理",
        "待坐标复核",
        "惜福镇街道周边",
        "周边景点",
    ),
    (
        "公共交通提示点",
        "服务设施",
        "用于提示游客结合公交、网约车和步行路线前往毛公山，避免把示意路线当成实时交通方案。",
        36.277,
        120.497,
        "示意坐标，实时交通请使用地图平台。",
        "/assets/images/commons/qingdao-02-jpg.jpg",
        "项目资源库整理",
        "待坐标复核",
        "毛公山周边交通节点",
        "服务设施",
    ),
]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM scenic_spots WHERE name LIKE '%?%' OR type LIKE '%?%' OR category LIKE '%?%'")
    for row in SPOTS:
        exists = cur.execute("SELECT id FROM scenic_spots WHERE name=?", (row[0],)).fetchone()
        if exists:
            cur.execute(
                """
                UPDATE scenic_spots SET type=?, description=?, latitude=?, longitude=?, route_hint=?,
                image_url=?, source=?, verification_status=?, address=?, category=? WHERE name=?
                """,
                row[1:] + (row[0],),
            )
        else:
            cur.execute(
                """
                INSERT INTO scenic_spots(name,type,description,latitude,longitude,route_hint,image_url,source,verification_status,address,category)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                row,
            )
    conn.commit()
    print(cur.execute("SELECT COUNT(*) FROM scenic_spots").fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()
