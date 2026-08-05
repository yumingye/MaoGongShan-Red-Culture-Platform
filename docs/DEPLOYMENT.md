# 生产部署指南

本指南使用以下部署架构：

```text
浏览器
  └─ HTTPS → Vercel（Vue 3 / Vite 静态前端）
                 └─ HTTPS API → Render 或 Railway（FastAPI）
                                      └─ SQLite 运行副本
```

推荐按“部署后端 → 记录 API 地址 → 部署前端 → 回填后端 CORS → 验证”的顺序操作。

## 一、部署前检查

```powershell
git status
cd frontend
$env:VITE_API_BASE_URL="https://example-api.onrender.com"
npm ci
npm run build
npm run check:deploy
```

生产构建会拒绝空 API 地址以及 `localhost`、`127.0.0.1` 地址，避免把本地依赖带到线上。

## 二、后端部署到 Render

### 方式 A：使用 Blueprint

1. 登录 [Render Dashboard](https://dashboard.render.com/)。
2. 选择 **New → Blueprint**，连接 GitHub 仓库 `yumingye/MaoGongShan-Red-Culture-Platform`。
3. Blueprint Path 使用根目录的 `render.yaml`。
4. Render 会创建 `maogongshan-red-culture-api-yumingye` Web Service。
5. `CORS_ORIGINS` 暂时填写预计使用的 Vercel 域名；获得最终域名后再更新。
6. Apply Blueprint，等待 `/api/health` 健康检查通过。
7. 记录 Render 给出的 API 地址，例如：

   ```text
   https://maogongshan-red-culture-api-yumingye.onrender.com
   ```

`render.yaml` 已配置：

```text
Build Command: pip install --upgrade pip && pip install -r backend/requirements.txt
Start Command: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
Health Check: /api/health
```

### 方式 B：手动创建 Render Web Service

| Render 设置 | 值 |
| --- | --- |
| Runtime | Python 3 |
| Root Directory | 留空，即仓库根目录 |
| Build Command | `pip install --upgrade pip && pip install -r backend/requirements.txt` |
| Start Command | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/api/health` |

环境变量：

```text
PYTHON_VERSION=3.12.8
ENVIRONMENT=production
SERVICE_NAME=maogongshan-api
DATABASE_URL=/tmp/maogongshan.db
READ_ONLY_MODE=true
CORS_ORIGINS=https://你的前端域名.vercel.app
```

公网只读展示不需要启用管理员写入。若确实需要管理功能，再在 Render 控制台生成强随机 `ADMIN_PASSWORD` 和 `ADMIN_TOKEN`，不要写入仓库。

## 三、后端部署到 Railway（Render 的替代方案）

1. 登录 [Railway](https://railway.com/)，创建 New Project。
2. 选择 **Deploy from GitHub repo**，连接本仓库。
3. Railway 会读取根目录 `railway.toml`。
4. 在 Variables 中添加：

   ```text
   ENVIRONMENT=production
   SERVICE_NAME=maogongshan-api
   DATABASE_URL=/tmp/maogongshan.db
   READ_ONLY_MODE=true
   CORS_ORIGINS=https://你的前端域名.vercel.app
   ```

5. 不要手动设置 `PORT`；Railway 会自动注入。
6. 打开 Service → Settings → Networking，点击 **Generate Domain**。
7. 记录生成的 `https://....up.railway.app` 地址并访问 `/api/health`。

`railway.toml` 已将服务绑定到 `0.0.0.0:$PORT`，并配置 `/api/health` 健康检查。

## 四、前端部署到 Vercel

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)。
2. 选择 **Add New → Project**，导入 GitHub 仓库。
3. 设置：

   | Vercel 设置 | 值 |
   | --- | --- |
   | Framework Preset | Vite |
   | Root Directory | `frontend` |
   | Install Command | `npm ci` |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |

