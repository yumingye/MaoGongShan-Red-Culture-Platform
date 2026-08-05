# GitHub 上传整理检查报告

## 整理时间

2026-07-19

## 最终目录

```text
maogongshan-github-ready
```

## 已整理内容

- 重写根目录 `README.md`，补充项目背景、功能、技术栈、启动方式、环境变量、数据库、地图、问答、截图目录和常见问题。
- 新增 MIT `LICENSE`，版权信息为 `Yu Mingye`。
- 重写 `.gitignore`，排除依赖、缓存、构建产物、日志、真实环境变量、原始 Word 文档和私有目录。
- 新增根目录 `.env.example`。
- 重写 `frontend/.env.example` 和 `backend/.env.example`。
- 重写 `start.bat`、`start_backend.ps1`、`start_frontend.ps1`，全部使用相对路径。
- 后端管理员用户名、密码、Token 和数据库路径改为环境变量读取。
- 前端 API 地址支持 `VITE_API_BASE_URL`，默认仍可使用 Vite 代理。
- 修复后台管理页中文乱码。
- 新增 `docs/screenshots/.gitkeep`，预留项目截图目录。

## 排除内容

最终 GitHub-ready 目录不包含：

- `node_modules`
- `backend/.venv`
- `frontend/dist`
- `.npm-cache`
- `__pycache__`
- `.git`
- `.env`
- 日志文件
- 原始 Word 文档
- 私有目录

## 敏感信息检查

- 未提交真实高德地图 Key。
- 未提交真实大模型 API Key。
- 未提交真实 `.env` 文件。
- 未提交身份证号、手机号、私人邮箱、家庭住址等个人敏感信息。
- 管理员默认账号仅用于本地演示，正式部署前应通过环境变量修改。

## 体积检查

- 最终目录约 25MB。
- 未发现超过 50MB 的单文件。
- SQLite 数据库约 3.1MB，可直接随仓库用于本地演示。

## 测试结果

在原项目和 GitHub-ready 目录均执行了检查：

```bash
python -m py_compile backend/app.py backend/augment_final_rounds.py backend/augment_iteration_data.py backend/enrich_competition_data.py backend/finalize_platform_content.py backend/import_word.py
npm install
npm run check
npm run build
npm audit --omit=dev
```

结果：

- 后端 Python 编译通过。
- 前端依赖安装通过。
- 前端质量检查通过。
- 前端生产构建通过。
- npm 运行依赖审计为 0 个漏洞。
- API 和主要路由检查通过。

## 第三方服务说明

- 高德地图需要用户在 `frontend/.env` 中填写 `VITE_AMAP_KEY` 和 `VITE_AMAP_SECURITY_CODE`。
- 未配置高德地图 Key 时，地图页自动显示本地静态导览。
- 大模型 API 为可选配置；未配置时使用本地检索式问答。

## 上传建议

可直接将 `maogongshan-github-ready` 目录作为 GitHub 仓库根目录上传。上传前不需要复制 `node_modules` 或虚拟环境。
