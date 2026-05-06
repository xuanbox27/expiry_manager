# 保质期管家 AI Agent 使用说明

## 功能

通过自然语言对话管理你的保质期物品：
- "我还有哪些牛奶快过期？"
- "帮我添加一盒牛奶，5月10号过期"
- "删除那个过期的面包"

## 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 USER_TOKEN

1. 启动后端服务：
   ```bash
   cd server
   npm start
   ```

2. 启动前端并登录：
   ```bash
   cd client
   npm run dev
   ```
   用浏览器访问 http://localhost:5173，登录你的账号。

3. 获取 Token（任选一种）：
   - **方法1**：打开浏览器开发者工具 → Application → Local Storage → 找到 `token` 键，复制其值。
   - **方法2**：使用 curl 命令登录获取：
     ```bash
     curl -X POST http://localhost:3000/api/auth/login \
       -H "Content-Type: application/json" \
       -d '{"email": "你的邮箱", "password": "你的密码"}'
     ```
     从返回的 JSON 中复制 `token` 字段。

4. 编辑 `.env` 文件（复制 `.env.example`）：
   ```bash
   cp .env.example .env
   ```
   然后填入你的 `USER_TOKEN` 和 `OPENAI_API_KEY`。

### 3. 运行 Agent

```bash
python agent.py
```

## 使用示例

```
==================================================
   保质期管家 AI Agent
   输入 'exit' 或 'quit' 退出
==================================================

你: 我有哪些物品快过期了？
[调用工具: get_expiring_items]
AI: 您有2个物品即将在3天内过期：
1. 鲜牛奶 - 过期日期：2025-05-10（剩余1天）
2. 草莓 - 过期日期：2025-05-09（今天到期）

你: 帮我添加一盒酸奶，明天过期
[调用工具: add_item]
AI: 已成功添加「酸奶」，过期日期设置为2025-05-10。

你: 删除那个过期的面包
[调用工具: search_items]
[调用工具: delete_item]
AI: 已找到并删除「面包」（ID: abc123），操作成功。
```

## 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `OPENAI_API_KEY` | 是 | OpenAI API Key，或兼容接口的 Key |
| `USER_TOKEN` | 是 | JWT Token，从浏览器或登录接口获取 |
| `OPENAI_BASE_URL` | 否 | 兼容接口地址（如 DeepSeek: `https://api.deepseek.com/v1`） |
| `API_BASE_URL` | 否 | 后端地址，默认 `http://localhost:3000` |
| `MODEL` | 否 | 模型名称，默认 `gpt-3.5-turbo` |

## 兼容 DeepSeek / 通义千问

### DeepSeek
```env
OPENAI_API_KEY=your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-chat
```

### 通义千问 (Qwen)
```env
OPENAI_API_KEY=your-qwen-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL=qwen-turbo
```

## 注意事项

1. **Token 过期**：如果返回 401 错误，请重新登录获取新 Token 并更新 `.env`。
2. **日期格式**：所有日期统一为 `YYYY-MM-DD` 格式。
3. **Windows 兼容**：脚本使用 `os.path` 处理路径，兼容 Windows。
4. **Token 安全**：不要将包含真实 Token 的 `.env` 文件提交到 Git。建议添加 `.gitignore`：
   ```
   .env
   data/
   *.db
   ```

## 故障排查

| 问题 | 解决方案 |
|------|------|
| `未找到 USER_TOKEN` | 检查 `.env` 文件，确保已填入正确的 Token |
| `401 Unauthorized` | Token 过期，重新登录并获取新 Token |
| `ModuleNotFoundError` | 运行 `pip install -r requirements.txt` |
| 连接拒绝 | 确保后端服务 (`npm start`) 正在运行 |
