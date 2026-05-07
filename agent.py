import os
import sys
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# 修复 Windows 下中文编码问题
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', buffering=1)

# 强制重新加载 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 读取配置
api_base_url = os.getenv("API_BASE_URL", "http://localhost:3000")
user_token = os.getenv("USER_TOKEN")
provider = os.getenv("LLM_PROVIDER", "dashscope").lower()

print(f"[初始化] 提供商: {provider}")
print(f"[初始化] .env 文件: {env_path} (存在: {env_path.exists()})")

# 检查必需配置
if not user_token:
    print("错误：未找到 USER_TOKEN")
    exit(1)

# 初始化 LLM 客户端
def init_llm():
    if provider == "zhipu":
        api_key = os.getenv("ZHIPU_API_KEY")
        base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
        model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    elif provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    elif provider == "siliconflow":
        api_key = os.getenv("SILICON_API_KEY")          # ← 必须是 SILICON_API_KEY
        base_url = os.getenv("SILICON_BASE_URL", "https://api.siliconflow.cn/v1")
        model = os.getenv("SILICON_MODEL", "Qwen/Qwen3-8B")
    else:
        raise ValueError(f"不支持的提供商: {provider}")
    
    if not api_key:
        raise ValueError(f"缺少 API Key")
    
    print(f"[初始化] 模型: {model}")
    print(f"[初始化] Base URL: {base_url}")
    
    return OpenAI(api_key=api_key, base_url=base_url), model

try:
    llm_client, llm_model = init_llm()
except Exception as e:
    print(f"LLM 初始化失败: {e}")
    exit(1)

# 请求头
HEADERS = {
    "Authorization": f"Bearer {user_token}",
    "Content-Type": "application/json"
}

# -------------------- Tools 定义 --------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_all_items",
            "description": "获取当前用户的所有物品列表",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expiring_items",
            "description": "获取即将过期的物品（默认3天内）",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "天数阈值", "default": 3}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_items",
            "description": "按关键词搜索物品",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_item",
            "description": "添加新物品",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "expiry_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "category": {"type": "string"},
                    "purchase_date": {"type": "string"},
                    "shelf_life_days": {"type": "integer"}
                },
                "required": ["name", "expiry_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_item",
            "description": "删除物品",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"}
                },
                "required": ["item_id"]
            }
        }
    }
]

# -------------------- Function 实现（简化版） --------------------
def call_api(method, endpoint, **kwargs):
    """统一 API 调用"""
    try:
        resp = requests.request(
            method=method,
            url=f"{api_base_url}{endpoint}",
            headers=HEADERS,
            **kwargs
        )
        if resp.status_code == 401:
            return {"error": "Token 已过期"}
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def get_all_items():
    return call_api("GET", "/api/items")

def get_expiring_items(days=3):
    return call_api("GET", "/api/items", params={"expiring": "true", "days": days})

def search_items(keyword):
    items = get_all_items()
    if isinstance(items, dict) and "error" in items:
        return items
    return [i for i in items if keyword.lower() in i.get("name", "").lower()]

def add_item(name, expiry_date, **kwargs):
    payload = {"name": name, "expiry_date": expiry_date}
    for k in ["category", "purchase_date", "shelf_life_days"]:
        if k in kwargs and kwargs[k]:
            payload[k] = kwargs[k]
    
    # 如果提供了购买日期和保质期，计算过期日期
    if "purchase_date" in payload and "shelf_life_days" in payload:
        from datetime import datetime, timedelta
        try:
            purchase = datetime.strptime(payload["purchase_date"], "%Y-%m-%d")
            expiry = purchase + timedelta(days=payload["shelf_life_days"])
            payload["expiry_date"] = expiry.strftime("%Y-%m-%d")
            # 移除临时字段
            del payload["purchase_date"]
            del payload["shelf_life_days"]
        except:
            pass
    
    return call_api("POST", "/api/items", json=payload)
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv()

# 通用配置
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "dashscope").lower()

# 硅基流动（SiliconFlow）默认值
DEFAULT_SILICON_API_KEY = "sk-viconoqwarvbowmxwsmzrydgvritpwmwcdvuquiougsrtfzy"
DEFAULT_SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_SILICON_MODEL = "Qwen/Qwen3-8B"

# 根据 LLM_PROVIDER 选择配置
if LLM_PROVIDER == "zhipu":
    api_key = os.getenv("ZHIPU_API_KEY")
    base_url = os.getenv("ZHIPU_BASE_URL")
    model = os.getenv("ZHIPU_MODEL")
elif LLM_PROVIDER == "dashscope":
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")
    model = os.getenv("DASHSCOPE_MODEL")
