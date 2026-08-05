# 青岛市城阳区毛公山红色文化数字资源平台

面向社会实践展示、课程答辩与公众浏览的红色文化数字平台。项目以毛公山和城阳区文化资源为核心，同时设置党史学习、山东红色文化、青岛红色记忆、山东大学软件学院实践专题。平台坚持区分地方史实、全国党史拓展、当代实景和项目自制图解，所有党史媒体均保存来源、类型和章节关联信息。

项目作者：于茗烨

所属单位：山东大学软件学院

项目用途：大学生社会实践成果展示、红色文化数字化保护与教学演示

## 项目背景

本项目源于山东大学软件学院毛公山红色文化调研社会实践。团队围绕青岛市城阳区毛公山及周边红色文化资源开展现场走访、资料整理与数字化传播研究，将调研照片、历史资料、研学内容和实践成果组织为可检索、可浏览、可持续维护的数字文化平台。

平台既服务于社会实践成果展示和课程答辩，也希望以规范的数据来源记录、响应式网页和开放的工程结构，为后续红色文化数字化保护、地方文化传播及教学应用提供可复用基础。

## 主要功能

- 毛公山概览、自然风光、景点导览和研学路线。
- 党史文章、历史事件、红色人物、红色精神与交互时间轴。
- 图片影像馆、数字资源库、音频讲解和图文微课。
- 关键词搜索、分类筛选、分页、收藏和最近浏览。
- 基于 SQLite 知识库的本地检索式智能问答。
- 高德地图 Web JS API 导览；未配置 Key 时自动使用本地静态导览。
- 山东大学软件学院社会实践、调研日志、成果和团队专题。
- 管理员登录及历史资料、人物、资源和图片的基础管理。
- 图片加载失败、接口异常、地图缺少 Key 和深层路由的稳定降级。
- GET 请求失败时自动重试，并可使用最近一次成功缓存或公开本地基础数据。
- 页面级错误边界、分类图片备用资源和受限环境复制链接降级。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Vue Router、Element Plus、Axios |
| 后端 | Python 3.10+、FastAPI、Uvicorn |
| 数据库 | SQLite |
| 媒体 | 本地图片资源、来源元数据、统一安全媒体组件 |
| 测试 | Node.js 数据检查脚本、浏览器布局与深层路由巡检 |

## 项目结构

```text
MaoGongShan-Red-Culture-Platform/
├─ assets/                    图片、视频等源静态资源
├─ database/
│  ├─ maogongshan.db         公开基础 SQLite 数据
│  └─ maogongshan_photos.json 照片导入清单
├─ frontend/
│  ├─ public/                 公开数据及运行时同步的静态资源
│  ├─ scripts/                数据、图库、党史媒体和浏览器检查
│  ├─ src/
│  │  ├─ api/                 统一 HTTP 请求
│  │  ├─ components/          导航、页脚、安全媒体等公共组件
│  │  ├─ data/                前端结构化专题数据
│  │  ├─ router/              一级、二级和详情路由
│  │  ├─ styles/              全局设计系统和响应式样式
│  │  └─ views/               页面组件
│  ├─ .env.example
│  ├─ package.json
│  └─ vite.config.js
├─ backend/
│  ├─ static/                 后端上传资源
│  ├─ app.py                  FastAPI 应用与接口
│  ├─ config.py               集中环境配置
│  ├─ init_db.py              幂等初始化和安全重建
│  ├─ backup_db.py            数据库备份
│  ├─ sanitize_public_db.py   发布前清除运行记录
│  ├─ .env.example
│  └─ requirements.txt
├─ docs/                      数据来源、图片来源、测试和迭代文档
├─ scripts/
│  ├─ start-project.ps1       安装依赖并启动前后端
│  ├─ stop-project.ps1        按 PID 关闭本项目进程
│  ├─ verify-project.ps1      打包前结构与敏感文件检查
│  └─ package-project.ps1     生成干净 ZIP
├─ .env.example              配置索引
├─ .gitignore
├─ LICENSE
├─ README.md
├─ start.bat
├─ stop.bat
└─ package-project.bat
```

