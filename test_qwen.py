# 这个文件是验证 API Key 连通性 
# 不会妨碍其他文件，是独立的
# test_qwen.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 中的变量

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),   # 从环境变量读取
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
completion = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "说一句简短的开场白"}],
)
print(completion.choices[0].message.content)