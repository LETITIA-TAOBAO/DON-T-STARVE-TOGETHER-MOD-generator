import dashscope
import os
import json
import re

# =========================
# 🔐 API Key（兼容本地 + Cloud）
# =========================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# =========================
# 🧠 探索模式 Prompt（完全保留你的）
# =========================
EXPLORATION_PROMPT = """
# 角色
你是一个专业的《Don't Starve Together》Mod设计引导专家，熟悉Klei的设计风格与游戏机制。你擅长通过多轮对话，引导用户逐步明确他们想要制作的Mod内容，并将模糊的想法转化为清晰、可实现的设计方案。

你的风格像一位游戏设计师，而不是程序或工具。你会用自然语言与用户交流，避免使用JSON或结构化数据输出。

# 输入
以下是输入内容：
- user_idea：用户输入的初始想法，可能是模糊的（例如“我想做一个夜晚变强的boss”）
- history：历史对话记录（用于多轮上下文理解）

# 任务
你需要通过逐步引导对话，帮助用户明确他们想要制作的Mod类型、核心玩法、风格方向与实现范围。

你的目标不是一次性给出答案，而是“引导用户思考 + 逐步收敛设计”。

## 步骤一：识别想法类型
判断user_idea属于哪种Mod方向：
- 角色类（Character）
- Boss/生物类（Creature/Boss）
- 物品/装备类（Item）
- 机制类（Mechanic）
- UI/体验类（UI/UX）
- 综合玩法（Mixed）

并用一句话“复述 + 轻微扩展”用户的想法（不要改写太多）。

## 步骤二：补全核心设计维度（选择2-3个关键点追问）
根据Mod类型，从以下维度中选择最关键的2-3个进行提问（不要一次问太多）：

通用维度：
- 核心玩法（这个Mod最有趣的点是什么？）
- 风格氛围（偏恐怖 / 搞笑 / 克苏鲁 / 科雷原版风格？）
- 复杂度（轻量增强 / 中型内容 / 大型系统）

Boss/生物类优先问：
- 行为机制（怎么攻击？有什么特殊机制？）
- 刷新/触发方式（自然出现 or 召唤）
- 是否有阶段变化（类似季节/血量/时间）

角色类优先问：
- 核心能力（技能/特性）
- 优势与代价（平衡性）
- 生存风格（战斗/探索/辅助）

物品类优先问：
- 使用场景（战斗/生存/建造）
- 是否有副作用
- 获取方式

## 步骤三：构建“半成型设计”
当信息足够时，用自然语言整理出一个“初步设计方案”，包括：
- 核心概念（像官方描述）
- 玩法亮点（2-3条）
- 一点点世界观/设定味道

⚠️ 不要使用JSON格式  
⚠️ 要像游戏设计师在讲创意  

## 步骤四：继续引导（关键）
在结尾必须提出2-3个“有方向的选择题式问题”

## 步骤五：对话风格要求
- 使用自然语言
- 分段清晰
- 不要输出代码
- 不要输出JSON
"""

# =========================
# ⚡ 快速生成模式 Prompt（仅做最小修复）
# =========================
FAST_PROMPT = """
# 角色
你是一个专业的《Don't Starve Together》Mod设计与实现专家。

你需要：
1. 用自然语言输出完整设计
2. 最后附带一个JSON结构（用于程序解析）

⚠️ 不要在正文中使用JSON，只允许在最后输出JSON

JSON格式如下：
{
  "concept": "...",
  "mechanics": ["...", "..."],
  "code_hint": "..."
}
"""

# =========================
# 🧠 提取JSON（稳定版）
# =========================
def extract_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            return json.loads(text[start:end])
    except:
        pass

    return None


# =========================
# 🧠 清理文本（去掉JSON）
# =========================
def clean_text(text):
    return re.sub(r"\{.*\}", "", text, flags=re.DOTALL).strip()


# =========================
# 🚀 核心调用函数（关键修复点）
# =========================
def call_qwen(user_input="", mode="explore", messages=None):

    system_prompt = EXPLORATION_PROMPT if mode == "explore" else FAST_PROMPT

    # 构建 messages
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

        # ⚠️ 防御
        if response is None:
            return {"text": "❌ 模型无返回", "json": None, "raw": None}

        content = response.output.choices[0].message.content

        # 👉 分离
        parsed_json = extract_json(content)
        display_text = clean_text(content)

        return {
            "text": display_text,   # 给用户
            "json": parsed_json,    # 给系统
            "raw": content          # 调试用
        }

    except Exception as e:
        return {
            "text": f"❌ API错误: {str(e)}",
            "json": None,
            "raw": None
        }


# =========================
# 🎯 对外封装
# =========================
def design_with_llm(user_input):
    return call_qwen(user_input, mode="fast")


def explore_with_llm(messages):
    return call_qwen("", mode="explore", messages=messages)
