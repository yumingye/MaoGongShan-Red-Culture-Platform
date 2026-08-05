const covers = [
  '/assets/images/commons/hero-hill-monument-jinan-2009-07-18-jpg.jpg',
  '/assets/images/commons/liberation-pavillion-jinan-2008-11-jpg.jpg',
  '/assets/images/commons/2024-04-longhua-revolutionary-martyr-memorial-14-jpg.jpg',
  '/assets/images/commons/national-shandong-university-qingdao-jpg.jpg',
  '/assets/images/commons/20240730-qingdao-campus-of-shandong-university-01-jpg.jpg',
  '/assets/images/culture/maogongshan-red-park-2022.jpg',
  '/assets/images/scenery/maogongshan-mountain.jpg',
  '/assets/images/activity/maogongshan-3a-plaque.jpg'
]

function buildSections(title, focus, practice) {
  return [
    { title: '专题导语', content: `${title}专题不是把若干口号和图片简单排列，而是围绕“从哪里来、解决了什么问题、留下什么经验、今天怎样理解”组织学习。${focus}` },
    { title: '资料组织方法', content: '平台把权威公开资料、地方文化资源、项目实践记录和面向青年的文化解读分层呈现。历史事实保留来源，主题配图不作为事件现场证据；有争议或尚未核验的信息不写成确定结论。' },
    { title: '互动阅读线索', content: '读者可以沿时间节点、人物关系、地点资源和精神关键词四条线索继续浏览。页面中的动态演示用于帮助理解信息关系，不替代原始文献、档案和纪念场馆的正式说明。' },
    { title: '青年实践入口', content: `${practice}学习成果可以通过收藏、答题、时间轴浏览和推荐路线保存到本机，平台不采集姓名、手机号等个人信息。` }
  ]
}

const definitions = [
  ['red-zone', '红色文化数字专区', '综合专题', '连接党史、人物、事件、精神、地点与青年实践的数字展馆入口。', '通过跨栏目关联避免把红色文化压缩成单一年代或单一表现形式。', '建议先浏览时间轴，再选择人物或精神专题深入阅读。'],
  ['shandong-red', '山东红色文化专题', '区域专题', '以沂蒙精神、胶东革命文化和山东红色场馆为线索，建立区域学习索引。', '本专题属于山东红色文化拓展，不把山东其他地区资料写成毛公山本地史。', '可结合山东地方志、纪念馆正式介绍和公开地图继续核对。'],
  ['qingdao-red', '青岛红色文化专题', '区域专题', '从城市发展、工人运动、革命记忆和公共文化场馆理解青岛红色文化。', '青岛地方史内容以政府、地方志和纪念场馆公开资料为优先来源。', '研学前先记录来源，现场拍摄时尊重场馆规定和人物隐私。'],
  ['sdu-practice', '山东大学红色实践专题', '青年实践', '呈现山东大学软件学院学生以软件工程方法参与文化资源整理的过程。', '专题强调专业赋能、事实核验、版权登记和持续维护。', '从需求访谈、数据建模、前端呈现、后端接口到测试复盘形成完整闭环。'],
  ['youth-mission', '新时代青年使命专题', '青年实践', '把理想信念、专业学习、公共责任和基层实践连接为可执行的成长路线。', '青年使命不是抽象口号，而是对每一条数据、每一次服务和每一个用户负责。', '完成一个可靠的小功能，往往比展示一个无法验证的大概念更有价值。'],
  ['major-conferences', '重大会议专题', '党史学习', '按问题背景、会议决策、历史影响和学习方法梳理重要会议。', '会议学习要回到具体历史环境，理解当时需要解决的核心问题。', '使用时间轴对照前因后果，并从正式党史资料核验日期和结论。'],
  ['heroes', '英雄人物专题', '人物档案', '通过人物与事件、地点、集体实践的关联阅读英雄模范资料。', '人物叙述不神化个人，不忽略集体奋斗和时代条件。', '进入人物档案后可继续查看相关事件与来源。'],
  ['red-books', '红色书籍导读', '资源导读', '提供党史基本著作、公开文献和地方文化资料的阅读方法。', '本页是导读索引，不提供未经授权的整本电子书下载。', '优先通过出版社、图书馆和权威数字平台获取合法版本。'],
  ['red-relics', '红色文物数字解读', '文物专题', '从物件信息、使用场景、保存机构和史料价值学习文物阅读方法。', '主题配图不冒充具体文物原件，文物身份以收藏机构正式著录为准。', '观察材质、铭文、年代和流传信息，并核对展签与馆方目录。'],
  ['photo-compare', '历史照片对比实验室', '影像专题', '通过可拖动对比界面观察景观、场馆和城市空间的变化。', '当前对比图片均显示各自来源与说明，不把不同地点拼接成同一地点今昔。', '对比的目的在于训练影像证据意识，而不是制造视觉噱头。'],
  ['study-routes', '红色研学路线', '研学专题', '将资料预习、现场观察、访谈记录和返程整理组合为安全、可执行的路线。', '路线信息仅作教学展示，实时开放时间与交通应以管理单位为准。', '出发前完成资料卡，现场遵守秩序，返程后形成来源清晰的观察记录。'],
  ['revolutionary-sites', '革命纪念地导览', '地点专题', '以纪念馆、旧址、烈士纪念设施和教育基地为对象建立导览方法。', '全国红色地点属于拓展资源，不作为毛公山景区内部点位。', '参观时关注空间、展陈、史料和公共服务，不追求打卡数量。'],
  ['red-stories', '红色故事长卷', '故事专题', '把故事放回时间、人物和资料出处中，通过横向长卷形成关联阅读。', '故事化表达必须以基本史实为边界，不能为了戏剧性虚构对话和细节。', '阅读后可进入知识问答检验自己是否理解故事背景。'],
  ['research-route', '毛公山数字调研路线', '青年实践', '展示从前期资料、实地观察、摄影采集到数据库录入的调研流程。', '团队按照资料、影像、点位和访谈任务分组协作，完整记录现场工作过程。', '每一个采集对象同时记录位置、时间、来源、版权和考证状态。'],
  ['digital-architecture', '数字资源库技术架构', '数字技术', '解释 Vue、FastAPI、SQLite、检索式问答和媒体兜底如何协同工作。', '技术专题如实说明本地检索与第三方大模型的区别，不伪装系统能力。', '通过自动化检查保证路由、接口、图片和移动端布局能够重复验证。']
]

