import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端（兼容 DeepSeek、Qwen 等）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")  # 如果为空则使用官方 OpenAI
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")
USER_TOKEN = os.getenv("USER_TOKEN")

if not USER_TOKEN:
    print("错误：未找到 USER_TOKEN。请先在 .env 中设置，或运行脚本获取 token。")
    exit(1)

# 请求头
HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "Content-Type": "application/json"
}

# -------------------- Function 工具定义 --------------------
functions = [
    {
        "name": "get_all_items",
        "description": "获取当前用户的所有物品列表（包含已共享的家庭物品）",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
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
    },
    {
        "name": "search_items",
        "description": "按关键词搜索物品名称（本地过滤）",
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
    },
    {
        "name": "add_item",
        "description": "添加新物品到保质期管家",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "物品名称"},
                "expire_date": {"type": "string", "description": "过期日期 YYYY-MM-DD"},
                "category": {"type": "string", "description": "分类（可选）"},
                "purchase_date": {"type": "string", "description": "购买日期 YYYY-MM-DD（可选）"},
                "shelf_life_days": {"type": "integer", "description": "保质期天数（可选）"}
            },
            "required": ["name", "expire_date"]
        }
    },
    {
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
]

# -------------------- Function 实现 --------------------
def get_all_items():
    try:
        resp = requests.get(f"{API_BASE_URL}/api/items", headers=HEADERS)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}"}

def get_expiring_items(days=3):
    try:
        # 后端已支持 expiring 参数，如不支持可在本地过滤
        resp = requests.get(
            f"{API_BASE_URL}/api/items",
            params={"expiring": "true", "days": days},
            headers=HEADERS
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        # 如果后端不支持 expiring 参数，则本地过滤
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                return local_filter_expiring(days)
        return {"error": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}"}

def local_filter_expiring(days=3):
    all_items = get_all_items()
    if isinstance(all_items, dict) and "error" in all_items:
        return all_items

    from datetime import datetime, timedelta
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    later = today + timedelta(days=days)

    result = []
    for item in all_items:
        if item.get("status") != "active":
            continue
        try:
            exp_date = datetime.strptime(item["expire_date"], "%Y-%m-%d")
            if today <= exp_date <= later:
                result.append(item)
        except:
            pass
    return result

def search_items(keyword):
    all_items = get_all_items()
    if isinstance(all_items, dict) and "error" in all_items:
        return all_items

    keyword_lower = keyword.lower()
    return [item for item in all_items if keyword_lower in item.get("name", "").lower()]

def add_item(name, expire_date, category=None, purchase_date=None, shelf_life_days=None):
    payload = {
        "name": name,
        "expire_date": expire_date
    }
    if category:
        payload["category"] = category
    if purchase_date:
        payload["purchase_date"] = purchase_date
    if shelf_life_days:
        payload["shelf_life_days"] = shelf_life_days

    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/items",
            headers=HEADERS,
            json=payload
        )
        if resp.status_code == 401:
            return {"error": "Token 已过期，请重新登录获取新的 USER_TOKEN"}
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"添加失败: {str(e)}"}

def delete_item(item_id):
    try:
        resp = requests.delete(
            f"{API_BASE_URL}/api/items/{item_id}",
            headers=HEADERS
        )
        if resp.status_code == 401:
            return {"error": "Token 已过期，请重新登录获取新的 USER_TOKEN"}
        if resp.status_code == 404:
            return {"error": f"未找到 ID 为 {item_id} 的物品"}
        resp.raise_for_status()
        return {"success": True, "message": "删除成功"}
    except requests.exceptions.RequestException as e:
        return {"error": f"删除失败: {str(e)}"}

# -------------------- Function 调用分发 --------------------
def handle_function_call(name, args):
    if name == "get_all_items":
        return get_all_items()
    elif name == "get_expiring_items":
        days = args.get("days", 3)
        return get_expiring_items(days)
    elif name == "search_items":
        return search_items(args["keyword"])
    elif name == "add_item":
        return add_item(
            name=args["name"],
            expire_date=args["expire_date"],
            category=args.get("category"),
            purchase_date=args.get("purchase_date"),
            shelf_life_days=args.get("shelf_life_days")
        )
    elif name == "delete_item":
        return delete_item(args["item_id"])
    else:
        return {"error": f"未知函数: {name}"}

# -------------------- 主对话循环 --------------------
def main():
    print("=" * 50)
    print("   保质期管家 AI Agent")
    print("   输入 'exit' 或 'quit' 退出")
    print("=" * 50)
    print()

    messages = [
        {
            "role": "system",
            "content": """你是保质期管家的 AI 助手，帮助用户管理他们的物品保质期。
你可以通过 function calling 来操作用户的物品数据。
当用户询问即将过期的物品时，使用 get_expiring_items。
当用户想添加物品时，确认所有必要信息后使用 add_item。
当用户想删除物品时，先搜索找到物品 ID，再使用 delete_item。
保持回复简洁友好，使用中文。"""
        }
    ]

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if user_input.lower() in ["exit", "quit", "退出", "bye"]:
            print("再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL", "gpt-3.5-turbo"),
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.2
            )

            message = response.choices[0].message

            # 如果有 function call
            if message.function_call:
                func_name = message.function_call.name
                func_args = json.loads(message.function_call.arguments)

                print(f"[调用工具: {func_name}]")
                result = handle_function_call(func_name, func_args)

                # 把 function 结果加回对话
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

                # 再次请求，让 AI 总结结果
                second_resp = client.chat.completions.create(
                    model=os.getenv("MODEL", "gpt-3.5-turbo"),
                    messages=messages,
                    temperature=0.2
                )
                reply = second_resp.choices[0].message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})

            else:
                reply = message.content
                print(f"AI: {reply}")
                messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"错误: {str(e)}")
            # 如果 token 过期，提示用户
            if "401" in str(e) or "unauthorized" in str(e).lower():
                print("提示：Token 可能已过期，请更新 .env 中的 USER_TOKEN")

if __name__ == "__main__":
    main()
