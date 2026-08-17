# 生产部署指南（Render）

本项目使用同一个 Render Blueprint 部署前后端：

```text
浏览器
  └─ HTTPS → Render Static Site（Vue 3 / Vite）
                 └─ HTTPS API → Render Web Service（FastAPI）
                                      └─ SQLite 只读运行副本
```

## 已配置的公网服务

| 服务 | 公网地址 |
| --- | --- |
| 前端 | `https://maogongshan-red-culture-web-yumingye.onrender.com` |
| 后端 | `https://maogongshan-red-culture-api-yumingye.onrender.com` |

仓库根目录的 `render.yaml` 是唯一需要应用的 Blueprint。服务名沿用项目历史配置，Render 已存在同名服务时会更新该服务，不会创建重复名称。

## Blueprint 配置

后端 Web Service：

- Runtime：Python 3
- Build Command：`pip install --upgrade pip && pip install -r backend/requirements.txt`
- Start Command：`uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- Health Check：`/api/health`
- `ENVIRONMENT=production`
- `DATABASE_URL=/tmp/maogongshan.db`
- `READ_ONLY_MODE=true`
- CORS 仅允许正式 Render 前端 Origin

前端 Static Site：

- Root Directory：`frontend`
- Build Command：`npm ci && npm run build`
- Publish Directory：`dist`
- `VITE_API_BASE_URL=https://maogongshan-red-culture-api-yumingye.onrender.com`
- `VITE_PUBLIC_READ_ONLY=true`
- 所有 Vue Router 深层路径 Rewrite 到 `/index.html`

Vite 生产构建会拒绝 `localhost` 和 `127.0.0.1` API 地址。本地开发仍使用 `.env.development` 的本地代理，不影响开发体验。

## 部署前验证

在仓库根目录执行：

```powershell
cd frontend
$env:VITE_API_BASE_URL="https://maogongshan-red-culture-api-yumingye.onrender.com"
npm ci
npm run lint
npm run test
npm run build
npm run check:deploy
```

后端测试使用本地开发地址仅作为测试入口，不会写入生产构建：

```powershell
backend\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
backend\.venv\Scripts\python.exe backend\check_api_contract.py
```

## 应用 Blueprint

1. 打开 [Render Dashboard](https://dashboard.render.com/)。
2. 打开已连接仓库的 Blueprint；如果还没有 Blueprint，选择 **New → Blueprint**，连接 `yumingye/MaoGongShan-Red-Culture-Platform`。
3. Blueprint Path 使用仓库根目录的 `render.yaml`。
4. 点击 **Apply** 或 **Sync**，等待两个服务均显示 `Live`。

Render 自动提供 `PORT`，不要在控制台写死端口。公开实例默认只读，管理员密钥由 Render 生成且不进入仓库。

## 启用 RAG 大模型

知识助手默认可使用 SQLite 本地检索；要启用真正的大模型组织回答，只需在现有后端服务的 **Environment** 中设置以下服务端变量，无需修改或重新构建前端：

| 变量 | 值 |
| --- | --- |
| `LLM_PROVIDER` | 提供商标识，例如 `openai-compatible` |
| `LLM_BASE_URL` | OpenAI 兼容接口根地址，例如以 `/v1` 结尾的 HTTPS 地址 |
| `LLM_MODEL` | 该提供商实际可用的模型 ID |
| `LLM_API_KEY` | 仅保存在 Render 后端的 Secret，不得写入仓库或前端变量 |

模型异常、超时或返回格式不兼容时，接口会自动降级为本地知识库检索回答，并继续返回可核验来源。`LLM_TIMEOUT_SECONDS`、`LLM_MAX_CONTEXT_CHARS` 和 `LLM_MAX_TOKENS` 已由 Blueprint 配置。

## 上线验收

依次验证：

- 前端 `/` 首页可打开。
- `/party-history`、`/scenery`、`/research`、`/map`、`/chat` 可直接打开和刷新。
- `/assets/...` 图片、音频和视频返回成功。
- 后端 `/api/health` 显示 `status=ok`、`database=connected`。
- `/api/home`、`/api/search`、`/api/chat` 正常返回。
- 浏览器 Network 不包含 `localhost`、`127.0.0.1`、Mixed Content 或 CORS 错误。

在线高德地图需要在 Render 前端服务中配置 `VITE_AMAP_KEY` 和 `VITE_AMAP_SECURITY_CODE`；未配置时页面使用项目内置的静态导览，不依赖本机路径。

## 数据策略

Render 免费实例的本地文件系统不持久。公开站使用仓库中的 `database/maogongshan.db` 作为种子，并在启动时复制到 `/tmp/maogongshan.db`，适合长期只读展示。需要在线后台编辑时，应挂载 Persistent Disk 或迁移到 PostgreSQL。

`netlify.toml` 和 `frontend/public/_redirects` 仅保留为备用前端托管配置，不参与 Render 主部署链路。
