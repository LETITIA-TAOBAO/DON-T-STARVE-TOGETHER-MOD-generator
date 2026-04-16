# qwen_client.py
import os
import re
import json
import requests
from datetime import datetime

try:
    import dashscope
    from dashscope import Generation
except ImportError:
    print("[ERROR] 请先安装: pip install dashscope")
    raise

# ── 读取 API Key ──────────────────────────────────────────
try:
    import streamlit as st
    DASHSCOPE_API_KEY = st.secrets.get("DASHSCOPE_API_KEY",
                        os.getenv("DASHSCOPE_API_KEY", ""))
except Exception:
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY
else:
    print("[WARN] 请设置 DASHSCOPE_API_KEY")

# ══════════════════════════════════════════════════════════════
# 📚 DST 世界知识库
# ══════════════════════════════════════════════════════════════

DST_KNOWLEDGE_BASE = """
【DST核心生存机制】
- 三维生存：生命值(HP)、饥饿值(Hunger)、理智值(Sanity)
- 理智过低(<15%)会生成影怪（Shadow Creature），持续攻击玩家
- 理智归零后影怪伤害大幅提升，难以独自应对
- 夜晚没有光源时，查理（黑暗）每2秒造成100伤害，瞬间致命
- 季节系统（秋/冬/春/夏）影响生物行为、食物腐烂速度、温度

【阵营与生态体系】
- 猪人（Pigman）：中立，可用肉类交易换金子；满月时变疯猪，会攻击玩家
- 鱼人（Merm）：对玩家默认敌对（除Wurt），与猪人天然仇恨，见面互打
- 兔人（Bunnyman）：讨厌肉类持有者，看到玩家拿肉/怪物肉就会群体攻击
- 影怪（Shadow Creature）：理智低于15%时出现，虚幻攻击形态；理智满时消失
- 月亮阵营（Lunar）：克制影怪，带有净化/异化属性；月亮石、开眼属于此阵营

【关键数值参考区间】
- 生命：150（威尔逊），范围50-400
- 饥饿：150，每分钟消耗约6.25 / 理智：200，范围100-300
- 暗影剑：68伤害，每秒-1.33 San / 火焰剑：42伤害
- 怪物肉：-20 San，-10 HP / 太妃糖：+15 San，+3 HP

【设计潜规则】
1. 强力必有代价：高伤害=掉San/降饥饿/吸引仇恨/限时/高材料
2. 食物必须明确可食性及HP/Hunger/San变化
3. 装备必须有耐久（除非永久性且代价极高）
4. 暗影/月亮属性物品必须影响San

【Few-Shot示例】
暗影之刃：伤害68，耐久100次，每次攻击-5San，猪人敌对，影怪友好
月光蘑菇：HP+10，Hunger+25，San+30，夜晚额外+20San，影怪回避持有者
"""

# ══════════════════════════════════════════════════════════════
# 🎨 饥荒风格图片 Prompt 常量
# ══════════════════════════════════════════════════════════════

# 风格锚定词（固定，始终注入，PRD 3.6要求）
DST_STYLE_ANCHOR = (
    "Don't Starve Together game art style, Tim Burton inspired gothic cartoon, "
    "thick black ink outlines, hand-drawn sketch texture, "
    "muted earth tones, parchment paper background, "
    "dark whimsical, 2D game asset sprite"
)

# 固定负面提示词（短而精）
DST_NEGATIVE = (
    "realistic photo, 3d render, anime, bright colors, "
    "text, watermark, blurry, modern, gradient"
)

# ══════════════════════════════════════════════════════════════
# 📋 SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════

EXPLORE_SYSTEM_PROMPT = f"""你是一位《Don't Starve Together》资深老玩家（游戏时长1000小时+），同时也是MOD设计师。
你对饥荒世界的每一个机制了如指掌，说话风格像老玩家，不是客服，也不是问卷调查员。

{DST_KNOWLEDGE_BASE}

【你的两种工作模式——必须根据对话判断当前应该用哪种】

━━ 模式A：追问引导（用户想法模糊时）━━
当用户只给了一个方向但细节不清晰时，用这个模式。
- 以朋友聊天的方式，每次只追问1个最关键的点
- 带点黑色幽默和生存吐槽感
- 回复控制在100字以内
- 末尾附上【设计进度】

━━ 模式B：自主创作（用户授权你设计时）━━
当用户说出以下任何意思时，立刻切换到这个模式，不要再追问：
"你来设计" / "帮我补全" / "你决定" / "随便" / "你帮我做" / "你来" / "帮我设计"
在这个模式下，你必须：
1. 立刻基于已知信息，自主创作完整设计
2. 发挥创意，给出每种对象的不同功能、外观、代价
3. 设计必须符合DST平衡规则（强力必有代价）
4. 用生动的饥荒风格语言描述设计
5. 回复可以长一点（400字以内），因为你在展示完整设计
6. 末尾附上【设计进度】并标注[DESIGN_COMPLETE]

【自主创作示例——当用户说"给我一个全是花的MOD，你帮我设计"时】
"行，既然你把设计权交给我，那我就不客气了。四种花，各有各的命运：

暗影玫瑰（Shadow Rose）：深紫色，边缘黑色脉络，夜晚微微发光。
持有时每分钟-2San，影怪对持有者仇恨降低50%，猪人看到会敌对。
食用：HP-5，San-20，但解除所有减益效果。

月光百合（Lunar Lily）：银白色，月圆夜发出蓝光。
食用：HP+15，San+25，只在夜晚食用才有效，白天吃了没用。
属月亮阵营，影怪看到持有者会主动回避。

血色罂粟（Blood Poppy）：深红色，枯萎状，带腐败气息。
加入任何食谱额外+30Hunger，但同时-10San。
兔人闻到这花会莫名敌对——它们就是不喜欢这个味道。

毒雾兰（Poison Mist Orchid）：灰绿色，表面覆着细小孢子。
食用：中毒3秒，HP-5/秒，但毒素消退后回复HP+30。
蜘蛛对持有者友好，猪人和鱼人都会逃跑。

四种花，共同点：只在春秋生长，冬天消失，夏天变种（效果减半）。

【设计进度】✓ 已确认：花×4、外观、功能、代价、阵营、季节 ？ 待明确：无 [DESIGN_COMPLETE]"

【格式规范】
- 正文紧凑，禁止在列表项之间插入空行
- 禁止重复列出"生存代价/阵营关系/风险机制/外观"当问卷
- 【设计进度】格式：【设计进度】✓ 已确认：[...] ？ 待明确：[...]
- 当类型/功能/外观/数值/代价全部明确后，输出[DESIGN_COMPLETE]"""


