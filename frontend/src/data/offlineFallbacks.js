// 后端首次不可用时使用的最小公开内容，不包含个人联系方式或历史事实推断。
export const offlineProject = {
  information: [
    { id: 'offline-team', category: '团队', title: '团队名称', value: '山软寻脉·毛公山数字调研实践团，是一支以山东大学软件学院学生为主体、吸收跨学院成员协作参与的青年实践团队。', verification_status: '项目公开信息' },
    { id: 'offline-unit', category: '单位', title: '所属单位', value: '项目依托山东大学软件学院学生的专业学习与社会实践展开，以软件工程、数据治理和交互设计方法服务地方文化传播。', verification_status: '项目公开信息' },
    { id: 'offline-topic', category: '课题', title: '课题名称', value: '青春寻脉·数智传薪——毛公山红色文化数字化保护与青年赓续实践研究。课题强调资料考证、现场调研和数字建设的结合。', verification_status: '项目公开信息' },
    { id: 'offline-theme', category: '主题', title: '实践主题', value: '以毛公山及城阳区相关公开文化资源为切入点，探索红色文化数字化保护、青年实践与资源库建设。', verification_status: '项目整理' },
    { id: 'offline-time', category: '进程', title: '实践进程', value: '实践按资料准备、实地调研、内容整理、平台开发、测试复核和成果展示六个阶段推进，具体日期以正式日志为准。', verification_status: '项目整理' },
    { id: 'offline-location', category: '地点', title: '实践区域', value: '调研重点面向青岛市城阳区惜福镇街道毛公山周边公开可访问区域，资料整理与系统开发在山东大学软件学院完成。', verification_status: '项目整理' },
    { id: 'offline-route', category: '方法', title: '工作路线', value: '团队沿“案头研究—问题设计—现场观察—影像采集—数据建模—平台开发—测试复盘”的路线推进。', verification_status: '项目整理' },
    { id: 'offline-audience', category: '服务', title: '公众阅读对象', value: '平台面向毛公山文化资源浏览者、红色研学参与者、青年学生和项目答辩观众，提供结构清楚的公开阅读入口。', verification_status: '项目整理' },
    { id: 'offline-goal', category: '目标', title: '数字资源库建设', value: '围绕历史资料、人物档案、自然风光、地图点位和实践记录建立统一数据结构，支持检索、关联与来源追踪。', verification_status: '项目整理' },
    { id: 'offline-rule', category: '规范', title: '内容发布原则', value: '资料发布遵循来源清楚、授权明确和最小必要原则，无法确认的史实、人物身份与拍摄细节不作推断。', verification_status: '平台规则' }
  ],
  plans: [
    { id: 'offline-plan-1', step_order: 1, title: '前期资料查阅', summary: '建立毛公山、城阳文化和山东红色文化资料目录，登记来源单位、网页地址、发布时间与检索日期。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-2', step_order: 2, title: '访谈与观察设计', summary: '围绕地方记忆、游览体验和数字阅读需求设计问题，提前说明记录方式、授权范围与整理边界。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-3', step_order: 3, title: '实地调研', summary: '沿入口、步道、观景节点和文化展示区域开展观察，让后续页面设计回应真实使用场景。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-4', step_order: 4, title: '影像采集', summary: '按全景、道路、植被、文化景观和团队活动建立镜头清单，并同步登记图片说明与使用范围。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-5', step_order: 5, title: '访谈资料整理', summary: '以匿名编号和主题编码归纳访谈材料，不把个人口述直接写成未经核实的历史定论。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-6', step_order: 6, title: '数据清洗与核对', summary: '对公开文献、现场记录和图片进行去重与交叉核对，区分事实、文化解读和实践感悟。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-7', step_order: 7, title: '资源库建设', summary: '将历史、人物、景点、图片、日志和来源录入结构化数据，为检索、详情和问答提供依据。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-8', step_order: 8, title: '前后端开发与测试', summary: '完成响应式页面、数据接口、媒体兜底和错误提示，并在桌面与手机视口逐页检查。', status: '实施流程', verification_status: '项目整理' },
    { id: 'offline-plan-9', step_order: 9, title: '成果整理与复盘', summary: '结合调研问题、平台数据和测试结果形成展示材料，诚实说明完成内容、资料边界与限制。', status: '实施流程', verification_status: '项目整理' }
  ],
  results: [
    { id: 'offline-result-1', status: '已形成', title: '毛公山红色文化数字资源平台', summary: '提供实景图库、历史检索、人物档案、地图导览、实践展示和本地知识库问答，并保留后端断连时的公开内容。', source_title: '项目成果整理', verification_status: '项目公开信息' },
    { id: 'offline-result-2', status: '已形成', title: '调研资料与图片清单', summary: '图片按风景、文化、调研和团队活动分类，保留来源、说明、版权备注、替代文字与响应式网页版本。', source_title: '实践团队资料', verification_status: '项目公开信息' },
    { id: 'offline-result-3', status: '已形成', title: '社会实践调研记录', summary: '以计划、方法、日志、访谈整理稿和青年感悟呈现团队如何发现问题、核对资料并进行协作。', source_title: '实践团队公开文稿', verification_status: '项目公开信息' },
    { id: 'offline-result-4', status: '已形成', title: '资料来源与媒体台账', summary: '为党史文章、人物照片、景观影像和网络资料登记来源与核验状态，支持读者继续查看原始依据。', source_title: '项目来源记录', verification_status: '来源已登记' },
    { id: 'offline-result-5', status: '已形成', title: '平台质量检查工具', summary: '通过数据完整性、图片路径、媒体对应、路由访问、响应式布局和浏览器控制台检查降低展示故障。', source_title: '项目测试记录', verification_status: '项目公开信息' },
    { id: 'offline-result-6', status: '已形成', title: '工程化运行与部署文档', summary: '整理前后端依赖、环境变量、Windows 启停脚本、GitHub 目录和 Render 部署配置，便于异机运行。', source_title: '项目运行文档', verification_status: '项目公开信息' }
  ]
}

