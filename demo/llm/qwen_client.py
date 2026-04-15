import dashscope
import os
import json

# =========================
# 🔐 API Key（兼容本地 + Cloud）
# =========================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# ⚠️ 如果你本地测试，也可以临时写死（取消注释）
# dashscope.api_key = "你的API_KEY"


# =========================
# 🧠 探索模式 Prompt（多轮对话）
# =========================
EXPLORATION_PROMPT = """
你是《饥荒》世界观设计AI助手。

当前处于【探索设计模式】：
目标是帮助用户逐步构建Boss设定，而不是直接给完整答案。

要求：
1. 引导用户补充设定
2. 提出问题
3. 给出概念雏形
4. 不要输出代码

必须输出JSON格式：

{
  "concept": "",
  "entity": "",
  "mechanics": [],
  "questions": []
}
"""


# =========================
# ⚙️ 快速生成模式 Prompt（直接成品）
# =========================
FAST_PROMPT = """
你是《饥荒》Mod开发AI。

当前处于【快速生成模式】：
用户已经有明确想法，请直接生成完整Boss设计。

要求：
1. 生成完整Boss设定
2. 包含机制/行为/触发
3. 可用于游戏开发
4. 输出JSON

格式：

{
  "concept": "",
  "entity": "",
  "mechanics": [],
  "triggers": [],
  "behavior": []
}
"""


# =========================
# 🧠 安全JSON解析（防崩）
# =========================
def safe_parse(text):

    try:
        return json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except:
                pass

    return {
        "concept": "解析失败",
        "entity": "unknown",
        "mechanics": [],
        "questions": ["JSON解析失败，请重新生成"]
    }


# =========================
# 🚀 核心调用函数
# =========================
def call_qwen(user_input="", mode="explore", messages=None):

    system_prompt = EXPLORATION_PROMPT if mode == "explore" else FAST_PROMPT

    if messages:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
    else:
        full_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

    try:
        response = dashscope.Generation.call(
            model="qwen-plus",
            messages=full_messages,
            result_format="message"
        )

        content = response.output.choices[0].message.content

        return safe_parse(content)

    except Exception as e:
        return {
            "concept": "API错误",
            "entity": "error",
            "mechanics": [],
            "questions": [str(e)]
        }


# =========================
# 🎯 给app.py用的封装函数
# =========================
def design_with_llm(user_input):
    return call_qwen(user_input, mode="fast")


def explore_with_llm(messages):
    return call_qwen("", mode="explore", messages=messages)