RAPID_SYSTEM_PROMPT = f"""你是Klei Entertainment的DST数值设计师，负责把玩家创意转化为官方级MOD规格。

{DST_KNOWLEDGE_BASE}

【你的核心任务】
把用户的MOD想法转化为精确、平衡、符合DST世界观的设计规格。
如果用户的想法不完整，你有权力自主补全——这是你的专业判断。

【自主补全原则】
- 不要反复追问同样的问题
- 基于DST世界观和平衡规则，自主做出设计决策
- 最多追问1个最关键的未知点，其他全部自主填充

【强制设计约束】
□ 强力效果必须有代价
□ 食物必须明确HP/Hunger/San变化
□ 数值必须在合理区间内
□ 装备必须有耐久

【设计规格卡格式（信息充足时输出）】
═══ MOD设计规格卡 ═══
名称：[英文名] / [中文名]
类型：[物品/角色/生物/机制]
核心功能：[精确描述]
【各对象详情】（每种花/物品分别列出）
对象1：[名称] - [外观] - [功能] - [代价]
对象2：[名称] - [外观] - [功能] - [代价]
【生态关系】
【风险提示】⚠️
════════════════════
[DESIGN_COMPLETE]"""


# ══════════════════════════════════════════════════════════════
# 🖼️ 图片 Prompt 提取 System Prompt（新增独立模块）
# ══════════════════════════════════════════════════════════════

IMAGE_EXTRACTION_SYSTEM = """你是专门为《饥荒》(Don't Starve Together)风格AI绘图提取视觉描述的专家。

你的任务：从MOD设计规格中，为每个对象提取一段简洁、精准的英文外观描述。

【严格规则】
1. 只输出该对象本身的外观特征，不要输出风格词（风格词会自动添加）
2. 必须是纯英文，绝对不能含有中文字符
3. 每条描述控制在 8-15 个英文单词以内
4. 聚焦：颜色 + 花型 + 最显著特征（如发光/枯萎/孢子）
5. 使用具体形容词，避免抽象词（不要用"mysterious"，要用"glowing edges"）

【好的示例】
- 暗影玫瑰 → "dark purple rose black veins softly glowing edges wilted"
- 月光百合 → "silver white lily blue luminous petals moon glow"
- 血色罂粟 → "deep crimson poppy withered drooping petals dark spots"
- 毒雾兰 → "grey green orchid pale spores mist foggy petals"

【坏的示例（禁止）】
- "mysterious dark flower" （太抽象）
- "暗影玫瑰 dark rose" （含中文）
- "Don't Starve Together style dark purple rose" （含风格词）

只输出JSON数组，不要其他内容：
[
  {"label": "对象中文名", "visual_en": "8-15词的纯英文外观描述"},
  {"label": "对象中文名", "visual_en": "8-15词的纯英文外观描述"}
]"""


DESIGN_SUMMARY_PROMPT = f"""你是DST MOD设计总结师，负责从对话中提取结构化设计规格。

{DST_KNOWLEDGE_BASE}

【重要规则】
- 如果对话中AI已经给出了完整的自主设计（如四种花的详细设计），必须忠实提取
- sub_objects 必须包含所有变体（最多不限于3个，有几个提取几个）
- appearance 字段必须用中文详细描述该对象的外观（颜色、形态、特殊视觉效果）
- 不要在 image_prompts 里生成英文描述，那个由后续专门步骤处理

根据完整对话，只输出JSON，不要其他内容：
{{
  "mod_name_en": "英文名（字母数字下划线，无空格）",
  "mod_name_cn": "中文名",
  "mod_type": "item或character或creature或mechanic",
  "description": "MOD简介（80字以内）",
  "core_function": "核心功能的精确描述",
  "main_object": {{
    "name_en": "第一个对象英文名（小写下划线）",
    "name_cn": "第一个对象中文名",
    "appearance": "详细中文外观描述，包含颜色、形态、特殊效果",
    "size": "small"
  }},
  "sub_objects": [
    {{
      "name_en": "第二个对象英文名",
      "name_cn": "第二个对象中文名",
      "appearance": "详细中文外观描述，与主对象明显不同",
      "role": "该对象功能",
      "size": "small"
    }}
  ],
  "stats": {{
    "health": null, "damage": null, "durability": null,
    "hunger": null, "sanity": null,
    "sanity_drain": null, "sanity_drain_rate": null
  }},
  "recipe": ["petals x3", "nightmare_fuel x1"],
  "special_effects": ["效果1（含代价）", "效果2"],
  "ecology": {{
    "pigman": "hostile或neutral或friendly",
    "merm": "hostile或neutral或friendly",
    "shadow": "hostile或neutral或friendly",
    "lunar": "hostile或neutral或friendly",
    "faction_notes": "阵营归属说明"
  }},
  "survival_impact": {{
    "sanity_effect": "理智影响描述",
    "hunger_effect": "饥饿影响描述",
    "is_edible": true,
    "eat_effect": "食用效果"
  }},
  "risk_notes": "主要风险与代价说明",
  "sound_triggers": [
    {{
      "trigger_cn": "拾取花朵",
      "trigger_type": "pickup",
      "object_cn": "花朵",
      "description_cn": "拾取时的自然清脆声响",
      "faction": "neutral"
    }}
  ],
  "sound_description": "音效需求中文描述",
  "sound_prompt_en": "flower pickup natural rustle short"
}}

注意：
- appearance 字段用中文描述，要具体（如"深紫色玫瑰，边缘有黑色脉络，夜晚微微发光"）
- sound_triggers 列出所有需要音效的场景（拾取/使用/特殊效果触发等）"""


