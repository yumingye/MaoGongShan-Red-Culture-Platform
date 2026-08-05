# Render 公网部署专项报告

日期：2026-07-30

## 实际修改

1. 确认前端为 Vue 3 + Vite，后端为 FastAPI + SQLite。
2. 将生产 API 地址收口到 `VITE_API_BASE_URL` / `VITE_API_HOST`。
3. 后端监听改为 `0.0.0.0:$PORT`，兼容 Render 动态端口。
4. CORS 改为精确来源列表和 Render HTTPS 主机规则。
5. 公开 SQLite 作为种子数据库，公网默认运行只读副本。
6. 后台公开部署不显示默认账号，未配置凭据时拒绝登录。
7. 新增 `render.yaml`，定义 Static Site、Web Service、健康检查和 SPA Rewrite。
8. 新增部署静态检查 `npm run check:deploy`。
9. 打包脚本纳入 `render.yaml` 和可公开的环境变量示例文件。

## 修复的问题

| 问题 | 修复 |
| --- | --- |
| 公网前端可能请求访问者本机 | 生产 API 地址由 Render 注入 |
| 后端只适配固定本地端口 | 优先读取 `PORT` 并绑定 `0.0.0.0` |
| 默认管理员凭据不适合公开仓库 | 删除可用默认值，公开站启用只读模式 |
| SQLite 普通文件系统不持久 | 使用种子数据库和只读运行副本 |
| 数据库异常导致服务判定离线 | 健康接口独立报告 Web 与数据库状态 |
| 深层路由刷新可能返回平台 404 | Static Site 配置 `/*` Rewrite 到 `/index.html` |
| 打包目录遗漏 Blueprint | `render.yaml` 加入打包和结构验证 |

## 实际测试

| 检查项 | 结果 |
| --- | --- |
| Python 语法编译 | 通过 |
| Render 后端启动命令 | 通过 |
| 种子数据库复制 | 通过 |
| 正常数据库健康检查 | 200 |
| 异常数据库健康检查 | 200，状态为 `unavailable` |
| 配置来源 CORS | 通过 |
| 未授权来源预检 | 400 |
| 公开只读限制 | 通过 |
| `npm ci` | 通过，0 个漏洞 |
| `npm run build` | 通过，转换 1760 个模块 |
| `npm run check:deploy` | 通过 |
| 核心与深层路由 | 通过 |
| API 断开降级 | 通过 |
| 坏图兜底 | 通过 |
| 移动端菜单 | 通过 |

浏览器验收分为核心路由与生成链接遍历、真实交互、接口断开、慢网络、坏图和移动端菜单。自动化脚本对高频硬刷新导致的偶发异步分包首载失败执行一次受控重试；第二次仍失败时测试保持失败。

## 数据与第三方限制

- Render 公网版本默认提供浏览、检索、地图静态导览和本地检索问答。
- 高德在线地图需要 `VITE_AMAP_KEY` 和 `VITE_AMAP_SECURITY_CODE`。
- 外部大模型需要后端 `LLM_PROVIDER`、`LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`。
- 持久后台编辑需要 Render Persistent Disk 或迁移到云数据库；默认只读模式不会误报写入成功。
