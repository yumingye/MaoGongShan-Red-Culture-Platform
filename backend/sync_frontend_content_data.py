"""清理前端离线数据中的编号模板，生成可独立阅读的备用内容。"""

from __future__ import annotations

import json
from pathlib import Path

try:
    from .editorial_catalog import (
        ACHIEVEMENT_RESOURCE_TITLES,
        LATER_LOGS,
        PLACE_TITLES,
        RED_STORY_TITLES,
    )
except ImportError:
    from editorial_catalog import ACHIEVEMENT_RESOURCE_TITLES, LATER_LOGS, PLACE_TITLES, RED_STORY_TITLES


DATA_DIR = Path(__file__).resolve().parents[1] / "frontend" / "src" / "data"

ACHIEVEMENT_TITLES = ACHIEVEMENT_RESOURCE_TITLES + [
    "本地图片资源分类与压缩", "媒体加载失败统一兜底", "前后端接口与健康检查",
    "Windows 一键启动与停止脚本", "图片来源与版权说明文档", "内容完整性自动审查",
    "毛公山文化问答知识库", "调研计划与日志时间轴", "跨学院团队协作档案", "公网部署配置与运行说明",
]

PLACE_EXTRA = [
    "城阳区山地文化扩展索引", "青岛红色文化学习索引", "山东红色文化扩展索引", "山东大学软件园校区实践起点",
    "资料整理与开发工作区", "团队成果展示与答辩区", "历史图片来源核验点", "人物照片来源核验点",
    "音频讲解内容关联点", "智能问答知识关联点", "实践成果归档点", "公众阅读反馈观察点",
]

STORY_EXTRA = [
    "五四运动与青年觉醒的学习线索", "中国共产党成立的历史起点", "南昌起义与人民军队创建",
    "秋收起义后的道路探索", "井冈山革命根据地的实践启示", "古田会议与政治建军",
    "红军长征中的理想与纪律", "遵义会议与独立自主", "全民族抗战中的共同意志",
    "延安时期的作风与学习", "西柏坡时期的清醒与担当", "新中国成立与人民新生活",
    "抗美援朝中的家国担当", "改革开放中的实践品格", "伟大建党精神的青年阅读",
    "沂蒙精神中的党群深情", "雷锋精神与平凡岗位", "焦裕禄精神与调查研究",
    "两弹一星精神与科技报国", "科学家精神与长期主义", "劳模精神与劳动价值",
    "工匠精神与质量意识", "脱贫攻坚精神与精准务实", "抗疫精神与共同责任", "新时代青年的数字文化使命",
]

LOG_TITLES = [
    "从一张资料清单开始", "把研究问题写在功能之前", "访谈提纲的第一次修改", "为实地观察制作任务单",
    "镜头清单与影像命名", "现场信息与网络资料对照", "从照片文件夹到资源表", "数据库字段的反复推敲",
    "前后端第一次完整联调", "让搜索结果真正可用", "地图失效时页面还能做什么", "智能问答的证据边界",
    "移动端逐页找错", "一次内容与图片复核", "从答辩作品走向可维护项目",
] + [item[0] for item in LATER_LOGS[:15]]

ACHIEVEMENT_NOTES = [
    "答辩展示时，团队从用户需求、资料依据和测试结果三个角度说明完成情况，不用功能名称代替真实成果。",
    "成果文件同时保留运行说明、数据结构与复核记录，使展示结束后仍能继续维护，而不是成为一次性的页面截图。",
    "团队把稳定性、可追溯性和公众阅读体验作为验收条件，逐项核对页面、接口、媒体资源与文字说明。",
    "形成成果的过程也被纳入归档：哪些内容来自公开资料、哪些来自团队观察、哪些属于技术实现，均在页面中明确区分。",
    "这项成果回应了社会实践中的具体问题，并通过可运行页面、结构化数据或检查脚本留下能够复查的证据。",
]

PLACE_NOTES = [
    "若该点位属于方法或资料索引，它表示调研工作中的信息节点，不等同于景区正式设施或精确地理坐标。",
    "现场到访前仍需核对当日开放、交通和天气信息；平台的静态说明用于规划阅读与观察任务，不替代实时导航。",
    "点位详情强调可确认的空间关系，不为未核实的建筑、人物或活动补写具体名称，避免数字导览造成误导。",
    "研学使用时可围绕环境观察、信息记录和文明游览设置任务，并在返程后把现场笔记与公开资料再次对照。",
    "该条目既服务地图列表，也连接图片、日志和来源记录，使地点不再只是一个标记，而成为理解资料的入口。",
]

