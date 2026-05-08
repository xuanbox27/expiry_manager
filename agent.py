import os
import sys
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# 修复 Windows 中文编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 读取配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")
USER_TOKEN = os.getenv("USER_TOKEN")

# 检查必需配置
if not USER_TOKEN:
    print("错误：未找到 USER_TOKEN，请在 .env 中设置")
    exit(1)

# 初始化 LLM 客户端 - 默认使用硅基流动
def init_llm():
    provider = os.getenv("LLM_PROVIDER", "siliconflow").lower()
    
    if provider == "siliconflow":
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen3-8B")
    elif provider == "zhipu":
        api_key = os.getenv("ZHIPU_API_KEY")
        base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
        model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    elif provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    else:
        raise ValueError(f"不支持的提供商: {provider}")
    
    if not api_key:
        raise ValueError(f"缺少 {provider.upper()}_API_KEY")
    
    print(f"[初始化] 提供商: {provider}")
    print(f"[初始化] 模型: {model}")
    print(f"[初始化] Base URL: {base_url}")
    
    return OpenAI(api_key=api_key, base_url=base_url), model, provider

try:
    llm_client, llm_model, current_provider = init_llm()
except Exception as e:
    print(f"LLM 初始化失败: {e}")
    exit(1)

# 请求头
HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "Content-Type": "application/json"
}

# -------------------- Tools 定义（OpenAI 新格式） --------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_all_items",
            "description": "获取当前用户的所有物品列表（包含已共享的家庭物品）",
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
                    "days": {
                        "type": "integer",
                        "description": "天数阈值，默认3天",
                        "default": 3
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_items",
            "description": "按关键词搜索物品名称",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，如'牛奶'、'面包'"
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_item",
            "description": "添加新物品到保质期管家",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "物品名称"},
                    "expiry_date": {"type": "string", "description": "过期日期 YYYY-MM-DD"},
                    "category": {"type": "string", "description": "分类（可选）"},
                    "purchase_date": {"type": "string", "description": "购买日期 YYYY-MM-DD（可选）"},
                    "shelf_life_days": {"type": "integer", "description": "保质期天数（可选）"}
                },
                "required": ["name", "expiry_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_item",
            "description": "删除指定物品（需要提供物品ID）",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "物品ID"}
                },
                "required": ["item_id"]
            }
        }
    }
]

# -------------------- Function 实现 --------------------
def api_request(method, endpoint, **kwargs):
    """统一 API 调用"""
    try:
        resp = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            headers=HEADERS,
            **kwargs
        )
        if resp.status_code == 401:
            return {"error": "Token 已过期，请重新登录获取新的 USER_TOKEN"}
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}"}

def get_all_items():
    return api_request("GET", "/api/items")

def get_expiring_items(days=3):
    return api_request("GET", "/api/items", params={"expiring": "true", "days": days})

def search_items(keyword):
    items = get_all_items()
    if isinstance(items, dict) and "error" in items:
        return items
    keyword_lower = keyword.lower()
    return [item for item in items if keyword_lower in item.get("name", "").lower()]

def add_item(name, expiry_date, category=None, purchase_date=None, shelf_life_days=None):
    # 如果提供了 purchase_date 和 shelf_life_days，则计算 expiry_date
    if purchase_date and shelf_life_days:
        try:
            purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
            expiry = purchase + timedelta(days=shelf_life_days)
            expiry_date = expiry.strftime("%Y-%m-%d")
        except Exception as e:
            return {"error": f"日期计算失败: {str(e)}"}
        # 清除临时字段
        purchase_date = None
        shelf_life_days = None

    payload = {"name": name, "expiry_date": expiry_date}
    if category:
        payload["category"] = category

    return api_request("POST", "/api/items", json=payload)

def delete_item(item_id):
    return api_request("DELETE", f"/api/items/{item_id}")

# -------------------- Function 调用分发 --------------------
def handle_tool_call(tool_call):
    """处理单个工具调用"""
    func_name = tool_call.function.name
    try:
        func_args = json.loads(tool_call.function.arguments)
    except:
        return {"error": "参数解析失败"}
    
    print(f"\n[工具调用] {func_name}")
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

# -------------------- 主对话循环 --------------------
def main():
    print("=" * 50)
    print("   保质期管家 AI Agent")
    print(f"   提供商: {current_provider}")
    print(f"   模型: {llm_model}")
    print("   输入 'exit' 或 'quit' 退出")
    print("   输入 'debug' 切换调试模式")
    print("=" * 50)
    print()
    
    messages = [
        {
            "role": "system",
            "content": """你是保质期管家的 AI 助手，帮助用户管理他们的物品保质期。
你可以通过工具调用来操作用户的物品数据。
当用户询问即将过期的物品时，使用 get_expiring_items 工具。
当用户想添加物品时，确认所有必要信息后使用 add_item 工具。
当用户想删除物品时，先搜索找到物品 ID，再使用 delete_item 工具。
保持回复简洁友好，使用中文。"""
        }
    ]
    
    debug_mode = True
    
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if user_input.lower() in ["exit", "quit", "退出", "bye"]:
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
                print(f"\n[调试] 发送请求到模型...")
            
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
                    print(f"[调试] 检测到 {len(message.tool_calls)} 个工具调用")
            
            # 处理工具调用（新格式 tool_calls）
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # 添加 assistant 消息（包含 tool_calls）
                assistant_msg = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                }
                messages.append(assistant_msg)
                
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
            
            # 兼容旧格式（function_call）
            elif hasattr(message, 'function_call') and message.function_call:
                func_name = message.function_call.name
                func_args = json.loads(message.function_call.arguments)
                
                print(f"[工具调用] {func_name}")
                result = handle_tool_call(type('ToolCall', (), {
                    'function': type('Function', (), {
                        'name': func_name,
                        'arguments': json.dumps(func_args, ensure_ascii=False)
                    })()
                })())
                
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": func_name,
                        "arguments": json.dumps(func_args, ensure_ascii=False)
                    }
                })
                messages.append({
                    "role": "function",
                    "name": func_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
                second_resp = llm_client.chat.completions.create(
                    model=llm_model,
                    messages=messages,
                    temperature=0.2
                )
                reply = second_resp.choices[0].message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})
            
            else:
                # 没有工具调用
                reply = message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})
            
            print()
        
        except Exception as e:
            error_msg = str(e)
            print(f"错误: {error_msg}")
            
            if debug_mode:
                import traceback
                traceback.print_exc()
            
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                print("提示：API Key 可能无效或已过期")
            elif "quota" in error_msg.lower():
                print("提示：API 额度已用完")
            elif "tool" in error_msg.lower():
                print("提示：工具调用可能不被该模型支持")

if __name__ == "__main__":
    main()
