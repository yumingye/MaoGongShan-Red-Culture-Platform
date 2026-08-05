# 项目结构说明

## 毛公山照片资源

```text
毛公山照片/                              原始照片，只读保留且不进入 GitHub 包
assets/images/
├─ architecture/                        景区建筑响应式 WebP
├─ banners/                             首页横幅 WebP
├─ people/                              人物事迹展板 WebP
├─ red-culture/                         红色文化展陈 WebP
├─ research/                            调研活动 WebP
├─ scenery/                             毛公山自然风景 WebP
└─ team/                                团队合影 WebP
frontend/src/data/maogongshanPhotos.json 前端统一照片清单
database/maogongshan_photos.json          后端恢复清单
backend/import_photo_materials.py         可重复导入与图片处理脚本
tools/analyze_photo_materials.py          原图扫描与联系表脚本
docs/photo-import/                        扫描报告和联系表
```

## 本轮新增核心文件

- `frontend/src/data/experienceContent.js`：15 个动态展馆和 12 条图文动态微课的统一结构化数据。
- `frontend/src/components/MotionStory.vue`：可暂停、支持减少动态效果的本地图文动画。
- `frontend/src/components/SafeVideo.vue`：播放器加载、封面、失败重试和无媒体降级。
- `frontend/src/components/PhotoCompare.vue`：可拖动的影像对比组件。
- `frontend/src/views/ExhibitionHub.vue`、`ExhibitionDetail.vue`：动态专区列表与独立专题详情。
- `frontend/src/views/VideoHub.vue`、`VideoDetail.vue`：红色影像馆与动态图文微课详情。
- `frontend/src/views/InteractiveLearning.vue`：积分、解析、错题和本地学习报告。
- `frontend/src/views/Timeline.vue`：横向长卷、纵向时间轴、阶段筛选和自动播放。

```text
暑期社会实践—毛公山/
├─ backend/                      后端 FastAPI、SQLite 数据库和数据增强脚本
│  ├─ app.py                     后端主程序
│  ├─ requirements.txt           Python 依赖
│  ├─ augment_map_spots.py       地图点位补充脚本
│  └─ data/maogongshan.db        SQLite 数据库
├─ frontend/                     Vue 3 前端
│  ├─ public/assets/images/      本地图片资源
│  ├─ scripts/quality-check.mjs  自动质量检查脚本
│  ├─ src/api/                   API 封装
│  ├─ src/components/            公共组件
│  ├─ src/data/topicPages.js     二级专题结构化数据
│  ├─ src/router/index.js        路由配置
│  └─ src/views/                 页面组件
├─ docs/                         项目文档、测试报告和来源说明
├─ README.md                     项目说明
├─ .env.example                  环境变量示例
├─ .gitignore                    Git 忽略规则
├─ start.bat                     Windows 一键启动脚本
├─ start_backend.ps1             后端启动脚本
└─ start_frontend.ps1            前端启动脚本
```

## 主要页面

- 首页 `/`
- 毛公山概览 `/overview`
- 红色历史 `/history`
- 历史人物 `/figures`
- 红色故事 `/stories`
- 数字资源库 `/resources`
- 实践调研 `/research`
- 山软青年 `/school`
- 数字地图 `/map`
- 全景图库 `/scenery`
- 音频讲解 `/audio`
- AI 数字讲解 `/guide`
- 智能问答 `/chat`
- 三维沙盘 `/sandtable`
- 收藏中心 `/favorites`
- 关于平台 `/about`
- 使用帮助 `/help`

## 新增二级专题

- `/overview/geography`
- `/overview/name-origin`
- `/overview/nature`
- `/overview/culture`
- `/overview/routes`
- `/history/topic/spirit`
- `/history/topic/qingdao-memory`
- `/research/topic/route`
- `/research/topic/interviews`
- `/research/topic/methods`
- `/research/topic/reflections`
- `/school/topic/introduction`
- `/school/topic/architecture`
- `/school/topic/development`
- `/school/topic/responsibility`
- `/map/topic/red-points`
- `/map/topic/research-route`
- `/map/topic/service`
- `/gallery/maogongshan`
- `/gallery/red-culture`
- `/gallery/research`
- `/gallery/school`
- `/resources/category/documents`
- `/resources/category/images`
- `/resources/category/audio`
- `/resources/category/achievements`
# 2026-07-22 结构补充

- `backend/augment_red_learning.py`：34 条党史和红色文化专题的幂等数据同步。
- `frontend/src/views/LearningHub.vue`：党史学习、事件、精神和拓展资料复用列表。
- `frontend/src/views/LearningDetail.vue`：专题正文、知识卡片、来源、收藏、分享和相关推荐。
- `frontend/src/utils/reveal.js`：滚动出现动画与减少动态效果兼容。
- `frontend/scripts/browser-layout-check.mjs`：基于 Chrome DevTools 协议的桌面/移动浏览器检查。
- `docs/screenshots/`：真实浏览器验收截图。