export const exhibitions = definitions.map((item, index) => ({
  id: index + 1,
  slug: item[0],
  title: item[1],
  category: item[2],
  summary: item[3],
  focus: item[4],
  practice: item[5],
  image: covers[index % covers.length],
  gallery: [covers[index % covers.length], covers[(index + 2) % covers.length], covers[(index + 5) % covers.length]],
  keywords: ['资料可追溯', '互动学习', '青年实践'],
  sections: buildSections(item[1], item[4], item[5]),
  source: '平台公开资料与实践团队整理',
  sourceUrl: '/sources'
}))

const lessonDefinitions = [
  ['party-century', '百年党史时间长卷', '党史微课堂', '05:20', '以时间节点串联党的创建、革命、建设、改革与新时代。'],
  ['long-march-route', '长征路线动态图解', '重大历史事件', '04:10', '通过路线动画理解战略转移与重要节点，配图不作为现场影像。'],
  ['spirit-spectrum', '中国共产党人精神谱系', '革命精神讲解', '06:30', '以关键词动画连接不同历史时期形成的精神财富。'],
  ['shandong-memory', '山东红色文化学习地图', '山东红色文化', '04:45', '从沂蒙精神、胶东文化与纪念场馆建立区域学习索引。'],
  ['qingdao-memory', '青岛红色记忆资料索引', '青岛红色历史', '03:50', '介绍地方资料检索、场馆参观与来源核验方法。'],
  ['maogongshan-overview', '走进城阳毛公山', '红色景区介绍', '04:25', '以本地实景图片介绍山体环境、游览提示与文化展示边界。'],
  ['field-research', '毛公山数字调研工作流', '毛公山实地调研', '05:05', '展示资料查阅、实地观察、拍摄登记和结构化录入流程。'],
  ['software-practice', '软件赋能红色文化', '山东大学社会实践', '06:00', '解释软件学院学生如何把工程方法用于文化资源保护。'],
  ['source-check', '一条资料如何完成考证', '红色文物讲解', '03:35', '演示来源、日期、版权和考证状态的登记步骤。'],
  ['youth-learning', '青年理论学习的数字方法', '青年理论学习', '04:00', '用搜索、时间轴、问答与收藏形成个人学习路径。'],
  ['hero-stories', '人物档案怎样阅读', '红色人物故事', '04:40', '把人物放回集体实践和时代背景，避免传奇化叙述。'],
  ['platform-guide', '数字文化平台使用导览', '平台导览', '03:20', '快速掌握资源检索、地图、图库、问答和互动学习入口。']
]