MOD_CODE_PROMPT = """你是DST（饥荒联机版）MOD的Lua代码生成专家。
根据提供的MOD设计规格，生成完整可运行的MOD代码。

【必须包含的文件】
- modinfo.lua
- modmain.lua：为每个对象注册prefab
- prefabs/{name}.lua：每个对象各一个prefab文件

【代码规范】
- api_version = 10
- 必须实现理智影响、阵营仇恨逻辑、食物edible组件、耐久finiteuses
- 如有多个对象变体，为每个生成独立prefab
- 所有字符串用双引号

只输出JSON（不要```标记）：
{
  "text": "铸造说明（中文，100字以内）",
  "data": {
    "name": "mod英文名",
    "desc": "mod描述",
    "files": {
      "modinfo.lua": "完整lua代码",
      "modmain.lua": "完整lua代码",
      "prefabs/object1.lua": "完整lua代码"
    }
  }
}"""


SOUND_DESIGN_SYSTEM = """你是游戏音效设计师，专门为《饥荒联机版》风格MOD设计音效方案。

《饥荒》音效特征：
- 自然材质感（木头、叶片、花瓣碰撞）
- 略显怪异神秘，简短有力（0.3-1.5秒）
- 影系：低频共鸣+噪声 / 月亮系：高频空灵+正弦波 / 自然系：中频三角波

你会收到一个MOD的完整设计信息，包含多个触发场景。
请为每个触发场景设计音效，输出合成参数。

音效合成参数说明：
- oscillator: "sine"（纯净）/ "triangle"（温暖）/ "sawtooth"（粗糙）/ "square"（方硬）
- frequency_start/end: 频率范围Hz（自然声20-800，魔法800-2000，影系40-200）
- gain_start/end: 音量0-1
- noise_mix: 噪声混合比例0-1（叶片声0.6，魔法0.1，金属0.3）
- duration: 时长秒
- vibrato: 是否颤音（月亮系/魔法系true）
- lfo: 是否低频调制（环境音true）

只输出JSON：
{
  "sound_effects": [
    {
      "trigger": "触发条件中文",
      "trigger_type": "pickup/use/equip/eat/special/ambient",
      "description_cn": "音效中文描述",
      "faction": "neutral/shadow/lunar/nature",
      "synth_params": {
        "type": "描述性名称",
        "oscillator": "triangle",
        "frequency_start": 400,
        "frequency_end": 200,
        "gain_start": 0.5,
        "gain_end": 0.0,
        "noise_mix": 0.4,
        "duration": 0.5,
        "vibrato": false,
        "lfo": false
      }
    }
  ],
  "ambient_sound": {
    "needed": false,
    "description_cn": "",
    "synth_params": null
  }
}"""

# ══════════════════════════════════════════════════════════════
# 🔧 底层工具
# ══════════════════════════════════════════════════════════════

def _call_llm(system_prompt: str, user_content: str,
              temperature: float = 0.7, max_tokens: int = 2000) -> str:
    """调用通义千问"""
    response = Generation.call(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        result_format='message'
    )
    return response.output.choices[0].message.content.strip()