elif LLM_PROVIDER == "siliconflow":
    api_key = os.getenv("SILICON_API_KEY", DEFAULT_SILICON_API_KEY)
    base_url = os.getenv("SILICON_BASE_URL", DEFAULT_SILICON_BASE_URL)
    model = os.getenv("SILICON_MODEL", DEFAULT_SILICON_MODEL)
else:
    raise ValueError(f"不支持的 LLM_PROVIDER: {LLM_PROVIDER}")

# 创建 OpenAI 客户端
client = OpenAI(api_key=api_key, base_url=base_url)
def delete_item(item_id):
    return call_api("DELETE", f"/api/items/{item_id}")

# -------------------- 工具调用处理 --------------------
def handle_tool_call(tool_call):
    """处理单个工具调用"""
    func_name = tool_call.function.name
    try:
        func_args = json.loads(tool_call.function.arguments)
    except:
        return {"error": "参数解析失败"}
    
    print(f"[工具调用] {func_name}")
    print(f"[参数] {func_args}")
    
    # 调用对应函数
    if func_name == "get_all_items":
        result = get_all_items()
    elif func_name == "get_expiring_items":
        result = get_expiring_items(func_args.get("days", 3))
    elif func_name == "search_items":
        result = search_items(func_args["keyword"])
    elif func_name == "add_item":
        result = add_item(
            name=func_args["name"],
            expiry_date=func_args["expiry_date"],
            category=func_args.get("category"),
            purchase_date=func_args.get("purchase_date"),
            shelf_life_days=func_args.get("shelf_life_days")
        )
    elif func_name == "delete_item":
        result = delete_item(func_args["item_id"])
    else:
        result = {"error": f"未知工具: {func_name}"}
    
    print(f"[结果] {json.dumps(result, ensure_ascii=False)[:200]}")
    return result

# -------------------- 主循环 --------------------
def main():
    print("=" * 50)
    print("   保质期管家 AI Agent")
    print(f"   提供商: {provider} | 模型: {llm_model}")
    print("   输入 'exit' 退出，输入 'debug' 切换调试模式")
    print("=" * 50)
    print()
    
    messages = [
        {"role": "system", "content": "你是保质期管家 AI，帮助用户管理物品。使用工具操作数据。"}
    ]
    debug_mode = True  # 默认开启调试
    
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("再见！")
            break
        if user_input.lower() == "debug":
            debug_mode = not debug_mode
            print(f"调试模式: {'开启' if debug_mode else '关闭'}")
            continue
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            if debug_mode:
                print(f"\n[调试] 发送请求...")
            
            # 第一次调用：获取工具调用
            response = llm_client.chat.completions.create(
                model=llm_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2
            )
            
            message = response.choices[0].message
            
            if debug_mode:
                print(f"[调试] 响应角色: {message.role}")
                if message.content:
                    print(f"[调试] 文本内容: {message.content[:100]}")
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"[调试] 工具调用数: {len(message.tool_calls)}")
            
            # 处理工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # 添加 assistant 消息
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # 执行所有工具调用
                for tool_call in message.tool_calls:
                    result = handle_tool_call(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                # 第二次调用：获取最终回复
                if debug_mode:
                    print(f"[调试] 发送工具结果，获取最终回复...")
                
                final_resp = llm_client.chat.completions.create(
                    model=llm_model,
                    messages=messages,
                    temperature=0.2
                )
                
                reply = final_resp.choices[0].message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})
            
            else:
                # 没有工具调用
                reply = message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})
            
            print()
        
        except Exception as e:
            print(f"错误: {e}")
            if debug_mode:
                import traceback
                traceback.print_exc()

def test_tool_calling():
    """测试工具调用是否工作"""
    print("=" * 50)
    print("   测试模式：验证工具调用")
    print("=" * 50)
    
    # 测试1：查看所有物品
    print("\n[测试1] 发送：查看我的所有物品")
    messages = [
        {"role": "system", "content": "你是保质期管家 AI，有工具可以调用。"},
        {"role": "user", "content": "查看我的所有物品"}
    ]
    
    try:
        response = llm_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )
        
        message = response.choices[0].message
        print(f"模型回复: {message.content[:200] if message.content else '(无文本内容)'}")
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"✓ 检测到 {len(message.tool_calls)} 个工具调用：")
            for tc in message.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"  - {tc.function.name}({args})")
            
            # 执行工具
            print("\n执行工具...")
            for tc in message.tool_calls:
                result = handle_tool_call(tc)
                print(f"工具结果: {json.dumps(result, ensure_ascii=False)[:200]}")
            
            print("\n✓ 工具调用测试通过！")
        else:
            print("✗ 没有检测到工具调用，模型可能不支持或prompt需要优化")
            print("建议：检查模型是否支持工具调用，或尝试其他模型")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_tool_calling()
    else:
        main()
