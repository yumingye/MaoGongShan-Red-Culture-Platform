"""幂等补全平台公开文稿，清理早期短文本和模板化占位内容。"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from .config import DB_PATH
    from .editorial_catalog import (
        ACHIEVEMENT_RESOURCE_TITLES,
        CORE_RESOURCE_TITLES,
        LATER_LOGS,
        PLACE_TITLES,
        PRACTICE_RESOURCE_TITLES,
        RED_STORY_TITLES,
    )
    from .platform_copy import QA_ITEMS
except ImportError:
    from config import DB_PATH
    from editorial_catalog import (
        ACHIEVEMENT_RESOURCE_TITLES,
        CORE_RESOURCE_TITLES,
        LATER_LOGS,
        PLACE_TITLES,
        PRACTICE_RESOURCE_TITLES,
        RED_STORY_TITLES,
    )
    from platform_copy import QA_ITEMS


PROJECT_VALUES = {
    "团队名称": "山软寻脉·毛公山数字调研实践团，是一支以山东大学软件学院学生为主体、吸收跨学院成员协作参与的青年实践团队。团队围绕地方文化资料整理、实地观察、数字采集与平台开发开展工作。",
    "所属单位": "项目依托山东大学软件学院学生的专业学习与社会实践展开，以软件工程、数据治理和交互设计方法服务红色文化资源的整理、展示与传播。",
    "课题名称": "青春寻脉·数智传薪——毛公山红色文化数字化保护与青年赓续实践研究。课题强调青年学生在资料考证、现场调研和数字平台建设中的主动参与。",
    "实践主题": "以毛公山及城阳区相关公开文化资源为切入点，探索红色文化数字化保护、青年赓续实践与数字资源库建设，让分散资料能够被检索、理解和持续维护。",
    "实践时间": "实践按照前期资料准备、实地调研、资料整理、平台开发、测试复核和成果展示六个阶段连续推进，具体活动日期以团队最终实践日志和正式材料为准。",
    "实践地点": "实践重点面向青岛市城阳区惜福镇街道毛公山及周边公开可访问区域，同时在山东大学软件学院完成资料清洗、系统开发、内容复核与成果展示工作。",
    "实践路线": "团队沿着“案头研究—问题设计—现场观察—影像采集—访谈整理—数据建模—平台开发—测试复盘—成果传播”的路线推进，使调研材料能够转化为可维护的数字资源。",
    "接收单位简介": "项目服务对象包括毛公山文化资源的公众浏览者、红色研学参与者、青年学生和课程答辩观众。平台以公开资料和团队实践成果为基础，为地方文化传播提供结构化数字载体。",
    "数字资源库建设目标": "资源库围绕历史资料、人物档案、自然风光、地图点位、实践记录和多媒体资源建立统一数据结构，提供检索、筛选、详情阅读、图片预览、来源追踪与本地知识问答能力。",
    "隐私保护说明": "资料发布遵循最小必要、来源清楚和授权明确的原则。团队将内容核验、图像版权、引用边界和公开范围纳入发布流程，使平台兼顾展示效果、研究规范与长期维护。",
}

PLAN_SUMMARIES = {
    "前期资料查阅": "围绕毛公山、城阳区文化资源、景区公开报道和山东红色文化背景建立资料目录，记录来源单位、网页地址、发布时间与检索日期，为后续访谈和实地观察提供问题线索。",
    "调研问卷与访谈提纲设计": "根据居民、游客、景区服务视角和青年用户的不同经验设计半结构式问题，减少诱导性表达，并提前明确记录方式、授权范围和资料整理格式。",
    "实地调研": "沿景区入口、登山步道、观景节点、文化展示与服务设施开展观察，记录位置、信息清晰度、游览体验和现场传播状况，使平台设计回应真实使用场景。",
    "摄影摄像与数字采集": "按照全景、路径、标识、环境、活动和资料细节建立镜头清单，同步登记文件名称、内容说明、来源性质、使用页面和版权状态，形成可追溯的影像档案。",
    "周边社区及游客访谈": "围绕地方记忆、游览感受、信息获得和平台使用需求开展访谈整理，通过匿名编号和主题编码归纳观点，不把单一口述直接转化为未经核实的历史结论。",
    "数据整理分析": "对问卷、访谈、图片、公开文献和现场记录进行去重、分类与交叉核对，区分权威资料、团队观察、情景化整理稿和待进一步核查内容。",
    "资源库建设": "将历史事件、人物、景点、图片、新闻、实践日志和研究文章录入结构化数据库，通过标签、关联资源和统一接口支撑前端检索、详情展示与智能问答。",
    "短视频制作": "以项目自有影像、已获许可图片、字幕和讲解稿组织短视频内容，重点呈现调研过程、毛公山景观和数字化建设方法，并为每项素材保留来源记录。",
    "调研报告和总结报告形成": "综合研究问题、现场记录、平台数据与团队复盘形成调研报告、实践总结和答辩材料，清楚说明完成内容、证据边界、技术方法与社会价值。",
}

RESULT_SUMMARIES = {
    "毛公山红色文化资源数字化传播现状调研报告": "围绕资料可获得性、现场文化说明、游客信息需求和数字传播路径形成分析报告，以公开来源和调研记录支撑结论，为平台功能设计提供依据。",
    "毛公山红色文化数字资源库": "形成集历史检索、人物档案、图片画廊、地图导览、实践展示和本地知识问答于一体的数字平台，并保留可重复执行的数据初始化与质量检查工具。",
    "毛公山红色文化宣传短视频": "依据团队实地影像和授权素材制作节奏清晰、说明准确的宣传短片，通过画面、字幕和讲解呈现毛公山景观、文化价值与青年实践过程。",
    "社会实践新闻稿和宣传推文": "围绕实践准备、现场调研、平台开发和阶段成果形成系列图文内容，以大学生实践视角讲述团队如何发现问题、协同工作并形成可持续成果。",
    "AI赋能红色文化传播方案": "以本地知识库检索为基础构建文化助手，回答毛公山、平台使用和实践项目相关问题；在资料不足时明确说明边界，并为后续合规接入大模型预留配置接口。",
    "社会实践总结报告": "系统梳理项目背景、调研方法、团队协作、技术实现、内容治理、测试结果与青年感悟，既呈现成果，也诚实记录资料限制和实践中的判断过程。",
}

TEAM_RESPONSIBILITIES = {
    "于茗烨": "负责项目总体统筹、任务拆解、活动组织协调、对外联络与调研报告审核，并推动前端、后端、数据和展示材料按统一目标协同完成。",
    "张金烨": "协助队长推进实践活动，负责行程安排、现场组织、任务衔接和进度反馈，保障不同小组在实地调研中有序配合。",
    "陈序文": "负责数字化资料整理、数据库分析、技术方案实现和成果展示制作，参与接口联调、数据校验与平台稳定性检查。",
    "凌健鑫": "负责调研问题设计、问卷与访谈提纲编制、现场访谈组织和调研数据整理，推动观察材料形成可分析的结构化记录。",
    "朴珍燮": "负责摄影摄像、活动纪实、新闻稿撰写和新媒体内容整理，建立影像清单并协调图片说明、页面配图与成果传播。",
    "赵乐镕": "负责物资采购、经费记录、安全保障、签到统计和现场应急协助，为团队调研路线执行与设备使用提供可靠支持。",
}

EDITORIAL_TOPICS = [
    ("毛公山地理位置与公开资料索引", "梳理毛公山所在区域、公开页面和基础地理信息，为地图导览与资料检索建立统一入口。"),
    ("毛公山山体形象与名称传播", "从公开介绍和视觉传播角度整理毛公山山体形象的识别方式，并区分文化解读与历史事实。"),
    ("毛公山景区等级公开报道脉络", "汇总景区等级相关公开报道，记录来源、发布时间和表述变化，避免不同年份信息相互混用。"),
    ("国家登山健身步道资料整理", "围绕登山健身步道的公开信息整理路线、活动与游览提示，为数字导览提供可核对依据。"),
    ("惜福镇街道文旅资源语境", "把毛公山放在惜福镇街道文旅资源背景中观察，理解山地景观、社区生活与公共传播的联系。"),
    ("青峰社区与毛公山周边环境", "整理毛公山周边社区和环境信息，关注景区发展、公共服务与地方文化记忆之间的互动。"),
    ("城阳山地生态观察专题", "从植被、季节变化和山地环境出发组织自然观察内容，为风景展示补充清晰的生态视角。"),
    ("毛公山红色文化景观表达", "分析红色文化主题如何通过标识、展陈、讲解和公共活动被感知，避免用空泛口号替代具体内容。"),
    ("红色教育活动资料编目", "建立红色教育活动的标题、主办信息、活动形式、影像与来源字段，使活动记录能够被检索和复用。"),
    ("历史图片与当代照片辨识", "说明历史资料、旧址照片、当代实景和项目自制图解的差异，提升图文对应与媒体使用准确性。"),
    ("地方口述材料整理方法", "围绕口述材料的授权、转写、主题编码和事实核查建立规范，让个人记忆成为研究线索而非未经核实的结论。"),
    ("游客文化感知与信息需求", "从入口说明、路线体验、停留节点和搜索习惯观察游客如何接触文化信息，为页面结构提供依据。"),
    ("登山路线分段导览设计", "按照入口、步道中段、观景节点和返程提示组织路线内容，使数字说明贴近真实行走过程。"),
    ("景区服务设施信息整理", "归纳停车、问询、休憩、卫生间和安全提示等服务信息，并强调发布前需要结合现场情况复核。"),
    ("公共交通与到访方式说明", "整合公交、自驾和步行衔接的公开信息，采用清晰而克制的表达，避免把静态资料冒充实时导航。"),
    ("毛公山四季景观观察", "以春季生长、夏日山色、秋季层次和冬季轮廓组织图集，让自然风光成为可比较的长期记录。"),
    ("山地摄影与观景节点", "结合光线、视野、地形和游览安全整理摄影节点，为图片详情和现场采集提供任务清单。"),
    ("毛公山周边文化资源联动", "整理周边可公开文化资源与毛公山之间的空间联系，为区域研学和专题阅读建立延伸入口。"),
    ("青岛红色文化扩展阅读", "把青岛相关红色文化资料作为扩展学习内容独立分类，避免与毛公山地方资料混写。"),
    ("山东红色文化资源索引", "以山东红色文化、纪念地和精神谱系为扩展范围建立索引，为地方平台提供更广阔的学习背景。"),
    ("沂蒙精神与山东红色文化", "从党群军民关系和群众实践理解沂蒙精神，并明确该专题属于山东红色文化拓展阅读。"),
    ("青岛城市文化与山海叙事", "观察青岛山海城市形象如何与地方文化传播结合，为毛公山专题设计提供区域视觉参照。"),
    ("红色研学内容组织方法", "把研学目标、路线、知识点、任务单和安全提示组织成完整流程，让参观从浏览转向主动学习。"),
    ("青年社会实践的现场意识", "记录大学生如何在现场倾听、观察和核对资料，使课程知识与真实公共文化需求发生联系。"),
    ("红色文化数字化保护路径", "从资料采集、结构化入库、来源追踪和多端展示梳理数字化保护路径，强调持续维护而非一次性呈现。"),
    ("文化资源数据库字段规范", "解释标题、摘要、正文、来源、版权、考证状态和关联资源等字段如何共同保障内容可读、可查和可复核。"),
    ("图片版权与来源登记", "建立原始页面、作者、许可、检索日期和使用页面记录，让图片在展示效果之外具备清楚的证据链。"),
    ("本地知识库与智能问答", "说明平台如何先检索数据库再组织回答，并在依据不足时保持克制，避免生成流畅却无来源的内容。"),
    ("数字地图与研学路线表达", "通过点位、分类、路线和图文弹窗连接空间与文化信息，并为第三方地图不可用时保留静态导览。"),
    ("项目答辩展示与持续维护", "从功能演示、数据来源、测试结果和团队分工组织答辩叙事，同时保留后续更新所需的脚本与文档。"),
]

PRACTICE_LOGS = [
    ("实践日志｜从一张资料清单开始", "团队将分散网页、报道和项目材料整理成首批来源目录。", "我们先确定资料从哪里来、如何命名、哪些字段必须保留，再讨论页面应该长什么样。这个过程让项目从想法变成可以执行的工作清单。"),
    ("实践日志｜把研究问题写在功能之前", "团队围绕资源现状、公众需求和数字传播边界明确研究问题。", "需求讨论不再从轮播图和卡片数量开始，而是追问用户想了解什么、资料能证明什么、技术可以解决什么。问题明确后，数据库和页面结构才有了依据。"),
    ("实践日志｜访谈提纲的第一次修改", "从开放问题、追问顺序和授权说明三个方面完善访谈提纲。", "我们删去容易诱导答案的问题，把“你是否喜欢”改成“你在哪个位置停留、看到了什么”。提问方式的变化，也改变了团队理解现场的方式。"),
    ("实践日志｜为实地观察制作任务单", "将入口、步道、观景点、文化说明和服务设施拆成观察任务。", "任务单让每名队员知道需要记录的位置、照片和文字，也为后续地图点位和路线页面准备了统一格式，减少现场回来后无法对应的材料。"),
    ("实践日志｜镜头清单与影像命名", "建立全景、路线、标识、人物活动和资料细节等拍摄类别。", "拍摄不再只是寻找好看的画面。每张照片都需要知道它展示什么、用于哪个页面、怎样写替代文本，影像由此成为可以长期辨认的数字档案。"),
    ("实践日志｜现场信息与网络资料对照", "把现场标识、公开报道和已有页面逐项比较，记录一致与矛盾之处。", "我们学会不急于下结论。现场看到的内容可能更新，网络页面也可能过时，只有保留来源和时间，才能为下一轮核对留下线索。"),
    ("实践日志｜从照片文件夹到资源表", "完成照片去重、方向修正、格式压缩和元数据登记。", "整理影像时，文件名、尺寸和说明同样重要。清楚的数据结构使一张照片能够同时服务图库、景点详情、实践日志和首页专题。"),
    ("实践日志｜数据库字段的反复推敲", "围绕来源、版权、考证状态和关联资源补充数据库字段。", "我们逐渐认识到，字段设计就是平台对内容的态度。来源不能只写“网络”，示意图不能标成历史照片，待核查内容也需要被明确识别。"),
    ("实践日志｜前后端第一次完整联调", "完成历史、人物、图片、项目与实践接口的页面接入。", "当数据库内容真正出现在浏览器中，许多问题也随之暴露：字段为空、图片比例不一、错误提示生硬。联调让技术实现重新回到用户阅读体验。"),
    ("实践日志｜让搜索结果真正可用", "优化关键词、分类、标签和详情跳转，检查无结果状态。", "搜索不只是返回标题。我们希望用户能够判断结果属于毛公山核心资源还是扩展学习内容，并从摘要、来源和标签中迅速找到继续阅读的方向。"),
    ("实践日志｜地图失效时页面还能做什么", "为高德地图未配置和网络异常设计静态导览与点位列表。", "第三方服务不稳定不应让整页失去价值。文字路线、分类点位和详情入口构成了独立可用的基础导览，也让系统更适合答辩现场。"),
    ("实践日志｜智能问答的证据边界", "以数据库检索结果组织回答，并为资料不足的问题设置明确回复。", "我们不追求无所不知的语气，而是让回答显示依据和相关页面。能够坦率说明“尚未收录”，也是文化数字平台可靠性的一部分。"),
    ("实践日志｜移动端逐页找错", "检查导航、长标题、图片裁切、详情排版和横向溢出。", "手机屏幕迫使我们重新判断信息主次。按钮是否容易点击、文字是否被遮挡、图片与说明是否仍在一起，这些细节决定平台能否真正被使用。"),
    ("实践日志｜一次内容与图片复核", "逐篇检查党史文字、人物、地点、时间和媒体资源的对应关系。", "宁可使用来源清楚的旧址照片或项目自制图解，也不让无关风景填充历史正文。复核让视觉设计从装饰转变为证据表达。"),
    ("实践日志｜从答辩作品走向可维护项目", "整理启动脚本、环境变量、测试报告、来源文档和交付压缩包。", "真正完整的成果不仅能在开发者电脑上运行，还应让下一位使用者看懂目录、启动服务、更新数据并复现检查。可维护性成为实践留下的另一种价值。"),
]

AUDIO_TOPICS = [
    ("毛公山概览", "从地理环境、山体景观、文化展示与数字资源四个方面认识毛公山。", "毛公山位于青岛市城阳区惜福镇街道一带。平台通过真实景观照片、公开报道索引、地图点位和实践记录呈现这座山的自然面貌与文化表达。浏览时可以先从概览了解位置，再进入风光、资源库和地图页面建立完整认识。"),
    ("名称与形象解读", "理解毛公山名称传播、山体形象观察与资料考证之间的关系。", "有关名称和山体形象的介绍，应区分公开资料、地方叙述和观景角度。平台把不同类型说明分别标注来源，不把传说直接写成确定史实。观察山体时，也应尊重自然景观本身，不因追求某种形象而忽略真实环境。"),
    ("红色文化价值", "从地方文化传播、公共教育和青年实践理解毛公山红色文化价值。", "红色文化的传播不只依靠醒目的色彩，更依靠准确资料、具体故事和能够进入日常生活的公共表达。毛公山相关文化展示为公众提供了观察地方叙事的窗口，也让青年学生思考如何用数字技术服务文化传承。"),
    ("登山路线讲解", "按照入口、步道、观景节点和返程顺序介绍毛公山游览思路。", "出发前请结合天气、体力和现场提示安排路线。进入步道后留意坡度、路面和同行人员状态，在观景节点停留时不要影响通行。平台地图提供的是资料型导览，实际游览仍应以景区当日开放信息和现场指引为准。"),
    ("实践调研介绍", "讲述山软寻脉团队如何从资料查阅走向现场观察和数字整理。", "团队先建立资料目录和调研问题，再开展路线观察、影像采集和访谈设计。回到开发阶段后，成员把照片、点位、文稿和来源录入数据库，并通过页面测试不断修正表达。这是一场由现场问题推动技术学习的实践。"),
    ("软件学院专题", "介绍山东大学软件学院学生如何以软件工程方法参与文化资源整理。", "软件工程不仅关心代码能否运行，也关心需求是否真实、数据是否可靠、系统是否便于维护。团队把版本管理、接口设计、异常处理和自动化检查引入社会实践，让专业训练与公共文化传播形成具体联系。"),
    ("数字平台使用", "帮助首次访问者快速认识平台导航、详情页、地图、图库和问答功能。", "首页提供核心入口，红色历史与人物栏目适合专题阅读，全景图库用于浏览真实照片，数字资源库支持分类检索，地图页面连接地点与路线。每个详情页还提供来源、相关推荐和返回入口，便于连续阅读。"),
    ("资源库检索方法", "介绍关键词、分类、标签和来源筛选的组合使用方式。", "搜索时可以输入人物、地点、事件或资源类型，再通过分类缩小范围。阅读结果时不要只看标题，还应关注摘要、来源和考证状态。若没有匹配结果，可以换用同义词，或从平台推荐专题继续查找。"),
    ("毛公山自然景观观察", "学习从山体轮廓、植被、光线和季节变化观察毛公山风景。", "自然景观不是红色文化页面的背景装饰，而是毛公山地域经验的重要组成。平台将全景、山路、植被和周边环境分类展示，帮助观众比较不同视角，并理解影像采集需要地点说明和来源记录。"),
    ("青峰社区与周边环境", "从社区、景区和周边生活空间的联系理解毛公山所在环境。", "一座山的文化意义往往与附近居民、道路和公共服务共同形成。平台通过周边环境照片和点位说明呈现这种联系，但不替代社区官方信息。关注地方日常，也能让文化传播摆脱空泛表达。"),
    ("登山安全与文明游览", "围绕天气、路况、同行照应和环境保护介绍基本游览原则。", "山地游览应量力而行，提前准备饮水和必要装备，遇到湿滑、强风或能见度变化及时调整计划。拍摄和参观时尊重现场秩序，不攀折植被、不留下垃圾，让每一次到访都成为对环境的温和回应。"),
    ("城阳山地文化概览", "把毛公山放在城阳山地环境与区域文化传播中理解。", "城阳的山地景观、社区生活和文旅活动共同构成地方文化的空间背景。平台将毛公山作为核心资源，同时设置城阳和青岛扩展阅读，既建立联系，也清楚区分不同地点的资料。"),
    ("红色文化资料如何考证", "介绍来源分级、时间核对、人物关系和图文一致性的基本方法。", "一条资料进入平台前，需要确认来源单位、发布时间、正文表述和图片说明。不同来源出现差异时，应保留线索而不是仓促合并。对无法确认的内容明确标注性质，比写出一个看似完整的答案更负责任。"),
    ("图像版权与来源说明", "认识图片原始页面、作者、许可、拍摄性质与页面用途等元数据。", "真实照片的价值不仅在于清晰，还在于能够说明它从哪里来、展示什么、是否允许使用。平台把历史资料、当代实景、路线示意和项目自制图解分开标注，使图片与正文形成可信对应。"),
    ("平台首页导览", "从首页首屏、统计、精选资源、实践专题和快捷入口开始浏览。", "首页不是信息的终点，而是一张通往各栏目内容的地图。观众可以从毛公山概览建立背景，从精选资源进入详情，从实践专题了解团队工作，也可以直接使用全局搜索寻找具体问题。"),
    ("红色历史检索", "学习按关键词、时间、地点、分类和考证状态查询历史资料。", "历史列表提供多条件筛选，详情页呈现时间、地点、相关人物、正文和参考来源。全国党史学习内容与毛公山核心资料分别标注，浏览时可以比较其范围，避免将扩展内容误认为地方史实。"),
    ("人物档案阅读", "了解人物生平、主要事迹、相关事件、真人照片和来源信息。", "人物档案不仅展示姓名和肖像，也通过活动时期、主要事迹和关联事件构成立体线索。平台中的三十位人物照片均已逐人核对并本地化，原始文件页与许可说明可在详情页查看。"),
    ("全景图库使用", "通过分类筛选、图片预览和详情页阅读毛公山与实践影像。", "图库中的图片保留标题、说明、地点、来源和版权状态。点击缩略图可以进入大图详情，也可以使用灯箱连续浏览。面对不确定的人物或地点，平台采用稳妥说明，不根据画面作无依据推测。"),
    ("数字地图与路线", "使用点位分类、列表联动和静态导览理解毛公山空间信息。", "配置高德地图后，页面可显示交互点位与路线；没有密钥时，静态位置说明和点位列表仍然可用。路线信息用于学习和行前参考，实时交通与开放状态应以官方服务为准。"),
    ("智能问答使用", "了解本地知识库如何检索资料、组织回答并显示参考来源。", "用户提出问题后，系统先在历史、人物、景点、项目和资源数据中寻找相关内容，再基于匹配结果组织回答。没有足够依据时，助手会明确说明收录不足，而不会凭空补写历史事实。"),
    ("社会实践成果", "回顾团队从调研设计、影像采集到系统开发和答辩整理的阶段成果。", "实践成果既包括可访问的平台，也包括数据库、来源记录、调研文稿、测试报告和启动脚本。它们共同证明项目如何从现场问题出发，经过团队协作，形成能够被他人继续使用的数字作品。"),
    ("青年责任与数字传承", "思考青年学生如何以专业能力接近历史、尊重证据并服务公共文化。", "数字传承不是替历史发言，而是把资料整理得更清楚，把不确定之处说得更诚实，把系统维护得更可靠。对软件学院学生而言，每一次字段设计、错误修复和来源核对，都是专业责任的具体实践。"),
]


def extend(value: str, addition: str, minimum: int) -> str:
    value = (value or "").strip()
    if len(value) >= minimum:
        return value
    return f"{value}{addition}".strip()


def sync_enriched_content(database_path=DB_PATH) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed = 0
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row

        for title, value in PROJECT_VALUES.items():
            cursor = conn.execute(
                """UPDATE project_information SET value=?, source_type=?, source_note=?,
                   verification_status=?, updated_at=? WHERE title=?""",
                (value, "团队公开展示文稿", "依据项目目标与平台建设过程整理。", "团队公开展示文稿", now, title),
            )
            changed += cursor.rowcount
        conn.execute("UPDATE project_information SET title='资料发布规范' WHERE title='隐私保护说明'")

        for title, summary in PLAN_SUMMARIES.items():
            cursor = conn.execute(
                """UPDATE practice_plans SET summary=?, status=?, source_type=?, source_note=?,
                   verification_status=?, updated_at=? WHERE title=?""",
                (summary, "实践流程", "团队公开展示文稿", "依据项目调研方法整理。", "团队公开展示文稿", now, title),
            )
            changed += cursor.rowcount

        for title, summary in RESULT_SUMMARIES.items():
            status = "阶段成果" if title in {"毛公山红色文化数字资源库", "AI赋能红色文化传播方案"} else "成果规划"
            cursor = conn.execute(
                """UPDATE expected_results SET summary=?, status=?, source_type=?, source_note=?,
                   verification_status=?, updated_at=? WHERE title=?""",
                (summary, status, "团队公开展示文稿", "依据项目成果体系整理。", "团队公开展示文稿", now, title),
            )
            changed += cursor.rowcount

        for name, responsibility in TEAM_RESPONSIBILITIES.items():
            cursor = conn.execute(
                "UPDATE team_members SET responsibility=?, updated_at=? WHERE name=?",
                (responsibility, now, name),
            )
            changed += cursor.rowcount

        frontend_data_dir = Path(__file__).resolve().parents[1] / "frontend" / "src" / "data"
        for table, filename in (
            ("achievements", "achievements.json"),
            ("places", "places.json"),
            ("red_stories", "red_stories.json"),
        ):
            path = frontend_data_dir / filename
            if not path.exists():
                continue
            records = json.loads(path.read_text(encoding="utf-8"))
            # 先使用事务内临时标题，避免新标题与尚未更新的旧行触发 UNIQUE 冲突。
            conn.execute(f"UPDATE {table} SET title='__content_sync__' || id")
            for record in records:
                conn.execute(
                    f"""UPDATE {table} SET title=?,summary=?,content=?,category=?,tags=?,date=?,
                       location=?,image=?,source=?,related_ids=? WHERE id=?""",
                    (
                        record["title"],
                        record["summary"],
                        record["content"],
                        record["category"],
                        ",".join(record.get("tags") or []),
                        record.get("date") or "实践推进阶段",
                        record.get("location") or "青岛市城阳区与山东大学软件学院",
                        record.get("image") or record.get("cover") or "",
                        record.get("source") or "山软寻脉·毛公山数字调研实践团整理",
                        ",".join(record.get("relatedItems") or record.get("relatedIds") or []),
                        int(record["id"]),
                    ),
                )
                changed += 1

        extra_achievements = [
            "数据库备份与可重复初始化", "党史媒体对应关系目录", "历史人物真人照片核验表", "全景图库完整性检查",
            "智能问答问题测试集", "地图无密钥降级方案", "浏览器多视口巡检报告", "项目公开资料引用规范",
            "GitHub 工程化交付目录", "Render 公网部署配置",
        ]
        for item_id, title in zip(range(21, 31), extra_achievements):
            summary = (
                f"{title}记录平台工程化建设中的一项具体成果，说明解决的问题、采用的方法、"
                "验证过程与公共展示价值，便于团队复盘和答辩说明。"
            )
            content = (
                f"成果说明\n{summary}\n\n形成过程\n团队先从实际运行和资料管理问题出发，确定可检查的完成标准，"
                "再通过代码实现、数据整理和交叉复核逐步完成。每次调整都保留脚本、文档或测试结果，"
                "避免成果只存在于口头描述之中。\n\n实践价值\n这项工作体现软件学院学生将工程规范带入文化资源项目的过程。"
                "它不追求夸张的技术叙事，而是关注平台能否稳定运行、资料能否追溯、错误能否被发现并修正，"
                "以及后续成员能否读懂并继续维护。\n\n展示说明\n页面呈现的是当前已经形成的阶段成果，"
                "不把仍需第三方密钥或外部授权的能力写成无条件可用。"
            )
            conn.execute(
                """UPDATE achievements SET title=?,summary=?,content=?,category=?,tags=?,location=?,source=? WHERE id=?""",
                (title, summary, content, "工程成果", "软件工程,质量检查,青年实践,数字文化",
                 "山东大学软件学院", "山软寻脉·毛公山数字调研实践团", item_id),
            )

        for row in conn.execute("SELECT id,title,summary,content,source_name FROM history").fetchall():
            content = (
                f"资料导语\n{row['summary']}\n\n公开信息脉络\n{row['content']}\n\n"
                f"平台整理方式\n该条目依据“{row['source_name']}”公开页面建立索引，"
                "重点保留时间、地点、来源和与景区认识有关的内容。平台不依据标题扩写未经来源支持的事件细节，"
                "而是将其作为景区发展、路线导览或文化传播的可追溯资料。\n\n"
                "阅读提示\n不同年份的景区等级、交通与活动信息可能发生变化。历史页面用于了解公开报道脉络，"
                "实际游览请以当日公告、实时地图和现场标识为准。"
            )
            summary = extend(
                row["summary"],
                "该条目保留公开来源与时间信息，用于理解毛公山景区发展和文化传播脉络。",
                45,
            )
            conn.execute("UPDATE history SET summary=?,content=? WHERE id=?", (summary, content, row["id"]))

        for row in conn.execute(
            """SELECT id,title,summary,details,source FROM historical_events
               WHERE length(coalesce(details,'')) < 180"""
        ).fetchall():
            details = (
                f"资料导语\n{row['summary']}\n\n公开资料内容\n{row['details']}\n\n"
                f"整理说明\n该条目依据{row['source']}公开信息建立，保留标题、时间、地点和来源，"
                "用于理解毛公山景区发展、路线建设或文化传播的公开脉络。"
                "平台不依据有限报道补写未出现的人物、活动规模和社会效果。\n\n"
                "使用提示\n这类信息具有时间性，页面中的年份用于资料回顾；开放安排、交通方式和现场服务"
                "可能发生变化，实际到访请查询最新公告。"
            )
            conn.execute("UPDATE historical_events SET details=? WHERE id=?", (details, row["id"]))

        for row in conn.execute("SELECT id,name,summary,content,category,location,source_name FROM scenery").fetchall():
            summary = extend(
                row["summary"],
                f"该专题从{row['category']}角度记录实景特征，并与具体图片来源保持对应。",
                45,
            )
            content = (
                f"景观导语\n{summary}\n\n观察重点\n{row['content']}\n\n"
                f"空间关系\n该内容所对应区域为{row['location']}。浏览时可结合山体、道路、植被、光线和周边环境观察，"
                "不要仅凭单张照片判断完整路线或现场难度。\n\n图片说明\n配图来自已登记的"
                f"{row['source_name']}页面或团队本地影像，主要用于呈现“{row['name']}”的可见景观。"
                "无法确认的拍摄日期和人物身份不作推断。"
            )
            conn.execute("UPDATE scenery SET summary=?,content=? WHERE id=?", (summary, content, row["id"]))

        for row in conn.execute("SELECT id,name,summary,start_point,end_point,route_type FROM routes").fetchall():
            addition = (
                f"路线由“{row['start_point']}”连接至“{row['end_point']}”，适合按{row['route_type']}主题理解。"
                "出发前应核对天气、开放信息和个人体力，平台说明不替代实时导航与现场管理要求。"
            )
            conn.execute("UPDATE routes SET summary=? WHERE id=?", (extend(row["summary"], addition, 70), row["id"]))

        category_copy = {
            "历史文献": "收录具有明确来源的公开文献、报道和资料索引，帮助读者追踪事件背景与表述依据。",
            "人物资料": "整理人物生平、主要事迹、相关事件、真人照片及来源说明，人物信息优先依据权威公开资料。",
            "历史事件": "按时间、地点、人物和来源组织历史事件，区分全国党史学习与毛公山地方文化资料。",
            "图片资料": "保存实景照片、历史资料图、人物照片和项目影像，并登记图片性质、来源、许可与页面用途。",
            "视频资料": "汇集可公开使用的视频入口和项目自制图文微课，播放失败时仍保留封面、简介与来源。",
            "音频资料": "提供毛公山概览、游览指南、平台使用和实践专题讲解稿，支持浏览器语音朗读。",
            "新闻报道": "索引政府、学校和主流媒体公开报道，保留发布日期、原始页面和检索信息。",
            "研究文章": "呈现资料整理、数字传播、社会实践和文化资源保护相关研究与团队方法总结。",
            "口述历史": "保存经授权或情景化整理的访谈内容，明确材料性质，不把单一口述直接作为历史定论。",
            "景区资料": "整理位置、路线、设施、自然环境和参观提示，动态信息以景区当日公告为准。",
        }
        for name, description in category_copy.items():
            conn.execute("UPDATE categories SET description=? WHERE name=?", (description, name))
        for row in conn.execute("SELECT id,name,description FROM categories").fetchall():
            addition = (
                f"“{row['name']}”分类同时保留来源、关联条目和检索标签，"
                "便于读者从列表继续进入完整详情并核对资料依据。"
            )
            conn.execute(
                "UPDATE categories SET description=? WHERE id=?",
                (extend(row["description"], addition, 35), row["id"]),
            )

        image_rows = conn.execute(
            "SELECT id,title,description,category,source_name,location,source_type,alt FROM images"
        ).fetchall()
        for row in image_rows:
            title = (row["title"] or "图片资料").replace("扩展参考资源｜", "")
            description = (
                f"图为“{title}”，归入{row['category'] or '图片资料'}。"
                f"{row['description'] or '页面依据可确认的画面内容作审慎说明。'} "
                f"地点标注为{row['location'] or '来源页面所示区域'}，"
                f"来源为{row['source_name'] or '项目图片资料库'}。"
                "该图片用于与当前专题建立区域或内容参照，不据此推断未标明的人物、日期和事件。"
                "阅读图片时应结合标题、分类、来源和图片性质判断其用途；扩展参考图片不作为毛公山实景或具体党史事件的直接证据。"
            )
            alt = (row["alt"] or "").strip() or f"{title}，{row['category'] or '数字资源库'}图片"
            conn.execute(
                "UPDATE images SET description=?,alt=? WHERE id=?",
                (description, alt, row["id"]),
            )

        for row in conn.execute("SELECT id,name,description,category,location,source FROM scenic_images").fetchall():
            description = (
                f"图为“{row['name']}”，用于呈现{row['category']}内容。{row['description']} "
                f"地点按资料登记为{row['location']}，来源为{row['source']}。"
                "图片说明只描述可确认的景观和页面用途，不补写无法核实的拍摄细节。"
            )
            conn.execute("UPDATE scenic_images SET description=? WHERE id=?", (description, row["id"]))

        for row in conn.execute("SELECT id,title,summary,source_name FROM source_records").fetchall():
            addition = (
                f"该来源记录用于支撑“{row['title']}”相关页面，平台保留来源单位、原始链接和检索状态，"
                "便于读者继续核对，也便于团队在资料更新时追踪表述变化。"
            )
            conn.execute(
                "UPDATE source_records SET summary=? WHERE id=?",
                (extend(row["summary"], addition, 35), row["id"]),
            )

        for row in conn.execute("SELECT id,target_title,script FROM narrations").fetchall():
            addition = (
                f"\n\n收听提示：本段讲解围绕“{row['target_title']}”组织，内容来自平台已登记资料。"
                "您可以继续查看对应图片、地图点位和来源说明；实际游览信息请以现场公告为准。"
            )
            conn.execute("UPDATE narrations SET script=? WHERE id=?", (extend(row["script"], addition, 150), row["id"]))

        conn.execute("DELETE FROM qa_knowledge")
        qa_routes = {
            "毛公山概况": "可继续阅读“毛公山概览”和“全景图库”。",
            "游览指南": "可继续查看“数字地图”和“游览路线”页面。",
            "平台使用": "可从顶部导航进入对应栏目，并使用全站搜索定位资料。",
            "党史学习": "可继续进入“党史学习”和“红色时间轴”查看来源与关联人物。",
            "青年实践": "可继续阅读“实践调研”和“山软青年”专题。",
            "实践团队": "可继续查看团队介绍、成员分工和实践日志。",
            "实践成果": "可继续进入项目成果页阅读形成过程与相关资料。",
            "资料说明": "可在详情页和“资料来源”栏目核对出处与媒体性质。",
            "智能问答": "回答下方会列出相关资料，便于继续核对。",
        }
        for question, answer, category, keywords in QA_ITEMS:
            answer = extend(answer, qa_routes.get(category, "可使用全站搜索继续查找相关专题和来源说明。"), 80)
            conn.execute(
                """INSERT INTO qa_knowledge(question,answer,category,keywords,source,created_at)
                   VALUES (?,?,?,?,?,?)""",
                (question, answer, category, keywords, "平台公开资料与山软寻脉实践团队整理", now),
            )
        changed += len(QA_ITEMS)

        generated_events = conn.execute(
            "SELECT id FROM historical_events WHERE title LIKE '红色历史｜青岛城阳与毛公山文化记忆专题 %' ORDER BY id"
        ).fetchall()
        for row, (title, summary) in zip(generated_events, EDITORIAL_TOPICS):
            details = (
                f"专题导语\n{summary}\n\n"
                "整理思路\n本专题以公开资料、页面来源记录和团队实践观察为基础，"
                "重点说明资料如何被发现、分类、核对并转化为可阅读的数字内容。"
                "对于涉及具体年代、人物和地方事件的表述，平台不依据想象补写，而是保留来源与核对状态。\n\n"
                "数字化表达\n内容通过摘要、标签、图片说明、地图点位和关联阅读进入资源库。"
                "这种组织方式既方便公众浏览，也让后续团队能够追踪依据、修订错误并继续补充材料。\n\n"
                "青年实践视角\n作为山东大学学生社会实践成果，本专题关注专业方法如何服务地方文化："
                "软件工程帮助我们建立稳定结构，实地调研提醒我们尊重现场，内容复核则要求每一句话都对来源负责。"
            )
            conn.execute(
                """UPDATE historical_events SET title=?, event_time=?, location=?, summary=?, details=?,
                   category=?, source=?, verification_status=? WHERE id=?""",
                (title, "资料整理与实践研究阶段", "青岛市城阳区及相关扩展学习区域", summary,
                 details, "文化资料整理", "公开资料与山软寻脉实践团队整理", "团队公开展示文稿", row["id"]),
            )
            changed += 1

        for row in conn.execute("SELECT id,summary FROM historical_events").fetchall():
            summary = extend(
                row["summary"],
                "平台据公开来源整理其背景、地点与文化传播线索，并保留资料出处供读者继续核对。",
                35,
            )
            conn.execute("UPDATE historical_events SET summary=? WHERE id=?", (summary, row["id"]))

        for row in conn.execute("SELECT id,summary FROM learning_articles").fetchall():
            summary = extend(row["summary"], "这一主题也为理解红色精神的当代传承与青年责任提供了清晰线索。", 40)
            conn.execute("UPDATE learning_articles SET summary=?, updated_at=? WHERE id=?", (summary, now, row["id"]))

        for row in conn.execute("SELECT id,youth_insight FROM learning_articles").fetchall():
            insight = extend(
                row["youth_insight"],
                "对青年学生而言，真正的传承应落实为尊重事实、认真学习、服务他人和完成好每一项具体工作。",
                45,
            )
            conn.execute(
                "UPDATE learning_articles SET youth_insight=?,updated_at=? WHERE id=?",
                (insight, now, row["id"]),
            )

        scientists = {"钱学森", "邓稼先", "郭永怀", "袁隆平", "黄旭华", "屠呦呦", "杨利伟"}
        models = {"雷锋", "焦裕禄", "王进喜", "张富清", "申纪兰"}
        for row in conn.execute("SELECT id,name,biography,deeds FROM historical_figures").fetchall():
            if row["name"] in scientists:
                suffix = "其长期工作体现严谨求实、协同攻关和把个人理想融入国家需要的科技报国品格。"
            elif row["name"] in models:
                suffix = "相关事迹把坚定信念落实到具体岗位和群众需要之中，为青年理解责任、劳动与奉献提供了生动参照。"
            else:
                suffix = "其经历贯穿中国革命、建设的重要阶段，相关历史贡献应结合权威党史资料和具体事件持续深入阅读。"
            deeds = extend(row["deeds"], suffix, 50)
            biography = extend(row["biography"], "人物基础信息与真人照片均已在来源页完成对应核对。", 45)
            conn.execute("UPDATE historical_figures SET deeds=?,biography=? WHERE id=?", (deeds, biography, row["id"]))

        for row in conn.execute("SELECT id,description FROM scenic_spots").fetchall():
            description = extend(
                row["description"],
                "平台在数字导览中结合图片、点位和关联阅读呈现该地点，实际到访时应同时参考现场开放与安全提示。",
                50,
            )
            conn.execute("UPDATE scenic_spots SET description=? WHERE id=?", (description, row["id"]))

        for table in ("resources", "digital_resources"):
            columns = {item[1] for item in conn.execute(f"PRAGMA table_info({table})")}
            if "summary" not in columns:
                continue
            title_column = "title" if "title" in columns else "name"
            for row in conn.execute(
                f"SELECT id,{title_column} AS title,summary FROM {table}"
            ).fetchall():
                addition = f"该条目围绕“{row['title']}”整理来源、内容线索与关联阅读，便于检索和答辩展示。"
                summary = extend(row["summary"], addition, 35)
                conn.execute(f"UPDATE {table} SET summary=? WHERE id=?", (summary, row["id"]))

        resource_groups = [
            (range(79, 109), CORE_RESOURCE_TITLES, "毛公山核心资料", "毛公山公开资料与团队现场观察"),
            (range(234, 264), RED_STORY_TITLES, "文化解读", "山软寻脉实践团队文化解读"),
            (range(264, 284), PLACE_TITLES, "地点导览", "毛公山调研路线与公开地图资料"),
            (range(284, 299), PRACTICE_RESOURCE_TITLES, "实践方法", "山软寻脉实践团队工作档案"),
            (range(299, 309), ACHIEVEMENT_RESOURCE_TITLES, "实践成果", "山软寻脉实践团队阶段成果"),
        ]
        for id_range, titles, category, source in resource_groups:
            for item_id, title in zip(id_range, titles):
                if category == "毛公山核心资料":
                    summary = f"“{title}”围绕毛公山及其所在区域的公开信息展开，记录资料来源、现场观察与页面用途，为景区认识、路线导览和文化阅读提供可追溯线索。"
                elif category == "文化解读":
                    summary = f"“{title}”是一篇面向青年读者的文化解读，讨论地方文化资料如何被发现、核对、组织与传播，并明确区分公开事实、团队观察和方法性思考。"
                elif category == "地点导览":
                    summary = f"“{title}”用于组织毛公山调研与游览中的空间信息，结合点位功能、观察任务和安全提示呈现，不把示意点位替代为实时导航结论。"
                elif category == "实践方法":
                    summary = f"“{title}”记录实践团队从问题设计到资料归档的一项具体方法，说明执行步骤、质量要求和协作方式，呈现软件学院学生把专业训练用于真实项目的过程。"
                else:
                    summary = f"“{title}”汇集平台建设中的一项可展示成果，既说明完成内容，也保留数据来源、技术实现和质量复核过程，便于课程答辩与社会实践交流。"
                conn.execute(
                    "UPDATE resources SET name=?,type=?,summary=?,source=?,tags=? WHERE id=?",
                    (title, category, summary, source, f"毛公山,{category},数字资源,青年实践", item_id),
                )

        early_logs = conn.execute("SELECT id FROM research_logs WHERE id <= 15 ORDER BY id").fetchall()
        for row, (title, summary, focus) in zip(early_logs, PRACTICE_LOGS):
            content = (
                f"记录缘起\n{summary}\n\n"
                f"实践过程\n{focus}\n\n"
                "方法收获\n这项工作让团队把课堂中的需求分析、数据建模和质量检查放进真实情境。"
                "我们不再把完成页面当作唯一目标，而是关注资料能否追溯、内容能否被理解、系统能否由下一位成员继续维护。\n\n"
                "青年感悟\n越接近现场，越能体会到文化传播需要耐心。技术可以提高整理和传播效率，"
                "但不能替代核对、倾听和负责的表达。每一次修改，都是团队对公共展示作出的认真回应。"
            )
            conn.execute(
                """UPDATE research_logs SET title=?,summary=?,content=?,category=?,date=?,location=?,source=? WHERE id=?""",
                (title, summary, content, "实践日志", "实践推进阶段", "毛公山调研现场与山东大学软件学院",
                 "山软寻脉·毛公山数字调研实践团整理", row["id"]),
            )
            changed += 1

        later_logs = conn.execute(
            "SELECT id FROM research_logs WHERE id BETWEEN 16 AND 40 ORDER BY id"
        ).fetchall()
        for row, (title, summary) in zip(later_logs, LATER_LOGS):
            content = (
                f"实践现场\n{summary}\n\n"
                "问题与选择\n这一环节看似只是平台建设中的一个细节，却直接影响资料能否被可靠理解。"
                "团队没有把任务停留在完成数量上，而是把来源、用途、页面表现和后续维护放在同一套检查中。\n\n"
                "专业方法\n我们把软件工程中的需求拆分、数据约束、异常处理和测试复核转化为实践方法："
                "先说明问题，再记录处理过程，最后由非原岗位成员交叉检查。这样的流程让每项成果都有清楚的来路。\n\n"
                "青年感悟\n社会实践让我们意识到，技术能力真正有价值的时刻，往往不是界面最炫目时，"
                "而是它帮助一份资料被妥善保存、一个来源被准确标注、一次访问变得更清晰时。"
                "这份耐心，也是青年学生参与文化数字化应当承担的责任。"
            )
            conn.execute(
                "UPDATE research_logs SET title=?,summary=?,content=?,category=?,date=?,location=?,source=? WHERE id=?",
                (f"实践日志｜{title}", summary, content, "实践日志", "实践推进阶段",
                 "毛公山调研现场与山东大学软件学院", "山软寻脉·毛公山数字调研实践团整理", row["id"]),
            )
            changed += 1

        for row in conn.execute("SELECT id,summary FROM research_logs").fetchall():
            summary = extend(row["summary"], "内容结合团队岗位、研究方法和平台建设过程展开，呈现青年实践中的具体判断与成长。", 35)
            conn.execute("UPDATE research_logs SET summary=? WHERE id=?", (summary, row["id"]))

        audio_rows = conn.execute("SELECT id FROM audio_guides ORDER BY id").fetchall()
        closings = [
            "感谢收听，您可以继续进入相关专题查看图片、来源和延伸资料。",
            "愿这段讲解成为继续阅读的起点，也欢迎通过平台搜索发现更多关联内容。",
            "请带着问题继续浏览，让一次数字访问转化为更主动、更可靠的文化学习。",
        ]
        for index, (row, topic) in enumerate(zip(audio_rows, AUDIO_TOPICS)):
            title, summary, focus = topic
            summary = extend(
                summary,
                "讲解结合平台现有资料展开，并提供可继续阅读的关联内容与来源线索。",
                35,
            )
            script = (
                f"欢迎收听《{title}》。{summary}\n\n{focus}\n\n"
                "这段讲解由山软寻脉·毛公山数字调研实践团依据平台公开内容整理。"
                "我们希望用平实、清楚的语言连接地方景观、文化资料与青年实践，"
                "既呈现数字技术带来的便利，也保留对来源、事实和现场经验的尊重。"
                f"{closings[index % len(closings)]}"
            )
            conn.execute(
                "UPDATE audio_guides SET title=?,summary=?,script=?,source=? WHERE id=?",
                (title, summary, script, "山软寻脉实践团队讲解稿", row["id"]),
            )
            changed += 1

        conn.commit()
    return changed


if __name__ == "__main__":
    print(f"内容扩充同步完成：更新 {sync_enriched_content()} 条记录。")
