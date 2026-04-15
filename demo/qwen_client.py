import dashscope
import os
import json
import re

# =========================
# 🔐 API Key
# =========================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# =========================
# 🧠 Prompt（保持你原设计）
# =========================
EXPLORATION_PROMPT = """
# 角色
你是一个专业的《Don't Starve Together》Mod设计引导专家，熟悉Klei的设计风格与游戏机制。你擅长通过多轮对话，引导用户逐步明确他们想要制作的Mod内容，并将模糊的想法转化为清晰、可实现的设计方案。

你的风格像一位游戏设计师，而不是程序或工具。你会用自然语言与用户交流，避免使用JSON或结构化数据输出。

# 输入
- user_idea
- history

# 任务
引导用户逐步明确Mod设计方向。

（以下内容保持你原来的prompt，可继续粘贴扩展）
"""

FAST_PROMPT = """
# 角色
你是一个专业的《Don't Starve Together》Mod设计与实现专家。

你不仅能进行创意设计，还能转化为Lua Mod实现结构。

⚠️ 禁止输出JSON或键值对格式
"""

STRUCTURE_HINT = """
在回答最后附加JSON（仅用于系统解析）：

{
  "concept": "一句话概括设计",
  "entity": "核心实体名称",
  "mechanics": ["机制1", "机制2"]
}
"""

# =========================
# 🧠 JSON 提取（安全版）
# =========================
def extract_json(text: str):
    if not text:
        return None

    # 找所有可能 JSON
    matches = re.findall(r"\{[\s\S]*?\}", text)

    for m in reversed(matches):
        try:
            return json.loads(m)
        except:
            continue

    return None

# =========================
# 🧹 文本清理（安全版）
# =========================
def clean_text(text: str):
    if not text:
        return "（AI没有返回内容）"

    # 去掉末尾 JSON
    text = re.sub(r"\{[\s\S]*?\}\s*$", "", text).strip()

    # 去掉编号
    lines = text.split("\n")
    result = []

    for line in lines:
        line = line.strip()

        if len(line) > 2 and line[0].isdigit() and ":" in line[:4]:
            line = line.split(":", 1)[-1].strip()

        if line:
            result.append(line)

    return "\n".join(result).strip()

# =========================
# 🚀 LLM 调用核心
# =========================
def call_qwen(user_input="", mode="explore", messages=None):

    base_prompt = EXPLORATION_PROMPT if mode == "explore" else FAST_PROMPT
    system_prompt = base_prompt + "\n\n" + STRUCTURE_HINT

    # 构造 messages
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

        raw_text = response.output.choices[0].message.content

        return {
            "text": clean_text(raw_text),
            "data": extract_json(raw_text)
        }

    except Exception as e:
        return {
            "text": f"LLM调用失败：{str(e)}",
            "data": None
        }

# =========================
# 🎯 对外接口
# =========================
def design_with_llm(user_input: str):
    return call_qwen(user_input, mode="fast")

def explore_with_llm(messages):
    return call_qwen(messages=messages, mode="explore")
