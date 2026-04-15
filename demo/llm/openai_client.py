from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def design_with_llm(user_input):
    prompt = f"""
你是一个游戏设计助手，帮助用户把模糊想法变成清晰的游戏机制。

用户输入：
{user_input}

请你输出 JSON，格式如下：

{{
  "concept": "总结用户想法",
  "entity": "",
  "mechanics": [],
  "design": {{
    "combat_style": "",
    "faction": "",
    "difficulty": ""
  }},
  "questions": [
    "用于进一步 уточ设计的问题"
  ]
}}

要求：
1. 不要输出解释，只输出JSON
2. 用游戏设计语言
3. questions必须是引导用户完善设计的问题
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你是一个游戏设计专家"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content