# WuwaWebTool

鸣潮（Wuthering Waves）角色面板 Web 查看器 — 将 [XutheringWavesUID](https://github.com/Loping151/XutheringWavesUID) 从 GsuidCore 机器人框架中剥离为独立 Web 服务，无需部署 NoneBot/GsuidCore 环境，通过浏览器即可查询角色面板、声骸评分等信息。

## 功能

- **库街区登录** — 支持手机号+验证码 / 邮箱+密码两种登录方式
- **角色列表** — 查看所有已解锁角色，按评分/等级/属性排序和搜索
- **角色面板** — 查看角色详情：属性、武器、技能、共鸣链、皮肤
- **声骸评分** — 每个声骸独立评分（SSS ~ C），副词条权重着色，套装效果展示
- **按需加载** — 仅在点击角色时请求详情和评分，本地缓存避免重复请求
- **单角色刷新** — 面板内一键刷新当前角色的数据
- **导出图片** — 将角色面板导出为 PNG 图片

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python FastAPI + uvicorn |
| 前端 | 原生 HTML/CSS/JS（无框架） |
| 评分引擎 | XutheringWavesUID 编译模块（.pyd） |
| 缓存 | 前端 localStorage + 后端 SQLite |

## 快速开始

### 本地运行

```bash
cd backend
pip install -r requirements.txt
python main.py
```

启动后访问 `http://localhost:8000`，首次启动会自动从 CDN 下载游戏资源和评分模块。

> 可通过环境变量 `PORT` 指定端口，`WUWA_DATA_PATH` 指定数据目录。

### Docker

**预构建镜像（推荐）：**

```bash
docker pull ghcr.io/eventhorizonsky/wuwawebtool:latest
docker run -p 8000:8000 \
  -v wuwa-data:/app/backend/data \
  ghcr.io/eventhorizonsky/wuwawebtool:latest
```

**本地构建：**

```bash
docker build -f backend/Dockerfile -t wuwawebtool .
docker run -p 8000:8000 -v wuwa-data:/app/backend/data wuwawebtool
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  wuwawebtool:
    image: ghcr.io/eventhorizonsky/wuwawebtool:latest
    ports:
      - "8000:8000"
    volumes:
      - wuwa-data:/app/backend/data
    restart: unless-stopped

volumes:
  wuwa-data:
```

```bash
docker compose up -d
```

> **数据持久化**：`/app/backend/data` 目录存放 CDN 下载的游戏资源和评分模块（.pyd），不映射的话每次容器重建都会重新下载（~数百 MB）。映射到宿主机卷或目录后，后续启动只需增量检查，秒级完成。

### 免费平台部署

项目支持一键部署到以下免费托管平台：

**Railway** — 点击下方按钮一键部署：

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/eventhorizonsky/WuwaWebTool)

> 首次使用需授权 Railway 访问 GitHub。部署会自动识别 `railway.json` 和 `backend/Dockerfile`，完成后分配 `*.up.railway.app` 域名。
>
> **Railway 数据持久化**：在 Railway Dashboard → 你的服务 → Settings → Volumes，添加挂载路径 `/app/backend/data`，否则每次重新部署都需要重新下载资源。
>
> 若你 Fork 了仓库，请将按钮链接中的 `eventhorizonsky` 替换为你的 GitHub 用户名。

**Render** — Fork 本仓库后，在 Render Dashboard 选择 "Blueprint" 即可自动读取 `render.yaml` 部署。

> **Render 数据持久化**：免费套餐不含持久磁盘，每次重新部署会重新下载资源（启动时自动完成）。

**其他支持 Docker 的平台**（Fly.io / Koyeb / Northflank 等）：

```bash
# Fly.io 示例（含持久卷）
fly launch --dockerfile backend/Dockerfile
fly volumes create wuwa_data --size 1
# 在 fly.toml 中添加:
# [mounts]
#   source = "wuwa_data"
#   destination = "/app/backend/data"
fly deploy
```

## 项目结构

```
WuwaWebTool/
├── frontend/           # 前端静态页面
│   ├── index.html      # 角色列表页
│   ├── panel.html      # 角色面板详情页
│   ├── css/style.css   # 样式
│   └── js/api.js       # API 客户端 & 缓存逻辑
├── backend/
│   ├── main.py         # FastAPI 入口
│   ├── api/            # API 路由（auth, game_data, score）
│   ├── core/           # 核心逻辑（评分、缓存、资源下载）
│   └── login_pages/    # 登录页面模板
└── README.md
```

## 致谢

本项目修改自 **[Loping151/XutheringWavesUID](https://github.com/Loping151/XutheringWavesUID)**。

衷心感谢原项目作者 [Loping151](https://github.com/Loping151) 以及 XutheringWavesUID 社区的贡献以及提供的CDN服务。

本项目将原 GsuidCore 插件改造为独立 Web 服务，前端从 Pillow 渲染图改为纯 HTML/CSS 展示，并优化了缓存策略以减少对官方 API 的请求频率。
