# 生产部署指南（Netlify + Render）

本项目采用前后端分离部署：

```text
浏览器
  └─ HTTPS → Netlify（Vue 3 / Vite 静态前端）
                 └─ HTTPS API → Render（FastAPI）
                                      └─ SQLite 只读运行副本
```

推荐顺序为“部署 Render 后端 → 配置 Netlify API 地址并部署前端 → 将 Netlify 域名回填到 Render CORS → 完整验收”。

## 一、部署前验证

在仓库根目录执行：

```powershell
cd frontend
$env:VITE_API_BASE_URL="https://your-render-service.onrender.com"
npm ci
npm run lint
npm run build
npm run check:deploy
```

生产构建会拒绝空 API 地址以及 `localhost`、`127.0.0.1` 地址，避免将本地接口发布到公网。

## 二、后端部署到 Render

### 使用 Blueprint

1. 登录 [Render Dashboard](https://dashboard.render.com/)。
2. 选择 **New → Blueprint**，连接 GitHub 仓库 `yumingye/MaoGongShan-Red-Culture-Platform`。
3. Blueprint 文件使用仓库根目录的 `render.yaml`。
4. 首次创建时，Render 会要求填写 `CORS_ORIGINS`。前端域名尚未生成时可暂填 `https://placeholder.invalid`，稍后再修改。
5. Apply Blueprint，等待 `/api/health` 健康检查通过。
6. 记录后端公网地址，例如：

   ```text
   https://maogongshan-red-culture-api-yumingye.onrender.com
   ```

`render.yaml` 已配置：

| Render 设置 | 值 |
| --- | --- |
| Runtime | Python 3 |
| Root Directory | 仓库根目录 |
| Build Command | `pip install --upgrade pip && pip install -r backend/requirements.txt` |
| Start Command | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| Health Check | `/api/health` |
| Environment | `production` |
| Database | `/tmp/maogongshan.db` |
| Public mode | `READ_ONLY_MODE=true` |

Render 自动提供 `PORT`，不要硬编码公网端口。公开展示使用只读模式；管理员密码和 Token 由 Render 生成，不写入仓库。

### 后端检查

```powershell
Invoke-RestMethod https://你的Render域名/api/health
```

预期返回包含：

```json
{
  "status": "ok",
  "database": "connected",
  "read_only": true
}
```

## 三、前端部署到 Netlify

### 通过 GitHub 持续部署

1. 登录 [Netlify](https://app.netlify.com/)。
2. 选择 **Add new project → Import an existing project → GitHub**。
3. 授权并选择仓库 `yumingye/MaoGongShan-Red-Culture-Platform`。
4. 仓库根目录的 `netlify.toml` 已提供以下设置，无需在控制台重复覆盖：

   | Netlify 设置 | 值 |
   | --- | --- |
   | Base directory | `frontend` |
   | Build command | `npm run build` |
   | Publish directory | `dist`（相对 `frontend`） |
   | Node.js | `22.16.0` |

5. 在 **Project configuration → Environment variables** 添加：

   ```text
   VITE_API_BASE_URL=https://你的Render后端域名
   VITE_PUBLIC_READ_ONLY=true
   ```

6. 可选地图变量：

   ```text
   VITE_AMAP_KEY=你的高德Web端Key
   VITE_AMAP_SECURITY_CODE=你的高德安全密钥
   ```

7. 点击 Deploy。部署成功后记录 Netlify 生成的公网地址：

   ```text
   https://你的站点名.netlify.app
   ```

Vite 的 `VITE_*` 变量会在构建时写入浏览器代码，修改后必须重新部署。API 地址应使用完整 HTTPS Origin，不包含 `/api` 和末尾 `/`。

### 使用 Netlify CLI（可选）

在 Netlify CLI 已登录时，从仓库根目录执行：

```powershell
npx netlify-cli init
npx netlify-cli env:set VITE_API_BASE_URL https://你的Render后端域名
npx netlify-cli env:set VITE_PUBLIC_READ_ONLY true
npx netlify-cli deploy --build --prod
```

首次执行会要求登录 Netlify 并授权 GitHub 仓库。

## 四、Vue Router 刷新规则

项目采用 History 路由。Netlify 必须在找不到静态文件时返回 `index.html`，否则直接访问或刷新 `/party-history`、`/scenery` 等地址会出现 404。

项目同时提供：

- 根目录 `netlify.toml` 中的 `/* → /index.html (200)` 重写。
- `frontend/public/_redirects`，构建后会复制到 `dist/_redirects`。

规则不会覆盖真实存在的 JS、CSS 和图片文件。部署后应直接打开并刷新以下地址：

```text
https://你的站点名.netlify.app/party-history
https://你的站点名.netlify.app/scenery
https://你的站点名.netlify.app/research
```

## 五、回填 Render CORS

获得 Netlify 公网域名后，在 Render Service → Environment 更新：

```text
CORS_ORIGINS=https://你的站点名.netlify.app
ENVIRONMENT=production
```

多个正式域名使用英文逗号分隔：

```text
CORS_ORIGINS=https://你的站点名.netlify.app,https://www.example.org
```

不要使用 `*` 或不受限的 `.*`。更新环境变量后重新部署 Render 服务。

## 六、上线验收

### CORS 预检

```powershell
$headers = @{
  Origin = "https://你的站点名.netlify.app"
  "Access-Control-Request-Method" = "GET"
}
Invoke-WebRequest -Method Options -Headers $headers -Uri "https://你的Render域名/api/home"
```

`Access-Control-Allow-Origin` 应与 Netlify Origin 完全一致。

### 浏览器检查

- 首页、党史、风景、调研和详情页可以打开并刷新。
- Network 中 API 请求指向 HTTPS Render 地址，不包含 localhost。
- `/assets/...` 图片返回 200。
- Console 中没有 CORS、Mixed Content 或资源 404。
- `/api/health` 显示数据库已连接。

## 七、SQLite 说明

生产环境首次启动时，后端会将 `database/maogongshan.db` 复制到 `/tmp/maogongshan.db`。该方式适合公开只读展示，但容器重启后运行时写入不会保留。

若未来需要后台持久编辑，应挂载 Render Persistent Disk，或迁移到 PostgreSQL，并增加数据库迁移、备份和权限审计。

## 八、常见问题

### Netlify 构建提示必须设置 VITE_API_BASE_URL

在 Netlify 的 **Project configuration → Environment variables** 添加 Render HTTPS 地址，然后重新部署。

### 页面能显示但接口失败

先检查 Render `/api/health`，再检查 Netlify 的 `VITE_API_BASE_URL`。变量修改后必须触发新的前端构建。

### 二级页面刷新返回 404

确认 Netlify 使用仓库根目录的 `netlify.toml`，并在 Deploy File Explorer 中确认发布产物存在 `_redirects`。

### 浏览器提示 CORS

Render 的 `CORS_ORIGINS` 必须等于地址栏中的完整 Netlify Origin，包括 `https://`，但不包含路径和末尾 `/`。

### Render 显示服务未监听端口

确认启动命令为：

```text
uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```