根目录 `assets/` 是媒体资源的唯一源码目录。安装依赖、启动、测试或构建前，`frontend/scripts/sync-assets.mjs` 会自动把它同步到被 Git 忽略的 `frontend/public/assets/`，因此现有 `/assets/...` 页面路径保持不变，也不会在仓库中保存重复图片。

`node_modules`、Python 虚拟环境、同步生成的前端资源、构建产物、日志、私密文档和真实 `.env` 不属于项目交付内容。

## Windows 一键启动

环境要求：

- Python 3.10 或更高版本，并可使用 `python` 或 `py` 命令。
- Node.js 18 或更高版本，并可使用 `npm` 命令。

双击根目录的：

```text
start.bat
```

脚本会：

1. 检查 8000 和 5173 端口；
2. 首次运行时创建 `backend/.venv`；
3. 仅在依赖清单变化时安装 Python 和 npm 依赖；
4. 在两个独立 PowerShell 窗口中启动后端和前端；
5. 等待健康检查通过后打开浏览器。

停止项目：

```text
stop.bat
```

停止脚本读取 `.runtime/project-pids.json`，只结束本次脚本启动的进程树。

## 手动启动后端

在项目根目录执行：

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python.exe -m backend.init_db
backend\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

后端地址：

- API 根地址：`http://127.0.0.1:8000`
- Swagger 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

## 手动启动前端

打开第二个终端：

```powershell
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

Vite 将 `/api` 和 `/static` 代理到 `http://127.0.0.1:8000`，页面代码中没有本机绝对路径。

## 环境变量

后端配置：

```powershell
Copy-Item backend\.env.example backend\.env
```

前端配置：

```powershell
Copy-Item frontend\.env.example frontend\.env
```

主要变量：

| 变量 | 说明 |
| --- | --- |
| `BACKEND_HOST` / `BACKEND_PORT` | 后端监听地址和端口 |
| `PORT` | Render 自动提供的监听端口，优先级高于 `BACKEND_PORT` |
| `DATABASE_URL` | SQLite 路径，相对路径以项目根目录解析 |
| `UPLOAD_DIR` | 后端上传目录 |
| `CORS_ORIGINS` | 允许访问 API 的前端地址 |
| `FRONTEND_HOST` | Render 正式前端主机名，不包含协议；用于精确 CORS |
| `READ_ONLY_MODE` | 公网展示实例设为 `true`，关闭后台写入与上传 |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_TOKEN` | 本地管理配置；密码和 Token 无源码默认值 |
| `VITE_API_BASE_URL` | 前端 API 根地址；开发环境留空使用 Vite 代理 |
| `VITE_API_HOST` | 兼容变量；正式部署优先使用完整 HTTPS 地址 `VITE_API_BASE_URL` |
| `VITE_PUBLIC_READ_ONLY` | 公网构建设为 `true`，后台页显示只读说明 |
| `VITE_AMAP_KEY` | 高德地图 Web JS API Key |
| `VITE_AMAP_SECURITY_CODE` | 高德地图安全密钥 |
| `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | 可选大模型配置 |

真实 `.env` 已被 `.gitignore` 排除，不要提交 API Key、Token 或密码。

## 数据库

公开数据库位于：

```text
database/maogongshan.db
```

普通初始化是幂等操作，不会删除现有数据：

```powershell
backend\.venv\Scripts\python.exe -m backend.init_db
```

安全重建会先生成时间戳备份：

```powershell
backend\.venv\Scripts\python.exe -m backend.init_db --reset
```

手动备份：

```powershell
backend\.venv\Scripts\python.exe -m backend.backup_db
```

打包脚本只清理 ZIP 副本中的 `chat_records` 和 `visit_records`，不修改原数据库。

