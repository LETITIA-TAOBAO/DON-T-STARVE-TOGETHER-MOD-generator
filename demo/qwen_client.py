import dashscope
import os
import json
import re

# 配置API密钥
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 定义提示词 - 使用最安全的单行字符串方式
EXPLORATION_PROMPT = (
    "# 角色\n"
    "你是专业的《Don't Starve Together》Mod设计专家，"
    "熟悉Klei设计风格与游戏机制。通过多轮对话引导用户明确Mod设计方向。"
    "风格自然，避免使用JSON或结构化数据输出。\n"
    "# 输入\n"
    "- user_idea\n"
    "- history\n"
    "# 任务\n"
    "引导用户逐步明确Mod设计方向。"
)

FAST_PROMPT = (
    "# 角色\n"
    "你是《Don't Starve Together》Mod设计与实现专家。"
    "能进行创意设计并转化为Lua Mod实现结构。"
    "⚠️ 禁止输出JSON或键值对格式"
)

STRUCTURE_HINT = (
    "在回答最后附加JSON（仅用于系统解析）：\n"
    "{\n"
    '  "concept": "设计概括",\n'
    '  "entity": "核心实体",\n'
    '  "mechanics": ["机制1", "机制2"]\n'
    "}"
)

def extract_json(text: str):
    if not text:
        return None
    matches = re.findall(r"\{[\s\S]*?\}", text)
    for m in reversed(matches):
        try:
            return json.loads(m)
        except:
            continue
    return None

def clean_text(text: str):
    if not text:
        return "（AI没有返回内容）"
    text = re.sub(r"\{[\s\S]*?\}\s*$", "", text).strip()
    lines = [line.split(":", 1)[-1].strip() if (len(line) > 2 and line[0].isdigit() and ":" in line[:4]) else line.strip()
             for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def call_qwen(user_input="", mode="explore", messages=None):
    base_prompt = EXPLORATION_PROMPT if mode == "explore" else FAST_PROMPT
    system_prompt = f"{base_prompt}\n\n{STRUCTURE_HINT}"

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
        return {"text": f"LLM调用失败：{str(e)}", "data": None}

def design_with_llm(user_input: str):
    return call_qwen(user_input, mode="fast")

def explore_with_llm(messages):
    return call_qwen(messages=messages, mode="explore")
