# 保质期管家🤖 - Expiry Manager · 智能过期提醒与家庭共享

![Vue](https://img.shields.io/badge/Web-Vue_3-brightgreen)
![Express](https://img.shields.io/badge/Backend-Node.js_Express-lightgrey)
![Python](https://img.shields.io/badge/AI-Python-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

一款全栈物品保质期管理应用，支持**过期提醒、家庭共享**以及**自然语言 AI Agent** 交互管理。  
Vue 3 前端 + Node.js 后端 + Python 智能代理，让库存管理像聊天一样简单

## ✨ 功能特性

- 📦 **物品管理** — 添加、编辑、删除物品，记录购买日期、保质期、分类和状态。
- ⏰ **过期提醒** — 定时检查即将过期的物品，支持配置提前通知天数。
- 👨‍👩‍👧‍👦 **家庭共享** — 多成员共享物品清单，协同管理家庭库存。
- 🤖 **AI 自然语言管理** — 通过对话式 Agent 直接操作物品：查询、添加、搜索、删除等。
- 🔌 **多 LLM 提供商** — 支持硅基流动、智谱 AI、阿里云灵积，按需切换

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 后端 | Node.js + Express + NeDB（嵌入式 NoSQL） |
| AI Agent | Python + OpenAI SDK（支持硅基流动/智谱/阿里云灵积） |

## 快速启动

### 1. 后端

```bash
cd server
npm install
cp .env.example .env      # 编辑环境变量
npm run dev                # http://localhost:3000
```

### 2. 前端

```bash
cd client
npm install
npm run dev                # http://localhost:5173
```

### 3. AI Agent

```bash
pip install -r requirements.txt
cp .env.example .env       # 编辑 LLM 配置
python agent.py            # 交互式会话
```

## 项目结构

```
expiry-manager/
├── server/                 # 后端
│   ├── src/
│   │   ├── app.js         # 入口
│   │   ├── routes/        # API 路由
│   │   ├── middleware/     # 中间件
│   │   ├── services/      # 业务逻辑
│   │   ├── jobs/          # 定时任务
│   │   └── utils/         # 工具函数
│   └── data/              # NeDB 数据文件
├── client/                 # 前端
│   └── src/
│       ├── views/         # 页面组件
│       ├── components/    # 通用组件
│       ├── stores/        # Pinia 状态
│       ├── api/           # API 封装
│       └── router/        # 路由配置
├── agent.py               # AI Agent（Python）
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
└── AGENT_README.md        # Agent 使用说明
```

## 环境变量配置（.env）

```env
# LLM 提供商：siliconflow / zhipu / dashscope
LLM_PROVIDER=siliconflow

# 后端 API
API_BASE_URL=http://localhost:3000
USER_TOKEN=<从浏览器 LocalStorage 获取>

# 硅基流动（推荐，支持工具调用）
SILICONFLOW_API_KEY=sk-xxx
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Qwen/Qwen3-8B

# 智谱 AI
ZHIPU_API_KEY=xxx.xxx
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash

# 阿里云灵积
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
```

## API 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/items` | 获取物品列表 |
| GET | `/api/items?expiring=true&days=3` | 获取即将过期物品 |
| POST | `/api/items` | 添加物品 |
| DELETE | `/api/items/:id` | 删除物品 |
| PUT | `/api/items/:id` | 更新物品 |

### 物品字段

```json
{
  "name": "牛奶",
  "expiry_date": "2026-06-01",
  "category": "食品",
  "purchase_date": "2026-05-01",
  "shelf_life_days": 30,
  "status": "active"
}
```

## 🤖 AI Agent 详细说明

`agent.py` 利用 Function Calling 技术，将自然语言指令转化为后端 API 调用。支持功能：

- `get_all_items` — 查看所有物品
- `get_expiring_items` — 查看即将过期物品
- `search_items` — 搜索物品
- `add_item` — 添加物品
- `delete_item` — 删除物品

### 使用示例

```bash
python agent.py

# 输入示例：
#   "查看我的所有物品"
#   "有什么快过期了？"
#   "帮我添加牛奶，过期到6月1号"
#   "删除第3个物品"
```

支持三个 LLM 提供商：
- **硅基流动**（推荐）：Qwen3-8B，免费额度，工具调用稳定
- **智谱 AI**：GLM-4-Flash
- **阿里云灵积**：通义千问 Plus

切换 LLM 提供商:修改 .env 中的 LLM_PROVIDER 为对应值，并填入对应的 API Key


## 获取 USER_TOKEN

1. 启动前后端，在浏览器打开 `http://localhost:5173`
2. 注册/登录一个账号
3. F12 打开开发者工具 → Application → Local Storage
4. 复制 `token` 的值到 `.env` 的 `USER_TOKEN`
- ⚠️ Token 可能有过期时间，失效后请重新获取并更新。后续版本可考虑通过登录接口自动刷新

## 💾数据存储

后端使用 NeDB（嵌入式 NoSQL），数据文件位于 `server/data/`：

```
server/data/
├── users.db
├── items.db
├── familyMembers.db
├── notifications.db
└── reminderSettings.db
```

## 🤝 贡献指南

欢迎提交 Issue 或 PR！请遵循以下流程：
1.Fork 本仓库
2.创建特性分支 (git checkout -b feature/AmazingFeature)
3.提交更改 (git commit -m 'Add some AmazingFeature')
4.推送到分支 (git push origin feature/AmazingFeature)
5.开启 Pull Request

## 📄 许可证
本项目基于 MIT 许可证开源，详情见 LICENSE 文件
```
💡 更多 AI Agent 的高级用法和自定义工具开发，请查看 AGENT_README.md
```