## 生产构建和质量检查

```powershell
cd frontend
npm run lint
npm run test
npm run build
```

运行浏览器巡检前，需要先启动前后端：

```powershell
npm run check:browser
```

检查内容包括数据 ID、详情正文、图片路径、党史章节媒体对应关系、图库完整性、深层路由、移动端溢出和浏览器严重错误。

## 地图与智能问答

- 未配置高德 Key 时，地图页仍显示本地点位、分类筛选、路线说明和静态导览，不会白屏。
- 未配置大模型时，问答自动使用 SQLite 知识库检索，返回相关资料和来源。
- 大模型和高德地图均属于可选增强项，不影响平台基础运行。

## 图片、视频和音频

- 核心图片源文件均存放于根目录 `assets/`，运行前自动同步到前端公开目录。
- 图库数据和媒体清单位于 `frontend/public/data/`。
- 项目提供的 48 张毛公山原始照片已完成只读扫描；42 张去重后照片已生成 WebP 多尺寸版本并接入首页、图库、调研、团队和活动页面。
- 统一照片清单位于 `frontend/src/data/maogongshanPhotos.json`，可重复导入脚本为 `backend/import_photo_materials.py`。
- 原始素材重新处理命令：`backend\.venv\Scripts\python.exe backend\import_photo_materials.py`。正常运行项目不需要重复执行。
- 每张党史图片记录文章、章节、事件、地点、类型、说明和来源。
- 图片来源见 [docs/IMAGE_SOURCES.md](docs/IMAGE_SOURCES.md)。
- 本次照片整理报告见 [docs/PHOTO_IMPORT_REPORT.md](docs/PHOTO_IMPORT_REPORT.md)。
- 资料来源见 [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)。
- 媒体失败时由安全媒体组件显示本地备用内容，不留下裂图或纯黑区域。

## 自动打包

双击：

```text
package-project.bat
```

脚本会在系统临时目录创建副本，排除依赖、缓存、日志、私密目录、数据库备份和 `.env`，清理运行记录，执行结构与密钥检查，然后生成：

```text
maogongshan-red-culture-platform.zip
```

压缩包只有一层项目根目录。原项目和本地依赖不会被删除。

## 上传 GitHub

确认质量检查和打包成功后：

