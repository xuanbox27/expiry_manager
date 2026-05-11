# 保质期管家（Expiry Manager）

全栈物品保质期管理应用，支持过期提醒、家庭共享、自然语言 AI Agent 管理。

## 技术栈

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

## AI Agent 功能

`agent.py` 支持自然语言管理物品，基于 Function Calling 实现：

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

切换方式：修改 `.env` 中的 `LLM_PROVIDER` 即可。

## 获取 USER_TOKEN

1. 启动前后端，在浏览器打开 `http://localhost:5173`
2. 登录账号
3. F12 打开开发者工具 → Application → Local Storage
4. 复制 `token` 的值到 `.env` 的 `USER_TOKEN`

## 数据存储

后端使用 NeDB（嵌入式 NoSQL），数据文件位于 `server/data/`：

```
server/data/
├── users.db
├── items.db
├── familyMembers.db
├── notifications.db
└── reminderSettings.db
```
