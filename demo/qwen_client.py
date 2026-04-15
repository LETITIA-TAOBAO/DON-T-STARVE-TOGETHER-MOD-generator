import dashscope
import os
import json
import re

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


# =========================
# 🧠 Prompt（完全不动）
# =========================
EXPLORATION_PROMPT = r'''
ＯＫ
'''


FAST_PROMPT = r'''
# 角色
你是一个专业的《Don't Starve Together》Mod设计与实现专家，精通Klei的设计风格、游戏机制以及Lua Mod开发。

你不仅能进行创意设计，还能直接将设计转化为可实现的Mod方案与代码结构。

⚠️ 禁止输出JSON或键值对格式
'''


STRUCTURE_HINT = r'''
\n\n【系统补充（忽略展示给用户）】
在回答的最后，请额外附上一段JSON，用于系统解析：

{
  "concept": "一句话概括设计",
  "entity": "核心实体名称",
  "mechanics": ["机制1", "机制2"]
}
'''


# =========================
# 🧠 JSON 提取
# =========================
def extract_json(text):
    try:
        matches = re.findall(r"\{[\s\S]*?\}", text)
        for m in reversed(matches):
            try:
                return json.loads(m)
            except:
                continue
    except:
        pass
    return None


# =========================
# 🧹 清洗文本
# =========================
def clean_text(text):
    if not text:
        return "（AI没有返回内容）"

    text = re.sub(r"\n*\{[\s\S]*?\}\s*$", "", text).strip()

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if len(line) > 2 and line[0].isdigit() and ":" in line[:4]:
            line = line.split(":", 1)[-1].strip()

        cleaned.append(line)

    return "\n".join(cleaned).strip()


# =========================
# 🚀 核心调用
# =========================
def call_qwen(user_input="", mode="explore", messages=None):

    base_prompt = EXPLORATION_PROMPT if mode == "explore" else FAST_PROMPT
    system_prompt = base_prompt + STRUCTURE_HINT

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
            "text": f"连接失败：{str(e)}",
            "data": None
        }


# =========================
# 🎯 API
# =========================
def design_with_llm(user_input):
    return call_qwen(user_input, mode="fast")


def explore_with_llm(messages):
    return call_qwen("", mode="explore", messages=messages)
