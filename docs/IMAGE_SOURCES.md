# 图片来源说明

## 本地图片目录

```text
assets/images/
├─ architecture/
├─ activity/
├─ banners/
├─ commons/
├─ culture/
├─ fallback/
├─ maogongshan/
├─ people/
├─ red-culture/
├─ research/
├─ route/
├─ scenery/
└─ team/
```

## 管理原则

- 当前本地图片文件不少于 60 张。
- 页面不得依赖随机图片接口。
- 核心页面图片均使用本地路径。
- 图片加载失败时使用 `fallback/fallback-real-scenery.jpg`。
- 图片详情页和数据库记录保留来源、地点、分类和版权说明。
- 对授权状态不清晰的图片，只用于课程展示和社会实践演示，不作为商业传播素材。

## 项目提供的毛公山照片（2026-07-30）

- 原始目录：项目根目录 `毛公山照片/`，原图未修改。
- 来源名称：项目提供的毛公山照片资料。
- 扫描数量：48 张；接入 42 张；6 张近似重复照片未接入；损坏照片 0 张。
- 内容范围：毛公山山景与步道、景区文化设施、红色文化展陈、团队调研记录和团队合影。
- 拍摄时间：原始文件未提供可靠日期，页面统一显示“原始照片未标注”。
- 版权状态：项目本地素材；公开传播或商业使用前由项目团队确认授权范围。
- 详细清单和处理方式见 [PHOTO_IMPORT_REPORT.md](PHOTO_IMPORT_REPORT.md)。

## 本轮补充接入的公开网络来源图片

本轮没有增加不明来源外链。以下两张图片此前已从 Wikimedia Commons
下载到项目本地，本轮补充了统一数据记录、页面归属和可见版权说明：

| 本地文件名 | 使用页面 | 原始来源 | 用途 | 处理 |
| --- | --- | --- | --- | --- |
| `qingdao-54square-jpg.jpg` | 青岛红色文化专题 | https://commons.wikimedia.org/wiki/File:Qingdao_54square.jpg | 青岛城市文化拓展配图，不作为毛公山实景或历史现场照片 | 已本地化并压缩，CC BY-SA 3.0，作者 Chang Liu |
| `20240730-qingdao-campus-of-shandong-university-01-jpg.jpg` | 山东大学软件学院专题、山东大学实践专题 | https://commons.wikimedia.org/wiki/File:20240730_Qingdao_Campus_of_Shandong_University_01.jpg | 山东大学青岛校区当代校园实景 | 已本地化并压缩，CC BY-SA 4.0，作者 Windmemories |

曾尝试从 Wikimedia Commons 新增两张许可明确的青岛照片，但远端返回 HTTP
429，因此没有写入不完整文件，也没有改用来源不明图片。核心页面继续优先使用
项目提供的 42 张毛公山与实践调研照片。

## 已修复问题

- 新增统一 fallback 图片。
- 修正 GIF 文件扩展名不一致问题。
- 修正山东大学校园图片路径。
- 质量检查脚本会检查专题图片路径是否存在。

## 后续使用提醒

上传真实毛公山新照片时，建议使用英文文件名，保存到对应分类目录，并同步补充数据库中的图片名称、图片来源、地点、拍摄时间、版权说明和检索日期。

## 党史图文一致性专项（2026-07-22）

党史媒体统一保存在 `assets/images/party-history/`。每个真实照片的主题、地点和许可均通过 Wikimedia Commons 文件页核对；页面同时显示媒体类型、图片说明、来源页和版权说明。以下照片均为当代旧址、纪念馆或纪念设施照片，不标作历史现场影像：

| 本地文件 | 对应专题 | 媒体类型 | 原始文件页 |
|---|---|---|---|
| `may-fourth.jpg` | 五四运动与马克思主义传播 | 当代实景 | https://commons.wikimedia.org/wiki/File:Peking_University_Red_Building.jpg |
| `party-founding.jpg`、`first-congress.jpg` | 中国共产党成立、中共一大 | 革命旧址照片 | https://commons.wikimedia.org/wiki/File:Site_of_the_First_National_Congress_of_the_CPC_-_2025.jpg |
| `nanchang-uprising.jpg` | 南昌起义 | 纪念设施照片 | https://commons.wikimedia.org/wiki/File:Memorial_tower_of_Nanchang_Uprising.jpg |
| `jinggangshan-base.jpg` | 井冈山革命根据地 | 纪念馆照片 | https://commons.wikimedia.org/wiki/File:井冈山革命博物馆_01.jpg |
| `gutian-meeting.jpg` | 古田会议 | 革命旧址照片 | https://commons.wikimedia.org/wiki/File:Gutian_entrance.jpg |
| `long-march.jpg` | 红军长征 | 纪念馆照片 | https://commons.wikimedia.org/wiki/File:Liupanshan_Red_Army_Long_March_Memorial_Hall_(20260201154058).jpg |
| `zunyi-meeting.jpg` | 遵义会议 | 革命旧址照片 | https://commons.wikimedia.org/wiki/File:Site_of_Zunyi_Conference_(20180220101816).jpg |
| `yanan-period.png` | 延安时期 | 当代实景 | https://commons.wikimedia.org/wiki/File:延安宝塔夜景.png |
| `xibaipo.jpg` | 西柏坡 | 纪念馆照片 | https://commons.wikimedia.org/wiki/File:Xibaipo_Memorial_Hall_(20240609100945).jpg |
| `resist-us-aid-korea.jpg` | 抗美援朝 | 纪念设施照片 | https://commons.wikimedia.org/wiki/File:Memorial_Tower_to_Resist_U.S._Aggression_and_Aid_Korea.jpg |
| `reform-opening.jpg` | 改革开放 | 纪念馆展陈照片 | https://commons.wikimedia.org/wiki/File:SZ_深圳博物館_Shenzhen_Museum_exhibition_rooms_Reform_and_Opening-Up_History_signs_Sept_2017_IX1.jpg |

人物照片已完成30位逐人核对。毛泽东、周恩来、朱德、邓小平沿用原有
Commons 真人照片；刘少奇、任弼时、陈云、董必武、彭德怀、林伯渠、贺龙、
刘伯承、陈毅、聂荣臻、徐向前、叶剑英、罗荣桓、粟裕、雷锋、焦裕禄、
王进喜、钱学森、邓稼先、郭永怀、袁隆平、黄旭华、屠呦呦、杨利伟、
张富清、申纪兰依据 Wikidata 人物实体的 P18 字段定位 Commons 文件，
并核对实体描述、文件页、作者和许可元数据。全部照片已本地化至
`assets/images/party-history/figure-*.jpg`，人物详情页展示
原始文件页与许可说明，逐项数据同时保存在
`frontend/public/data/party-media-manifest.json`。

人物照片自动检查由 `python -m backend.check_figure_photos` 执行，检查人物
集合、文件存在性、图片解码、照片类型、来源页和许可说明。带姓名的人工
核对总览保存在 `docs/screenshots/figure-portraits-contact-sheet.jpg`。

53 篇专题均生成独有的 `info-*.jpg` 信息图；9 个党史阶段和 6 个栏目导览也使用独立项目自制图解。项目自制图解不标注为历史照片。