def _safe_parse_json(text: str):
    """安全解析JSON"""
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```\s*$', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    # 尝试解析数组
    try:
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None


def _format_conversation(messages: list) -> str:
    """格式化对话记录"""
    lines = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role    = "用户" if m.get("role") == "user" else "助手"
        content = m.get("content", "").strip()
        content = re.sub(r'\n{2,}', '\n', content)
        if content:
            lines.append(f"【{role}】{content}")
    return "\n".join(lines)


def _detect_user_authorization(messages: list) -> bool:
    """检测用户是否已授权AI自主创作"""
    auth_patterns = [
        r"你(来|帮我|给我)(设计|做|补|填|决定|创作|搞)",
        r"帮(我|忙)(设计|做|补充|填充|决定|创作)",
        r"(你|AI)(决定|来|搞定|随便|定)",
        r"(随便|都行|无所谓|随你|你看着办)",
        r"(全部|都)帮我(补|填|做|完成|搞)",
        r"你(自己|自主)(设计|决定|来)",
        r"(补充|补全|填充)(完整|好|一下)",
    ]
    user_msgs = [
        m.get("content", "")
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user"
    ][-3:]
    for msg in user_msgs:
        for pattern in auth_patterns:
            if re.search(pattern, msg):
                return True
    return False


def _sanitize_english_only(text: str) -> str:
    """
    移除所有非ASCII字符（中文、日文等），只保留纯英文。
    用于图片 prompt 的最终清理。
    """
    # 移除所有非ASCII字符
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # 只保留字母、数字、空格、常用标点
    text = re.sub(r'[^a-zA-Z0-9\s,\-\.]', ' ', text)
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _truncate_to_words(text: str, max_words: int) -> str:
    """按单词数截断文本"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words])

# ══════════════════════════════════════════════════════════════
# 🗣️ 对话引导
# ══════════════════════════════════════════════════════════════

def explore_with_llm(messages: list) -> dict:
    """探索模式多轮对话"""
    conversation  = _format_conversation(messages)
    is_authorized = _detect_user_authorization(messages)

    if is_authorized:
        mode_instruction = (
            "【重要】用户已经授权你自主设计，不要再追问了。"
            "请立刻切换到【模式B：自主创作】，基于已知信息发挥创意，"
            "给出完整、有灵魂的设计方案，包含具体数值、外观、代价、阵营关系。"
            "如果MOD含多种对象（如多种花），每种都要详细设计。"
            "回复400字以内，末尾附【设计进度】并加[DESIGN_COMPLETE]。"
        )
        temp = 0.85
    else:
        mode_instruction = (
            "请以DST资深老玩家的语气继续引导设计。"
            "每次只追问1个最关键的点，不要列出所有待明确维度当问卷。"
            "回复控制在100字以内，末尾附【设计进度】。"
            "全部明确后加[DESIGN_COMPLETE]。"
        )
        temp = 0.75

    user_content = f"当前对话记录：\n{conversation}\n\n{mode_instruction}"

    try:
        raw         = _call_llm(EXPLORE_SYSTEM_PROMPT, user_content,
                                temperature=temp)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean       = raw.replace("[DESIGN_COMPLETE]", "").strip()
        clean       = re.sub(r'\n{3,}', '\n\n', clean)
        return {"text": clean, "data": None, "is_complete": is_complete}
    except Exception as e:
        return {"text": f"暗影失语了……（{e}）",
                "data": None, "is_complete": False}


def rapid_with_llm(messages: list) -> dict:
    """快速模式设计细化"""
    conversation  = _format_conversation(messages)
    is_authorized = _detect_user_authorization(messages)

    if is_authorized:
        mode_instruction = (
            "用户已授权你自主补全设计。不要追问，"
            "直接输出完整规格卡并加[DESIGN_COMPLETE]。"
        )
        temp = 0.75
    else:
        mode_instruction = (
            "信息不足时最多追问1个关键问题，其他自主补全。"
            "信息足够时输出完整规格卡并加[DESIGN_COMPLETE]。"
        )
        temp = 0.6

    user_content = (
        f"用户MOD构想：\n{conversation}\n\n{mode_instruction}"
        f"必须包含生存影响、生态关系、风险提示。"
    )

    try:
        raw         = _call_llm(RAPID_SYSTEM_PROMPT, user_content,
                                temperature=temp)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean       = raw.replace("[DESIGN_COMPLETE]", "").strip()
        clean       = re.sub(r'\n{3,}', '\n\n', clean)
        return {"text": clean, "data": None, "is_complete": is_complete}
    except Exception as e:
        return {"text": f"意志解读失败……（{e}）",
                "data": None, "is_complete": False}

# ══════════════════════════════════════════════════════════════
# 📋 设计总结
# ══════════════════════════════════════════════════════════════

def summarize_design(messages: list) -> dict:
    """从对话提取结构化设计规格"""
    conversation = _format_conversation(messages)
    user_content = (
        f"请从以下对话中提取完整MOD设计规格。\n"
        f"重要：如果AI已给出多种对象的完整设计（如4种花），"
        f"必须全部提取到 sub_objects 中。"
        f"appearance 字段必须用中文详细描述外观（颜色+形态+特殊效果）：\n\n"
        f"{conversation}"
    )
    try:
        raw    = _call_llm(DESIGN_SUMMARY_PROMPT, user_content,
                           temperature=0.2, max_tokens=3000)
        result = _safe_parse_json(raw)
        if result:
            if "sub_objects" not in result:
                result["sub_objects"] = []
            # 校验并修复 sound_triggers
            result = _validate_and_fix_sound_triggers(result)
            # 注意：不在这里生成 image_prompts，
            # 交给 optimize_visual_prompt 专门处理
            return result
        return _fallback_design_summary(messages)
    except Exception as e:
        print(f"[WARN] summarize_design: {e}")
        return _fallback_design_summary(messages)


def _validate_and_fix_sound_triggers(spec: dict) -> dict:
    """确保 sound_triggers 存在且合理"""
    if "sound_triggers" in spec and spec["sound_triggers"]:
        return spec

    mod_type = spec.get("mod_type", "item")
    ecology  = spec.get("ecology", {})
    faction  = ecology.get("faction_notes", "")

    main_faction = "nature"
    if "暗影" in faction or "影" in ecology.get("shadow", ""):
        main_faction = "shadow"
    elif "月亮" in faction or "lunar" in str(ecology).lower():
        main_faction = "lunar"

    triggers = []
    if mod_type == "item":
        triggers.append({
            "trigger_cn":    "拾取",
            "trigger_type":  "pickup",
            "object_cn":     spec.get("main_object", {}).get("name_cn", "物品"),
            "description_cn": "拾取时的自然声响",
            "faction":       main_faction,
        })
        if spec.get("survival_impact", {}).get("is_edible"):
            triggers.append({
                "trigger_cn":    "食用",
                "trigger_type":  "eat",
                "object_cn":     spec.get("main_object", {}).get("name_cn", "物品"),
                "description_cn": "食用时的咀嚼声",
                "faction":       main_faction,
            })
        triggers.append({
            "trigger_cn":    "使用/放置",
            "trigger_type":  "use",
            "object_cn":     spec.get("main_object", {}).get("name_cn", "物品"),
            "description_cn": "使用时的激活声",
            "faction":       main_faction,
        })

    spec["sound_triggers"] = triggers
    return spec

# ══════════════════════════════════════════════════════════════
# 🎨 图片 Prompt 生成（核心重构）
# ══════════════════════════════════════════════════════════════

def _extract_visual_descriptions(spec: dict) -> list:
    """
    第一步：调用 LLM 从设计规格中提取每个对象的纯英文视觉描述。
    返回：[{"label": "中文名", "visual_en": "纯英文外观描述"}, ...]
    """
    # 构建对象列表
    all_objects = []
    main = spec.get("main_object", {})
    if main:
        all_objects.append({
            "name_cn":    main.get("name_cn", "主对象"),
            "name_en":    main.get("name_en", "main_object"),
            "appearance": main.get("appearance", ""),
        })
    for sub in spec.get("sub_objects", []):
        all_objects.append({
            "name_cn":    sub.get("name_cn", "子对象"),
            "name_en":    sub.get("name_en", "sub_object"),
            "appearance": sub.get("appearance", ""),
        })

    if not all_objects:
        return []

    # 构建请求内容
    obj_list = "\n".join(
        f"{i+1}. {obj['name_cn']}（{obj['name_en']}）：{obj['appearance']}"
        for i, obj in enumerate(all_objects)
    )
    user_content = (
        f"请为以下 {len(all_objects)} 个对象，各提取一段纯英文外观描述：\n\n"
        f"{obj_list}\n\n"
        f"要求：\n"
        f"- 每条描述 8-15 个英文单词\n"
        f"- 聚焦颜色+花型+最显著视觉特征\n"
        f"- 绝对不含中文\n"
        f"- 不含风格词（如'Don't Starve'/'gothic'等）\n"
        f"- 输出JSON数组，数量必须与输入对象数量一致（{len(all_objects)}条）"
    )

    try:
        raw    = _call_llm(IMAGE_EXTRACTION_SYSTEM, user_content,
                           temperature=0.3, max_tokens=800)
        result = _safe_parse_json(raw)

        if isinstance(result, list) and len(result) > 0:
            # 验证并清理每条描述
            validated = []
            for i, item in enumerate(result):
                if i >= len(all_objects):
                    break
                label    = item.get("label", all_objects[i]["name_cn"])
                visual   = item.get("visual_en", "")
                # 强制清理：确保纯英文
                visual   = _sanitize_english_only(visual)
                visual   = _truncate_to_words(visual, 15)
                if not visual or len(visual) < 5:
                    # 兜底：用 name_en 构造
                    name = all_objects[i]["name_en"].replace("_", " ")
                    visual = _make_fallback_visual_en(
                        all_objects[i]["name_cn"], name)
                validated.append({"label": label, "visual_en": visual})

            # 如果数量不够，补充兜底
            for i in range(len(validated), len(all_objects)):
                obj  = all_objects[i]
                name = obj["name_en"].replace("_", " ")
                validated.append({
                    "label":     obj["name_cn"],
                    "visual_en": _make_fallback_visual_en(obj["name_cn"], name),
                })
            return validated

    except Exception as e:
        print(f"[WARN] _extract_visual_descriptions: {e}")

    # 完全兜底
    return [
        {
            "label":     obj["name_cn"],
            "visual_en": _make_fallback_visual_en(
                obj["name_cn"], obj["name_en"].replace("_", " ")),
        }
        for obj in all_objects
    ]


def _make_fallback_visual_en(name_cn: str, name_en: str) -> str:
    """
    根据对象名称生成兜底英文视觉描述。
    通过关键词匹配中文名，生成有意义的英文描述。
    """
    name_lower = name_cn.lower() + name_en.lower()

    # 花朵类关键词匹配
    if any(w in name_cn for w in ["玫瑰", "rose"]):
        if any(w in name_cn for w in ["暗影", "黑", "紫", "shadow"]):
            return "dark purple rose black veins wilted glowing edges"
        elif any(w in name_cn for w in ["血", "红", "crimson", "blood"]):
            return "deep crimson rose drooping petals dark thorns"
        return "thorny rose dark petals twisted stem"

    elif any(w in name_cn for w in ["百合", "lily"]):
        if any(w in name_cn for w in ["月", "白", "lunar", "moon"]):
            return "silver white lily glowing petals blue luminous"
        return "pale lily drooping petals dark center"

    elif any(w in name_cn for w in ["罂粟", "poppy"]):
        return "deep red poppy withered drooping dark spots stem"

    elif any(w in name_cn for w in ["兰", "orchid"]):
        if any(w in name_cn for w in ["毒", "poison", "雾"]):
            return "grey green orchid pale spores mist foggy petals"
        return "exotic orchid twisted petals dark veins"

    elif any(w in name_cn for w in ["菊", "chrysanthemum"]):
        return "dark chrysanthemum layered petals wilted gothic"

    elif any(w in name_cn for w in ["花", "flower", "bloom"]):
        # 通用花朵
        if any(w in name_cn for w in ["暗影", "影", "黑", "dark", "shadow"]):
            return "dark withered flower black petals glowing veins"
        elif any(w in name_cn for w in ["月", "白", "亮", "lunar"]):
            return "pale white flower soft glow delicate petals"
        elif any(w in name_cn for w in ["血", "红", "crimson"]):
            return "crimson flower drooping petals dark center"
        elif any(w in name_cn for w in ["毒", "poison", "绿"]):
            return "sickly green flower drooping toxic mist"
        return "wilted dark flower twisted stem gothic petals"

    else:
        # 非花朵类
        name_clean = _sanitize_english_only(name_en)[:20]
        return f"dark gothic {name_clean} item twisted shadowy"


def _build_full_prompt(visual_en: str) -> str:
    """
    将对象视觉描述与风格锚定词合并，构建完整绘图 prompt。
    格式：[风格锚定词], [对象描述]
    确保总词数不超过60词。
    """
    # 清理视觉描述
    clean_visual = _sanitize_english_only(visual_en)
    clean_visual = _truncate_to_words(clean_visual, 15)

    # 拼接完整 prompt
    full = f"{DST_STYLE_ANCHOR}, {clean_visual}"

    # 总长度检查（按字符，URL友好）
    if len(full) > 400:
        # 截短风格锚定词版本
        short_anchor = (
            "Don't Starve Together art style, Tim Burton gothic cartoon, "
            "thick black ink outlines, hand-drawn, muted tones, 2D game sprite"
        )
        full = f"{short_anchor}, {clean_visual}"

    return full


def optimize_visual_prompt(design_spec: dict) -> dict:
    """
    【核心重构】生成所有对象的绘图 prompt 列表。

    流程：
    1. 调用 LLM 提取每个对象的纯英文视觉描述（8-15词）
    2. 将视觉描述与固定风格锚定词合并，构建完整 prompt
    3. 返回结构化结果供 app.py 使用

    返回：{
        "optimized_prompt": str,     # 第一张图的完整 prompt（向后兼容）
        "negative_prompt":  str,     # 统一负面提示词
        "all_prompts": [             # 每个对象一条
            {"label": "中文名", "prompt": "完整英文prompt", "visual_en": "视觉描述部分"},
            ...
        ]
    }
    """
    print("[DEBUG] optimize_visual_prompt: 开始提取视觉描述...")

    # 第一步：提取每个对象的视觉描述
    visual_items = _extract_visual_descriptions(design_spec)

    print(f"[DEBUG] 提取到 {len(visual_items)} 个对象的视觉描述：")
    for i, v in enumerate(visual_items):
        print(f"  #{i+1} [{v['label']}]: {v['visual_en']}")

    if not visual_items:
        # 终极兜底
        obj  = design_spec.get("main_object", {})
        name = obj.get("name_cn", "神秘物品")
        visual_items = [{
            "label":     name,
            "visual_en": "dark mysterious flower wilted gothic petals",
        }]

    # 第二步：构建完整 prompt
    all_prompts = []
    for item in visual_items:
        full_prompt = _build_full_prompt(item["visual_en"])
        all_prompts.append({
            "label":     item["label"],
            "prompt":    full_prompt,
            "visual_en": item["visual_en"],  # 保存视觉描述部分（调试用）
        })
        print(f"  ✓ [{item['label']}] prompt长度={len(full_prompt)}字符")
        print(f"    视觉描述: {item['visual_en']}")

    return {
        "optimized_prompt": all_prompts[0]["prompt"] if all_prompts else DST_STYLE_ANCHOR,
        "negative_prompt":  DST_NEGATIVE,
        "all_prompts":      all_prompts,
    }

# ══════════════════════════════════════════════════════════════
# 🔊 音效方案生成
# ══════════════════════════════════════════════════════════════

def generate_sound_prompts(design_spec: dict) -> dict:
    """根据设计规格生成完整音效方案"""
    main_obj  = design_spec.get("main_object", {})
    subs      = design_spec.get("sub_objects", [])
    survival  = design_spec.get("survival_impact", {})
    ecology   = design_spec.get("ecology", {})
    triggers  = design_spec.get("sound_triggers", [])

    objects_desc = f"主对象：{main_obj.get('name_cn','物品')}（{main_obj.get('name_en','item')}）"
    if subs:
        sub_names = "、".join(s.get("name_cn", "子对象") for s in subs)
        objects_desc += f"\n子对象：{sub_names}"

    if triggers:
        trigger_desc = "\n".join(
            f"- {t.get('trigger_cn','')}：{t.get('description_cn','')}（阵营：{t.get('faction','neutral')}）"
            for t in triggers
        )
    else:
        trigger_desc = "- 拾取：自然声响\n- 使用：激活音效"

    user_content = (
        f"MOD类型：{design_spec.get('mod_type', 'item')}\n"
        f"{objects_desc}\n"
        f"核心功能：{design_spec.get('core_function', '')}\n"
        f"理智影响：{survival.get('sanity_effect', '无')}\n"
        f"阵营：{ecology.get('faction_notes', '无特殊阵营')}\n"
        f"可食用：{'是' if survival.get('is_edible') else '否'}\n\n"
        f"需要音效的场景：\n{trigger_desc}\n\n"
        f"请为以上每个场景生成对应的音效合成参数。"
        f"自然系花朵用 triangle 波，影系用 sawtooth，月亮系用 sine+vibrato。"
        f"如果MOD有多种对象（如多种花），拾取音效可以共用一套参数。"
    )

    try:
        raw    = _call_llm(SOUND_DESIGN_SYSTEM, user_content, temperature=0.5)
        result = _safe_parse_json(raw)
        if result and "sound_effects" in result:
            result = _validate_sound_result(result, design_spec)
            return result
        return _fallback_sound_prompts(
            design_spec.get("mod_type", "item"),
            design_spec.get("ecology", {})
        )
    except Exception as e:
        print(f"[WARN] generate_sound_prompts: {e}")
        return _fallback_sound_prompts(
            design_spec.get("mod_type", "item"),
            design_spec.get("ecology", {})
        )


def _validate_sound_result(result: dict, design_spec: dict) -> dict:
    """验证音效结果，为缺少 synth_params 的条目补充默认值"""
    ecology      = design_spec.get("ecology", {})
    faction_note = ecology.get("faction_notes", "")

    if "暗影" in faction_note:
        default_faction = "shadow"
    elif "月亮" in faction_note:
        default_faction = "lunar"
    else:
        default_faction = "nature"

    for sfx in result.get("sound_effects", []):
        if "synth_params" not in sfx or not sfx["synth_params"]:
            faction = sfx.get("faction", default_faction)
            trigger = sfx.get("trigger_type", "pickup")
            sfx["synth_params"] = _default_synth_params(faction, trigger)

    ambient = result.get("ambient_sound", {})
    if ambient.get("needed") and not ambient.get("synth_params"):
        ambient["synth_params"] = _default_synth_params(default_faction, "ambient")
        result["ambient_sound"] = ambient

    return result


def _default_synth_params(faction: str, trigger_type: str) -> dict:
    """根据阵营和触发类型生成默认合成参数"""
    faction_base = {
        "shadow": {
            "oscillator": "sawtooth",
            "frequency_start": 120, "frequency_end": 40,
            "gain_start": 0.6, "gain_end": 0.0,
            "noise_mix": 0.5, "vibrato": False,
        },
        "lunar": {
            "oscillator": "sine",
            "frequency_start": 800, "frequency_end": 1200,
            "gain_start": 0.4, "gain_end": 0.0,
            "noise_mix": 0.05, "vibrato": True,
        },
        "nature": {
            "oscillator": "triangle",
            "frequency_start": 300, "frequency_end": 150,
            "gain_start": 0.5, "gain_end": 0.0,
            "noise_mix": 0.45, "vibrato": False,
        },
        "neutral": {
            "oscillator": "triangle",
            "frequency_start": 350, "frequency_end": 180,
            "gain_start": 0.5, "gain_end": 0.0,
            "noise_mix": 0.3, "vibrato": False,
        },
    }

    trigger_overrides = {
        "pickup": {"duration": 0.4, "frequency_start": 400, "frequency_end": 200},
        "eat":    {"duration": 0.6, "noise_mix": 0.5, "oscillator": "triangle"},
        "use":    {"duration": 0.5, "frequency_start": 300, "frequency_end": 600},
        "equip":  {"duration": 0.7, "gain_start": 0.6},
        "special":{"duration": 1.0, "vibrato": True},
        "ambient":{"duration": 2.0, "gain_start": 0.15, "gain_end": 0.15, "lfo": True},
    }

    base      = faction_base.get(faction, faction_base["nature"]).copy()
    overrides = trigger_overrides.get(trigger_type, {})
    base.update(overrides)
    base["type"]     = f"{faction}_{trigger_type}"
    base["duration"] = base.get("duration", 0.5)
    base["lfo"]      = base.get("lfo", False)
    return base

# ══════════════════════════════════════════════════════════════
# 🔊 音效参数获取（供 app.py 调用）
# ══════════════════════════════════════════════════════════════

def generate_sound_effect(search_keywords: str, prompt_en: str,
                          duration: str = "short",
                          faction: str = "nature",
                          trigger_type: str = "pickup") -> dict:
    """获取音效合成参数"""
    if not faction or faction == "neutral":
        faction = _detect_faction_from_text(prompt_en or search_keywords)

    params = _default_synth_params(faction, trigger_type)
    if duration == "medium":
        params["duration"] = max(params.get("duration", 0.5), 1.0)

    return {
        "ok":           True,
        "source":       "synth",
        "synth_params": params,
        "format":       "synth",
    }


def _detect_faction_from_text(text: str) -> str:
    """从文本中识别阵营"""
    text_lower = (text or "").lower()

    shadow_kw = ["shadow", "dark", "nightmare", "void", "horror",
                 "暗影", "黑暗", "噩梦", "影怪"]
    lunar_kw  = ["lunar", "moon", "celestial", "light", "pure",
                 "月亮", "月光", "月圆", "净化"]
    nature_kw = ["flower", "petal", "leaf", "plant", "wood", "nature",
                 "花", "叶", "植物", "自然", "草"]

    if any(w in text_lower for w in shadow_kw):
        return "shadow"
    if any(w in text_lower for w in lunar_kw):
        return "lunar"
    if any(w in text_lower for w in nature_kw):
        return "nature"
    return "neutral"

# ══════════════════════════════════════════════════════════════
# ⚙️ MOD 代码生成
# ══════════════════════════════════════════════════════════════

def design_with_llm(design_summary: str,
                    previous_conversation: list = None) -> dict:
    """根据设计规格生成完整MOD代码"""
    user_content = (
        f"根据以下MOD设计规格生成完整Lua代码"
        f"（包含San影响、阵营逻辑，多个对象变体各自生成prefab）：\n\n"
        f"{design_summary}\n\n"
        f"严格输出JSON格式，不要代码块标记。"
    )
    try:
        raw    = _call_llm(MOD_CODE_PROMPT, user_content,
                           temperature=0.25, max_tokens=4000)
        result = _safe_parse_json(raw)
        if result and "data" in result:
            return result
        return _create_fallback_mod(design_summary)
    except Exception as e:
        print(f"[ERROR] design_with_llm: {e}")
        return _create_fallback_mod(design_summary)

# ══════════════════════════════════════════════════════════════
# 🔧 Fallback 函数
# ══════════════════════════════════════════════════════════════

def _fallback_design_summary(messages: list) -> dict:
    all_text = " ".join(
        m.get("content", "") for m in messages if isinstance(m, dict))
    ts = datetime.now().strftime("%Y%m%d%H%M")
    return {
        "mod_name_en":   f"FlowerMod_{ts}",
        "mod_name_cn":   "花之MOD",
        "mod_type":      "item",
        "description":   all_text[:100],
        "core_function": "多种具有不同效果的神秘花朵",
        "main_object": {
            "name_en":    "shadow_rose",
            "name_cn":    "暗影玫瑰",
            "appearance": "深紫色玫瑰，边缘有黑色脉络，夜晚微微发光",
            "size":       "small"
        },
        "sub_objects": [
            {
                "name_en":    "lunar_lily",
                "name_cn":    "月光百合",
                "appearance": "银白色百合，月圆之夜发出柔和蓝光",
                "role":       "月亮系回神花朵",
                "size":       "small"
            }
        ],
        "stats": {
            "health": None, "damage": None, "durability": None,
            "hunger": None, "sanity": None,
            "sanity_drain": -2, "sanity_drain_rate": 60
        },
        "recipe":          ["petals x3", "nightmare_fuel x1"],
        "special_effects": ["持有时-2San/min", "影怪仇恨降低50%"],
        "ecology": {
            "pigman": "hostile", "merm": "neutral",
            "shadow": "friendly", "lunar": "neutral",
            "faction_notes": "暗影阵营"
        },
        "survival_impact": {
            "sanity_effect": "持有时每分钟-2San",
            "hunger_effect": "无影响",
            "is_edible":     True,
            "eat_effect":    "HP-5, San-20, 解除所有减益"
        },
        "risk_notes":   "夜晚持有加速吸引影怪",
        "sound_triggers": [
            {"trigger_cn": "拾取花朵", "trigger_type": "pickup",
             "object_cn": "花朵", "description_cn": "拾取时的轻柔声响",
             "faction": "nature"},
            {"trigger_cn": "食用花朵", "trigger_type": "eat",
             "object_cn": "花朵", "description_cn": "食用时的神秘音效",
             "faction": "shadow"},
        ],
        "sound_description": "自然系拾取音效+暗影系食用音效",
        "sound_prompt_en":   "flower pickup rustle shadow consume",
    }


def _fallback_sound_prompts(mod_type: str, ecology: dict = None) -> dict:
    """生成兜底音效方案（直接含 synth_params）"""
    ecology      = ecology or {}
    faction_note = ecology.get("faction_notes", "")
    if "暗影" in faction_note:
        faction = "shadow"
    elif "月亮" in faction_note:
        faction = "lunar"
    else:
        faction = "nature"

    return {
        "sound_effects": [
            {
                "trigger":        "拾取",
                "trigger_type":   "pickup",
                "description_cn": "拾取时的自然声响",
                "faction":        faction,
                "synth_params":   _default_synth_params(faction, "pickup"),
            },
            {
                "trigger":        "使用",
                "trigger_type":   "use",
                "description_cn": "使用时的激活音效",
                "faction":        faction,
                "synth_params":   _default_synth_params(faction, "use"),
            },
        ],
        "ambient_sound": {
            "needed":         False,
            "description_cn": "",
            "synth_params":   None,
        }
    }


def _create_fallback_mod(design_summary: str) -> dict:
    ts   = datetime.now().strftime("%Y%m%d%H%M")
    name = f"AiMod_{ts}"
    desc = str(design_summary)[:100]

    modinfo = f'''name = "{name}"
description = "{desc}"
author = "DST MOD Generator LETITIA"
version = "1.0"
api_version = 10
icon_atlas = "modicon.xml"
icon = "modicon.tex"
dst_compatible = true
all_clients_require_mod = true
client_only_mod = false
'''
    modmain = '''GLOBAL.setmetatable(env, {
    __index = function(t, k) return GLOBAL.rawget(GLOBAL, k) end
})
PrefabFiles = { "shadow_rose", "lunar_lily" }
AddSimPostInit(function()
    print("[AI MOD] Loaded!")
end)
'''
    prefab = '''local Assets = { Asset("ANIM", "anim/shadow_rose.zip") }
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("shadow_rose")
    inst.AnimState:SetBuild("shadow_rose")
    inst.AnimState:PlayAnimation("idle")
    if not TheWorld.ismastersim then return inst end
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst:AddComponent("edible")
    inst.components.edible.healthvalue   = -5
    inst.components.edible.hungervalue   = 10
    inst.components.edible.sanityvalue   = -20
    inst:AddComponent("stackable")
    inst.components.stackable.maxsize    = 20
    return inst
end
return Prefab("shadow_rose", fn, Assets)
'''
    return {
        "text": "✦ 混沌已凝固，花之框架已铸造。⚠️ 食用会消耗理智。",
        "data": {
            "name": name, "desc": desc,
            "files": {
                "modinfo.lua":              modinfo,
                "modmain.lua":              modmain,
                "prefabs/shadow_rose.lua":  prefab,
            }
        }
    }