const lessonMedia = {
  'party-century': [
    ['/assets/images/party-history/info-may-fourth.jpg', '项目自制', '五四运动与马克思主义传播专题信息图'],
    ['/assets/images/party-history/party-founding.jpg', '革命旧址照片', '上海中共一大会址当代实景，不是1921年历史现场照片'],
    ['/assets/images/party-history/info-reform-opening.jpg', '项目自制', '改革开放专题信息图']
  ],
  'long-march-route': [
    ['/assets/images/party-history/info-long-march.jpg', '项目自制', '长征时间、空间与主题信息图，不是历史路线原图'],
    ['/assets/images/party-history/long-march.jpg', '纪念馆照片', '六盘山红军长征纪念馆当代实景，不是长征现场照片'],
    ['/assets/images/party-history/info-zunyi-meeting.jpg', '项目自制', '遵义会议在长征进程中的节点信息图']
  ],
  'spirit-spectrum': [
    ['/assets/images/party-history/info-founding-spirit.jpg', '项目自制', '伟大建党精神专题信息图'],
    ['/assets/images/party-history/info-long-march-spirit.jpg', '项目自制', '长征精神专题信息图'],
    ['/assets/images/party-history/info-yanan-spirit.jpg', '项目自制', '延安精神专题信息图']
  ],
  'shandong-memory': [
    ['/assets/images/party-history/info-yimeng-spirit.jpg', '项目自制', '沂蒙精神专题信息图'],
    ['/assets/images/commons/hero-hill-monument-jinan-2009-07-18-jpg.jpg', '纪念设施照片', '济南英雄山纪念设施当代实景'],
    ['/assets/images/commons/liberation-pavillion-jinan-2008-11-jpg.jpg', '纪念设施照片', '济南解放阁当代实景']
  ],
  'qingdao-memory': [
    ['/assets/images/party-history/info-qingdao-red-memory.jpg', '项目自制', '青岛红色记忆资料索引信息图'],
    ['/assets/images/commons/qingdao-54square-jpg.jpg', '当代实景', '青岛五四广场当代城市文化地标'],
    ['/assets/images/culture/qingfeng-community.jpg', '当代实景', '城阳区青峰社区公开资料配图']
  ],
  'maogongshan-overview': [
    ['/assets/images/scenery/maogongshan-mountain.jpg', '毛公山实景', '毛公山山体公开实景照片'],
    ['/assets/images/route/maogongshan-park-route-2022.jpg', '毛公山实景', '毛公山相关游览路线公开图片'],
    ['/assets/images/activity/maogongshan-3a-plaque.jpg', '毛公山实景', '毛公山景区公开标识照片']
  ],
  'field-research': [
    ['/assets/images/activity/maogongshan-3a-plaque.jpg', '实践资料', '实践调研对象登记画面'],
    ['/assets/images/culture/maogongshan-red-park-2022.jpg', '实践资料', '毛公山文化展示区域公开图片'],
    ['/assets/images/route/maogongshan-park-route-2022.jpg', '实践资料', '调研路线资料图片']
  ],
  'software-practice': [
    ['/assets/images/commons/national-shandong-university-qingdao-jpg.jpg', '校史资料', '国立山东大学青岛时期相关历史建筑资料'],
    ['/assets/images/commons/20240730-qingdao-campus-of-shandong-university-01-jpg.jpg', '当代实景', '山东大学青岛校区当代实景'],
    ['/assets/images/party-history/info-social-practice-spirit.jpg', '项目自制', '大学生社会实践精神信息图']
  ],
  'source-check': [
    ['/assets/images/party-history/info-first-congress.jpg', '项目自制', '包含来源核验提示的中共一大专题信息图'],
    ['/assets/images/party-history/first-congress.jpg', '革命旧址照片', '中共一大会址当代实景及来源页记录'],
    ['/assets/images/party-history/info-may-fourth.jpg', '项目自制', '时间、地点、类型和来源字段示例']
  ],
  'youth-learning': [
    ['/assets/images/party-history/info-youth-mission.jpg', '项目自制', '新时代青年使命专题信息图'],
    ['/assets/images/party-history/info-social-practice-spirit.jpg', '项目自制', '大学生社会实践精神信息图'],
    ['/assets/images/commons/20240730-qingdao-campus-of-shandong-university-01-jpg.jpg', '当代实景', '山东大学校园当代实景']
  ],
  'hero-stories': [
    ['/assets/images/party-history/info-leifeng-spirit.jpg', '项目自制', '雷锋精神专题信息图，不冒充人物照片'],
    ['/assets/images/party-history/info-jiaoyulu-spirit.jpg', '项目自制', '焦裕禄精神专题信息图，不冒充人物照片'],
    ['/assets/images/party-history/info-scientist-spirit.jpg', '项目自制', '科学家精神专题信息图']
  ],
  'platform-guide': [
    ['/assets/images/scenery/maogongshan-mountain.jpg', '毛公山实景', '平台毛公山核心资源入口'],
    ['/assets/images/party-history/info-party-founding.jpg', '项目自制', '平台党史学习专题入口'],
    ['/assets/images/commons/20240730-qingdao-campus-of-shandong-university-01-jpg.jpg', '当代实景', '山东大学实践专题入口']
  ]
}

export const videoLessons = lessonDefinitions.map((item, index) => {
  const media = lessonMedia[item[0]]
  return {
  id: index + 1,
  slug: item[0],
  title: item[1],
  category: item[2],
  duration: item[3],
  summary: item[4],
  cover: media[0][0],
  frames: media.map((entry) => entry[0]),
  frameTypes: media.map((entry) => entry[1]),
  frameCaptions: media.map((entry) => entry[2]),
  publishedAt: '2026-07',
  source: '山软寻脉实践团队制作的本地图文动态微课',
  sourceUrl: '/project',
  transcript: `${item[1]}围绕资料背景、核心信息、阅读方法和青年实践四个部分展开。每一幅画面均按当前专题人工指定，不再从公共图片池轮换；画面明确标注项目自制、旧址照片、纪念设施或当代实景，不把当代图片写成历史现场。${item[4]}观看后可进入对应专题、时间轴和知识问答继续学习。`
  }
})

export function getExhibition(slug) {
  return exhibitions.find((item) => item.slug === slug)
}

export function getVideoLesson(slug) {
  return videoLessons.find((item) => item.slug === slug)
}
