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

```bash
cd backend
pip install -r requirements.txt
python main.py
```

启动后访问 `http://localhost:8000`，首次启动会自动从 CDN 下载游戏资源和评分模块。

> 可通过环境变量 `PORT` 指定端口，`WUWA_DATA_PATH` 指定数据目录。

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