export const offlineOverview = {
  sections: [
    { title: '地理位置与区域环境', content: '公开资料显示，毛公山位于青岛市城阳区惜福镇街道青峰社区。山体、社区、登山步道和周边乡村共同构成游览空间，实际出行应结合实时地图、天气和景区公告。' },
    { title: '山体轮廓与名称传播', content: '毛公山因具有辨识度的山体轮廓而进入公众视野，并形成地方文化记忆。平台呈现公开资料中的常见介绍，同时明确区分可核实信息、文化解读和口述说法。' },
    { title: '自然风光观察', content: '山林、裸露岩石、坡面与光线共同构成毛公山的自然观赏层次。图库依据真实照片描述可见景观，不为照片补写无法确认的拍摄日期、人物和事件。' },
    { title: '游览与安全', content: '可按入口、步道、观景和返程安排节奏。出发前应查看天气和开放信息，穿防滑鞋并携带饮水；老年人和儿童应由家人陪同，不在恶劣天气勉强登行。' },
    { title: '红色文化价值', content: '毛公山的文化价值体现在山体形象、红色主题景观、公共教育活动与群众记忆的结合，为青年理解地方文化传播提供了可观察的现实场景。' },
    { title: '数字化建设意义', content: '平台将图片、历史资料、人物、地图、实践日志和来源记录放入统一结构，使内容可以检索、关联、核对和持续修正，而不只是把零散资料搬到网页上。' }
  ],
  images: [],
  routes: [],
  spots: []
}

export const offlineSchool = {
  title: '山软青年数字实践',
  unit: '山东大学软件学院',
  sections: [
    { category: '背景', title: '实践项目背景', content: '山软寻脉·毛公山数字调研实践团以山东大学软件学院学生为主体，把需求分析、数据建模和系统开发带入真实文化场景，回应资料分散、来源难追溯和公众查询不便等问题。' },
    { category: '调研', title: '团队调研目标', content: '团队关注毛公山自然环境、文化展示、游览路线和数字传播方式，尝试建立可复核、可检索、可持续维护的资料体系，并把不能确认的地方史细节留在核验范围之外。' },
    { category: '现场', title: '实地走访与观察', content: '成员围绕入口、步道、观景节点、文化景观和服务设施使用任务单记录位置、可见信息与图片内容，再与公开网页进行对照，让界面设计回应真实使用场景。' },
    { category: '内容', title: '资料整理与来源登记', content: '公开资料登记来源单位、原始页面、发布时间和检索日期；图片同步记录作者、许可、拍摄性质与页面用途，避免把项目材料、网络传说或个人感受写成地方史实。' },
    { category: '影像', title: '景区数字资源采集', content: '影像按全景、山体、道路、植被、文化景观和团队活动分类，进入平台前完成方向校正、重复检查、尺寸转换、替代文字和版权登记。' },
    { category: '开发', title: '网页平台设计与开发', content: '前端使用 Vue 3 组织响应式页面，后端使用 FastAPI 提供检索、详情、地图和问答接口，SQLite 保存结构化资源；公共组件统一处理图片失败、接口超时与空数据。' },
    { category: '功能', title: '搜索、地图与知识问答', content: '搜索连接标题、正文、标签、人物与地点；地图保留无密钥降级导览；问答先检索本站资料再组织回答，没有足够依据时明确提示未收录。' },
    { category: '成长', title: '青年学生的责任', content: '社会实践让团队认识到，一个字段的命名、一张图片的说明和一次错误提示都会影响公众理解。使用新工具的同时，也要愿意核对来源、承认未知并接受反复修改。' },
    { category: '成果', title: '阶段成果与展示', content: '团队已形成可运行平台、实景图片库、党史学习专题、人物档案、地图导览、本地知识问答、实践日志和来源说明，并在成果页交代形成过程。' },
    { category: '维护', title: '持续维护方向', content: '后续维护围绕来源更新、图片授权复核、无障碍阅读和部署稳定性推进，保留数据导入、字段扩展和第三方地图配置能力，使新资料能按同一规范进入平台。' }
  ]
}

