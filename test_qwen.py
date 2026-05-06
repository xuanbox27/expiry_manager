# 这个文件是验证 API Key 连通性 
# 不会妨碍其他文件，是独立的
from openai import OpenAI

client = OpenAI(
    api_key="sk-0c2ecd839a7b4b08bfa4cdaa9a27b017",   # 你的 API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "说一句简短的开场白"}],
)
print(completion.choices[0].message.content)