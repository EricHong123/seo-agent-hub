# SEO Agent Hub

SEO Agent + 内容分发系统 — AI 内容生产与多平台分发一体化平台。

```
研究关键词 → AI 写作 → SEO 优化 → 多格式导出 → 一键分发到抖音/B站/小红书/快手...
```

## 架构

```
seo-agent-hub/
├── apps/
│   ├── seo-agent/          # AI 内容引擎 (git submodule)
│   ├── social-upload/      # 多平台分发引擎 (git submodule)
│   └── dashboard/          # 统一 Web UI
├── packages/
│   └── content-bridge/     # 共享类型 + API 客户端
├── docker-compose.yml
└── Makefile
```

| 模块 | 端口 | 职责 |
|------|------|------|
| **seo-agent** | 8000 | AI 内容引擎 — 22工具，关键词研究/SERP分析/文章写作/SEO评分/知识库 |
| **social-upload** | 8001 | 多平台分发 — 抖音/B站/小红书/快手/视频号/百家号/TikTok |
| **dashboard** | 3000 | 统一操作界面（规划中） |
| **content-bridge** | — | Python 包，共享类型定义和 API 客户端 |

## 快速开始

```bash
# 1. 克隆（含子模块）
git clone --recurse-submodules https://github.com/EricHong123/seo-agent-hub.git
cd seo-agent-hub

# 2. 安装依赖
make install

# 3. 配置 SEO Agent
cp apps/seo-agent/.env.example apps/seo-agent/.env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 4. 启动
make start
# SEO Agent: http://localhost:8000
```

## 使用

```bash
# 1. SEO Agent 生成内容
curl -X POST http://localhost:8000/api/agent/run \
  -H 'Content-Type: application/json' \
  -d '{"task":"写一篇 standing desk 选购指南"}'

# 2. 导出给 SAU
curl "http://localhost:8000/api/content/export/latest?format=sau"

# 3. SAU 发布到抖音
sau douyin upload-video --account myaccount --file video.mp4 \
  --content-url http://localhost:8000/api/content/export/latest?format=sau
```

## 开发

```bash
# 更新子模块到最新
git submodule update --remote

# 重置所有数据
make reset

# 查看日志
make logs

# Docker 一键启动全部
make start-full
```

## 子模块

| 模块 | 仓库 | 版本 |
|------|------|------|
| seo-agent | [EricHong123/seo-ai-agent](https://github.com/EricHong123/seo-ai-agent) | main |
| social-upload | [EricHong123/social-auto-upload](https://github.com/EricHong123/social-auto-upload) | main |

## License

MIT