STORY_NOTES = [
    "延伸阅读时，读者可继续查看事件详情、人物档案和来源页面，在历史条件中理解精神内涵，避免用今天的想象替代当时的事实。",
    "平台把史实、文化解读和实践感悟分别标注：事实以公开资料为依据，感悟只代表青年团队在学习过程中的认识。",
    "阅读这一主题需要回到具体的人、事与时代环境。只有把选择放在真实处境中考察，精神价值才不会变成抽象口号。",
    "数字整理不是为故事增加传奇色彩，而是把来源、时间、地点和相关人物清楚连接，让读者能够继续查证和比较。",
    "当资料之间存在表述差异时，页面优先呈现可核对内容并保留来源入口，不以顺畅叙事掩盖尚待核实的问题。",
]


def write_records(filename: str, titles: list[str], kind: str) -> int:
    path = DATA_DIR / filename
    records = json.loads(path.read_text(encoding="utf-8"))
    for index, (record, title) in enumerate(zip(records, titles), 1):
        if kind == "实践成果":
            summary = (
                f"{title}是山软寻脉实践团队在资料整理、实地调研与平台开发过程中形成的具体成果，"
                "记录了任务目标、实施方法与复核结果。"
            )
            content = (
                f"成果概述\n{summary}\n\n形成过程\n团队从真实使用场景出发，把任务拆分为资料收集、来源登记、数据建模、界面实现和测试复核。"
                "每个环节都保留可追溯记录，使成果不仅适合答辩展示，也能被下一位维护者理解。\n\n实践价值\n"
                "这项成果体现山东大学软件学院学生以专业能力服务地方文化传播的尝试。技术不是装饰，而是帮助资料被准确保存、清晰检索和稳定呈现的方法。\n\n"
                f"成果复核\n{ACHIEVEMENT_NOTES[(index - 1) % len(ACHIEVEMENT_NOTES)]}"
            )
        elif kind == "地点资源":
            summary = f"{title}用于组织平台中的空间信息、观察任务与关联阅读，帮助访问者理解地点在调研和导览中的作用。"
            content = (
                f"点位说明\n{summary}\n\n观察方式\n页面以公开信息和团队调研任务为基础，说明点位功能、可观察内容与使用边界。"
                "不具备权威坐标或实时交通依据的内容，仅作为数字导览和研学组织参考。\n\n阅读提示\n"
                "访问者可以从该点位继续进入风景图片、路线说明、实践日志与来源记录，在空间线索中理解毛公山文化资源。"
                f"\n\n使用边界\n{PLACE_NOTES[(index - 1) % len(PLACE_NOTES)]}"
            )
        elif kind == "红色故事":
            summary = f"{title}从青年学习与数字整理视角展开，关注可靠资料、历史语境和当代传承之间的联系。"
            content = (
                f"内容导语\n{summary}\n\n阅读线索\n平台把这一主题放在公开党史资料与红色文化教育语境中理解，"
                "重点关注事件为何发生、人物作出怎样的选择、精神价值如何在具体实践中形成。\n\n青年启示\n"
                "对今天的大学生而言，学习红色文化不应停留在口号复述。我们更需要尊重证据、理解历史条件，并把责任落实到认真完成每一项学习和实践任务之中。"
                f"\n\n延伸阅读\n{STORY_NOTES[(index - 1) % len(STORY_NOTES)]}"
            )
        else:
            summary = f"{title}记录团队把专业学习带入毛公山数字调研的一次具体行动，呈现问题、选择与复盘。"
            content = (
                f"实践记录\n{summary}\n\n工作过程\n团队在推进任务时同步记录资料来源、协作分工和测试结果，"
                "不以页面数量代替内容质量，也不把未经确认的现场印象写成历史结论。\n\n青年感悟\n"
                "一次认真校对、一次耐心沟通和一次失败后的重新测试，都是社会实践真正发生的地方。"
                "我们希望用软件工程训练提升文化资源的可读性，也在真实问题中理解技术工作应有的责任。"
            )
        record["title"] = title
        record["subtitle"] = kind
        record["summary"] = summary
        record["content"] = content
        record["category"] = kind
        record["tags"] = ["毛公山", kind, "青年实践", "数字文化"]
        record["imageDescription"] = (
            f"配图用于呈现“{title}”所在的{kind}主题，图片内容与来源以详情页登记信息为准，"
            "不据此推断未标明的人物、日期或历史事件。"
        )
        record["author"] = "山软寻脉·毛公山数字调研实践团"
        record["source"] = "实践团队公开展示文稿与平台资料整理"
        record["relatedItems"] = record.get("relatedIds") or []
        record["featured"] = index <= 6
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(records)


def main() -> None:
    totals = {
        "achievements.json": write_records("achievements.json", ACHIEVEMENT_TITLES, "实践成果"),
        "places.json": write_records("places.json", PLACE_TITLES + PLACE_EXTRA, "地点资源"),
        "red_stories.json": write_records("red_stories.json", RED_STORY_TITLES + STORY_EXTRA, "红色故事"),
        "research_logs.json": write_records("research_logs.json", LOG_TITLES, "实践日志"),
    }
    print("前端离线内容同步完成：" + "，".join(f"{name} {count} 条" for name, count in totals.items()))


if __name__ == "__main__":
    main()