```powershell
git init
git add .
git commit -m "Initial release"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

不要上传：

- `.env`
- `node_modules`
- `backend/.venv`
- `dist`、缓存和日志
- 数据库备份
- 原始 Word 申报材料或包含个人信息的文件
- 未获授权的大型视频

这些规则已写入 `.gitignore`。

## Render 公网部署

仓库根目录的 `render.yaml` 定义了两个服务：

- `maogongshan-red-culture-web-yumingye`：Render Static Site。
- `maogongshan-red-culture-api-yumingye`：Render Python Web Service。

Blueprint 使用两个服务名对应的公开 HTTPS 地址连接前后端：前端构建变量
`VITE_API_BASE_URL` 指向 API 服务，后端 `CORS_ORIGINS` 和 `FRONTEND_HOST` 指向
Static Site。前端不依赖 `localhost`，后端监听 Render 提供的 `0.0.0.0:$PORT`。
SPA Rewrite 已配置为 `/* → /index.html`。

> Render 的服务名需要全局唯一。当前配置按
> `maogongshan-red-culture-web-yumingye.onrender.com` 和
> `maogongshan-red-culture-api-yumingye.onrender.com` 生成公网地址。如果创建 Blueprint
> 时提示名称已占用，需先同时修改 `render.yaml` 中的两个 `name`，并同步修改
> `VITE_API_BASE_URL`、`CORS_ORIGINS` 和 `FRONTEND_HOST` 的域名，再重新 Apply。

### 方式一：使用 Blueprint

1. 在 GitHub 新建空仓库，不勾选自动生成 README。
2. 在本项目根目录执行“上传 GitHub”一节的 Git 命令。
3. 登录 [Render Dashboard](https://dashboard.render.com/)。
4. 选择 **New + → Blueprint**。
5. 授权 Render 读取刚创建的 GitHub 仓库。
6. Blueprint Path 保持 `render.yaml`，点击 **Apply**。
7. 在 Apply 前核对两个服务名及三个公网地址变量是否完全一致。
8. 等待后端健康检查通过，再等待前端构建完成。
9. 打开 Static Site 显示的 `https://...onrender.com` 地址。
10. 访问后端 `/api/health`，确认返回 `status: ok`，再抽查首页和任一详情页刷新。

Blueprint 的实际配置：

| 服务 | 配置项 | 值 |
| --- | --- | --- |
| 后端 | Root Directory | `.` |
| 后端 | Runtime | `Python` |
| 后端 | Build Command | `pip install --upgrade pip && pip install -r backend/requirements.txt` |
| 后端 | Start Command | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| 后端 | Health Check | `/api/health` |
| 前端 | Root Directory | `frontend` |
| 前端 | Runtime | `Static` |
| 前端 | Build Command | `npm ci && npm run build` |
| 前端 | Publish Directory | `./dist` |
| 前端 | Rewrite | `/*` → `/index.html` |

生产环境变量已经写在 Blueprint 中，不包含真实密钥。`ADMIN_PASSWORD` 和
`ADMIN_TOKEN` 由 Render 生成；公开实例开启只读模式，因此后台写入和上传不会落盘。

### 方式二：手动创建两个服务

先创建后端 Web Service：

1. **New + → Web Service**，选择 GitHub 仓库。
2. Root Directory 留空（仓库根目录）。
3. Runtime 选择 Python。
4. Build Command：
   `pip install --upgrade pip && pip install -r backend/requirements.txt`
5. Start Command：
   `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
6. Health Check Path 填写 `/api/health`。
7. 设置 `DATABASE_URL=/tmp/maogongshan.db`、`READ_ONLY_MODE=true`、
   `SERVICE_NAME=maogongshan-api`。
8. 部署后记录后端完整 HTTPS 地址。

再创建前端 Static Site：

1. **New + → Static Site**，选择同一仓库。
2. Root Directory 填写 `frontend`。
3. Build Command 填写 `npm ci && npm run build`。
4. Publish Directory 填写 `dist`。
5. 设置 `VITE_API_BASE_URL=https://你的后端服务.onrender.com`。
6. 设置 `VITE_PUBLIC_READ_ONLY=true`。
7. 添加 Rewrite：Source `/*`，Destination `/index.html`，Action `Rewrite`。
8. 部署后把前端完整 Origin 写入后端 `CORS_ORIGINS`，例如
   `https://your-frontend.onrender.com`；同时把不含协议的主机名写入
   `FRONTEND_HOST`，例如 `your-frontend.onrender.com`，然后重新部署后端。

### 可选环境变量

- 高德地图：在 Static Site 设置 `VITE_AMAP_KEY` 和
  `VITE_AMAP_SECURITY_CODE`，然后执行 **Clear build cache & deploy**。
- 外部大模型：在 Web Service 设置 `LLM_PROVIDER`、`LLM_API_KEY`、
  `LLM_BASE_URL` 和 `LLM_MODEL`。未配置时继续使用本地检索问答。
- 自定义域名：在前端服务 **Settings → Custom Domains** 添加域名；随后将完整
  HTTPS Origin 加入后端 `CORS_ORIGINS`，多个地址用英文逗号分隔。

### SQLite 部署策略

Render 默认文件系统是临时的。当前 Blueprint 将仓库中的公开 SQLite 数据库复制
到 `/tmp/maogongshan.db`，用于浏览、检索和问答，并启用只读公开模式。运行期访问
计数、问答记录、后台修改和上传不会作为永久数据保存，后台写操作会返回明确的
`403`，不会让用户误以为修改已持久化。

需要长期后台编辑时，应使用 Render Persistent Disk 或迁移 PostgreSQL，再把
`READ_ONLY_MODE` 改为 `false` 并设置强随机管理员凭据。不要直接在免费实例的普通
文件系统中保存上传文件。

### 重新部署、日志与域名

- 推送到 `main` 后，两个服务按 `autoDeployTrigger: commit` 自动重新部署。
- 手动部署：服务页面选择 **Manual Deploy → Deploy latest commit**。
- 构建失败：查看服务页面 **Logs**，优先检查 Node/Python 版本、环境变量和命令。
- 前端接口失败：先打开后端 `/api/health`，再检查 `VITE_API_BASE_URL` 是否为完整
  HTTPS 地址，以及后端 `CORS_ORIGINS` 是否包含当前前端完整 Origin。
- 自定义域名在服务 **Settings → Custom Domains** 中配置；DNS 验证完成后 Render
  自动签发 HTTPS 证书。

### 上线前核对

在仓库根目录执行：

```powershell
cd frontend
npm ci
npm run check
npm run build
npm run check:deploy
```

上传 GitHub 前再确认：

- `git status --ignored` 中 `.env`、`node_modules`、`.venv`、`dist` 和日志均为忽略项；
- 仓库中只有 `.env.example`，没有真实 Key、Token 或密码；
- 不提交根目录生成的 ZIP、原始个人材料和数据库备份；
- Render Blueprint 创建成功后，以控制台给出的实际公网域名复核三处地址变量；
- 修改任何 `VITE_` 变量后重新构建前端，因为 Vite 会在构建时写入这些值。

## 常见问题

### 8000 或 5173 端口被占用

先运行 `stop.bat`。若不是本项目占用，请关闭相应程序后重新启动；脚本不会自动结束未知进程。

### 后端无法访问

检查后端窗口中的报错，并访问 `http://127.0.0.1:8000/api/health`。确认 Python 版本不低于 3.10。

### 前端显示接口失败

确认前后端同时启动。开发环境应让 `VITE_API_BASE_URL` 保持为空，以使用 Vite 代理。

### 依赖损坏

删除可再生成的 `frontend/node_modules` 和 `backend/.venv`，再次运行 `start.bat`。

### 地图提示未配置 Key

这是正常降级状态。申请高德 Web JS API Key 后填写 `frontend/.env`，不要把真实 Key 提交到 Git。

### 深层页面刷新

开发服务器支持 Vue Router 回退。`render.yaml` 已把未知路径重写到 `index.html`，
直接打开或刷新二级、三级详情页不会返回平台级 404。

## 当前限制

- 高德在线地图需要使用者自己的 Web JS API Key 和安全密钥。
- 外部大模型需要使用者自己的合法 API 配置；未配置时使用本地检索问答。
- 受版权限制的视频不随仓库分发，相关页面使用来源明确的图文微课和媒体降级。
- Render 公网版本使用 SQLite 临时副本和只读后台；浏览、搜索、问答不受影响，
  但后台持久编辑与上传需要 Persistent Disk 或后续迁移 PostgreSQL。

## 后续规划

- 完善毛公山实地调研资料的持续采集、审核、来源标注与授权管理。
- 扩充红色人物、历史事件、研学路线、音视频讲解和无障碍内容。
- 建立自动化测试与持续集成流程，覆盖接口、资源完整性和多端页面回归。
- 在具备持久化存储条件后，将生产数据迁移至 PostgreSQL 或带持久磁盘的 SQLite。
- 完善贡献指南、Issue 模板和版本发布记录，逐步形成可协作维护的开源社区。

## 许可证

代码采用 [MIT License](LICENSE)。图片、历史资料和第三方内容仍遵循各自来源页面标注的版权与使用条件。

参与开发前请阅读 [贡献指南](CONTRIBUTING.md)；安全或隐私问题请按 [安全说明](SECURITY.md) 报告。