export const offlineTeamMembers = [
  {
    id: 'team-yu-mingye',
    name: '于茗烨',
    college: '山东大学软件学院',
    role: '队长、项目负责人',
    responsibility: '负责项目总体统筹、活动组织协调、对外联络及调研报告审核。',
    public_bio: '统筹团队实践安排与平台建设进度，协调资料整理、调研实施和成果呈现。'
  },
  {
    id: 'team-zhang-jinye',
    name: '张金烨',
    college: '山东大学材料科学与工程学院',
    role: '副队长、实践组织',
    responsibility: '协助队长开展实践活动，负责行程安排与现场组织。',
    public_bio: '参与实践流程设计与执行协调，保障实地调研和团队活动有序开展。'
  },
  {
    id: 'team-chen-xuwen',
    name: '陈序文',
    college: '山东大学软件学院',
    role: '技术负责人',
    responsibility: '负责数字化资料整理、数据分析及成果展示制作。',
    public_bio: '运用软件工程和数据处理方法，参与数字资源整理、分析与平台成果呈现。'
  },
  {
    id: 'team-ling-jianxin',
    name: '凌健鑫',
    college: '山东大学软件学院',
    role: '调研负责人',
    responsibility: '负责调研设计、问卷编制、访谈开展及调研数据整理。',
    public_bio: '围绕毛公山文化资源设计调研流程，组织访谈和问卷资料的规范整理。'
  },
  {
    id: 'team-piao-zhenxie',
    name: '朴珍燮',
    college: '山东大学低空科学与工程学院',
    role: '宣传负责人',
    responsibility: '负责摄影摄像、新闻稿撰写及新媒体运营。',
    public_bio: '记录团队实践过程，整理图文影像资料并参与项目宣传内容制作。'
  },
  {
    id: 'team-zhao-lerong',
    name: '赵乐镕',
    college: '山东大学软件学院',
    role: '后勤与安全负责人',
    responsibility: '负责物资采购、经费管理、安全保障及签到统计。',
    public_bio: '承担实践活动的物资、经费与安全保障工作，为团队现场执行提供支持。'
  }
]

export const offlineNarrations = [
  {
    id: 'offline-guide',
    title: '平台导览',
    summary: '毛公山红色文化数字资源平台使用说明',
    duration: '约 2 分钟',
    image: '/assets/images/banners/summit-terrace-panorama-hero.webp',
    script: '欢迎使用毛公山红色文化数字资源平台。首页连接毛公山概览、全景图库、红色历史、实践调研、数字地图和资料来源页面。浏览山景时，你可以查看图片标题、内容说明和来源；阅读党史专题时，页面会区分毛公山核心资料、全国党史学习与山东红色文化拓展内容。若要规划现场游览，请先阅读路线与安全提示，并以当天开放信息和实时地图为准。平台由山软寻脉·毛公山数字调研实践团整理建设，希望用可靠资料、真实影像和清楚的数字结构，让地方文化更容易被理解、核对和继续维护。'
  }
]

export const offlineSources = [
  { title: '项目提供的毛公山照片资料', source_name: '实践团队本地资料', source_type: '图片资料', retrieved_at: '2026-07-30', verification_status: '来源已登记', source_url: '' },
  { title: '平台数据真实性与版权说明', source_name: '平台整理', source_type: '管理说明', retrieved_at: '2026-07-30', verification_status: '公开说明', source_url: '' }
]