4. 在 Production 环境变量中添加：

   ```text
   VITE_API_BASE_URL=https://你的后端公网地址
   VITE_PUBLIC_READ_ONLY=true
   ```

5. 可选地图配置：

   ```text
   VITE_AMAP_KEY=你的高德Web端Key
   VITE_AMAP_SECURITY_CODE=你的高德安全密钥
   ```

6. 点击 Deploy。`frontend/vercel.json` 会处理 Vue Router 深层链接，并为静态资源设置缓存与安全响应头。
7. 记录最终 Vercel Origin，例如 `https://your-project.vercel.app`。Origin 不包含末尾 `/`。

也可以在已登录 Vercel CLI 后执行：

```powershell
npx vercel --cwd frontend --prod
```

首次 CLI 部署会要求关联账户和项目。生产环境变量应优先在 Vercel Dashboard 中配置。

## 五、回填 CORS

获得最终 Vercel 域名后，返回 Render 或 Railway，把后端变量更新为：

```text
CORS_ORIGINS=https://your-project.vercel.app
ENVIRONMENT=production
```

多个正式域名使用英文逗号分隔：

```text
CORS_ORIGINS=https://your-project.vercel.app,https://www.example.org
```

如需允许同一项目的 Vercel Preview 域名，可额外配置受限正则；不要使用允许所有来源的 `.*`：

```text
CORS_ORIGIN_REGEX=^https://your-project(?:-[a-z0-9-]+)?\.vercel\.app$
```

更新变量后重新部署后端。

## 六、上线验证

### 1. 后端健康检查

```powershell
Invoke-RestMethod https://你的后端域名/api/health
```

预期包含：

```json
{
  "status": "ok",
  "database": "connected"
}
```

### 2. CORS 预检

```powershell
$headers = @{
  Origin = "https://你的前端域名.vercel.app"
  "Access-Control-Request-Method" = "GET"
}
Invoke-WebRequest -Method Options -Headers $headers -Uri "https://你的后端域名/api/home"
```

响应头中的 `Access-Control-Allow-Origin` 应等于前端 Origin。

### 3. 页面验证

依次检查：

- `/` 首页是否正常显示图片和统计数据。
- `/party-history`、`/scenery`、`/research` 是否可直接打开和刷新。
- `/assets/...` 图片是否返回 200。
- 浏览器 Network 中 API 是否请求 HTTPS 后端，而不是 localhost。
- Console 中是否存在 CORS、Mixed Content 或资源 404 错误。

## 七、数据库策略

当前生产配置使用公开种子 SQLite：首次启动时将 `database/maogongshan.db` 复制到 `/tmp/maogongshan.db`。这种方式适合只读展示，但运行时写入不会永久保存。

需要后台持久编辑时：

- Render：挂载 Persistent Disk，并把 `DATABASE_URL` 指向挂载目录。
- Railway：挂载 Volume，并把 `DATABASE_URL` 指向 Volume 路径。
- 多实例或长期协作：迁移到 PostgreSQL，并增加迁移、权限、备份和审计机制。

## 八、常见问题

### Vercel 构建提示必须设置 VITE_API_BASE_URL

在 Vercel Project → Settings → Environment Variables 中添加完整 HTTPS 后端地址，然后 Redeploy。

### 页面能打开但所有接口失败

先访问后端 `/api/health`，再确认 Vercel 的 `VITE_API_BASE_URL`。Vite 环境变量在构建时写入，修改后必须重新部署前端。

### 浏览器提示 CORS

后端 `CORS_ORIGINS` 必须包含浏览器地址栏中的完整 Origin，包括 `https://`，但不包含路径和末尾 `/`。

### 二级页面刷新返回 404

确认 Vercel 项目的 Root Directory 是 `frontend`，且部署读取了 `frontend/vercel.json` 中的 SPA Rewrite。

### Render 或 Railway 显示服务未监听端口

确认启动命令为：

```text
uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```
