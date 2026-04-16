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
- 蜘蛛（Spider）：可被韦伯友好；巢穴等级越高危险越高
- 守卫者（Guardian）：Boss级；蜂后、熊獾、独眼巨鹿、猪王等各有机制

【关键数值参考区间】
玩家基础属性：
- 生命：150（威尔逊），范围50-400
- 饥饿：150，每分钟消耗约6.25
- 理智：200，范围100-300

武器伤害参考：
- 长矛（Spear）：34 / 锤子（Hammer）：26
- 触手刺（Tentacle Spike）：51
- 暗影剑（Dark Sword）：68，每秒 -1.33 San
- 火焰剑（Fire Sword）：42，附带燃烧

防具参考：
- 草甲：-80%伤害，耐久450
- 大理石甲：-95%伤害，降低移速+影响理智
- 暗影护甲：-70%伤害，持续掉San

食物理智影响（常见）：
- 怪物肉（Monster Meat）：-20 San，-10 HP
- 太妃糖（Taffy）：+15 San，+3 HP，+37.5 Hunger
- 蜂蜜（Honey）：+9.375 San
- 蜜汁火腿（Dragonpie）：+40 HP，+75 Hunger，+5 San

【设计潜规则（必须遵守）】
1. 强力必有代价：高伤害=掉San / 降饥饿 / 吸引仇恨 / 限时 / 高材料
2. 数值不离谱：伤害上限参考暗影剑68；HP上限参考Boss 2500-10000
3. 食物必须明确可食性：是否可食、食用后HP/Hunger/San变化
4. 生物必须定义：阵营归属、仇恨规则、是否群体攻击、是否可驯化
5. 装备必须有耐久（除非是永久性装备，需极高代价）
6. 所有机制贴合世界观：禁止科幻/现代/超出DST逻辑的设计
7. 理智机制必须考虑：暗影/月亮属性物品必须影响San

【玩家核心偏好（基于社区反馈）】
- 喜欢"有风险的强力"：暗黑系、高风险高收益
- 喜欢"能互动的生物"：可交易/跟随/仇恨/驯化
- 喜欢"San玩法"：理智博弈、影怪互动
- 喜欢"Boss机制"：多阶段、特殊弱点
- 不喜欢"无代价的强力"：破坏游戏平衡

【Few-Shot 设计示例】
示例1——暗影之刃（shadow_blade）：
- 类型：武器 / 伤害：68 / 耐久：100次
- 代价：每次攻击 -5 San；装备时每分钟 -2 San
- 生态：猪人看到持有者会敌对；影怪对持有者友好
- 合成：暗影碎片×3 + 噩梦燃料×2 + 金子×1

示例2——月光蘑菇（lunar_shroom）：
- 类型：食物 / 可食：是；HP+10，Hunger+25，San+30
- 特性：夜晚食用额外+20 San；与怪物肉共烹会相互抵消
- 生态：属月亮阵营，影怪会逃避持有者
- 生长：只在月圆夜后的草地生长，稀有
"""

# ══════════════════════════════════════════════════════════════
# 📋 SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════

EXPLORE_SYSTEM_PROMPT = f"""你是一位《Don't Starve Together》资深老玩家（游戏时长1000小时+），同时也是MOD设计师。
你对饥荒世界的每一个机制了如指掌，说话像老玩家而不是客服。

{DST_KNOWLEDGE_BASE}

【你的设计风格】
- 所有设计必须符合DST世界逻辑（San/饥饿/昼夜/阵营）
- 每次听到用户想法，脑子里先转：这会不会掉San？能不能吃？猪人/鱼人会不会仇恨它？属于影系还是月亮系？代价是什么？
- 拒绝"普通游戏设计"，必须"像饥荒老玩家在讨论"

【对话方式】
- 像朋友聊天，不是问卷调查
- 可以带一点"生存建议/吐槽感"
- 每次只推进1-2个核心点，不要一次问完所有问题
- 中文回复，控制在150字以内，禁止使用多余空行
- 偶尔用饥荒内的黑色幽默语气

【强制追问维度（每次必须覆盖至少1个）】
A) 生存代价：会掉San吗？会影响饥饿吗？有没有副作用？
B) 阵营关系：猪人/鱼人/兔人会不会仇恨？
C) 风险机制：什么情况下会失控？（必须有风险）
D) 世界适配：白天/夜晚/季节有无差异？

【示例风格（必须模仿这个语气）】
用户说："我想要一把很强的剑"
你应该说："很强？那代价是什么——掉San还是烧饥饿？饥荒里白拿力量的人，基本都活不过冬天。伤害你想要多少？暗影剑是68，但装上去就开始掉理智……你能接受高风险高收益的路线吗？"

【回复格式规范】
- 正文紧凑，不要在列表项之间插入空行
- 【设计进度】与正文之间只留一个空行
- 格式：【设计进度】✓ 已确认：[...] ？ 待明确：[...]

当类型/功能/外观/数值/代价全部明确后，额外输出：[DESIGN_COMPLETE]"""


RAPID_SYSTEM_PROMPT = f"""你是Klei Entertainment的DST数值设计师，负责把玩家创意转化为官方级MOD规格。

{DST_KNOWLEDGE_BASE}

【你的核心任务】
把用户的MOD想法转化为精确、平衡、符合DST世界观的设计规格。

【强制设计约束（必须检查）】
□ 强力效果必须有代价：掉San / 降饥饿 / 吸引仇恨 / 限制时间 / 高材料
□ 食物必须明确：能否食用 + HP/Hunger/San变化
□ 生物必须定义：阵营 + 仇恨规则 + 是否群体攻击
□ 数值必须在合理区间内
□ 装备必须有耐久（或说明为何永久）

【输出风格】
- 像官方Wiki + 资深玩家说明的混合体
- 必须有"风险提示"板块
- 中文回复，饥荒神秘语气
- 禁止在列表项之间插入多余空行

【设计规格卡格式（信息充足时输出）】
═══ MOD设计规格卡 ═══
名称：[英文名] / [中文名]
类型：[物品/角色/生物/机制]
核心功能：[精确描述]
外观：[详细视觉描述]
【数值参数】
- 主要数值：[伤害/HP/耐久等]
- 配方：[材料×数量]
【生存影响】
- 理智影响：[掉San速率/触发条件]
- 饥饿影响：[消耗量]
- 可食性：[可食/不可食，食用效果]
【生态关系】
- 对猪人：[友好/敌对/中立，原因]
- 对鱼人：[友好/敌对/中立]
- 对影怪：[友好/敌对/中立]
- 对月亮阵营：[友好/敌对/中立]
【风险提示】
⚠️ [设计的主要风险和代价]
【特殊效果】
- [效果1]
- [效果2]
════════════════════
[DESIGN_COMPLETE]

如信息不足，每次最多追问2个关键问题。"""


DESIGN_SUMMARY_PROMPT = f"""你是DST MOD设计总结师，负责从对话中提取结构化设计规格。

参考以下DST世界知识确保数值合理：
{DST_KNOWLEDGE_BASE}

根据完整对话，提取最终MOD规格，只输出JSON，不要其他内容：
{{
  "mod_name_en": "英文名（字母数字下划线，无空格）",
  "mod_name_cn": "中文名",
  "mod_type": "item或character或creature或mechanic",
  "description": "MOD简介（80字以内）",
  "core_function": "核心功能的精确描述",
  "main_object": {{
    "name_en": "主要对象英文名（小写下划线）",
    "name_cn": "主要对象中文名",
    "appearance": "详细外观描述，包含颜色材质风格",
    "size": "small或medium或large"
  }},
  "sub_objects": [
    {{
      "name_en": "子对象英文名（小写下划线）",
      "name_cn": "子对象中文名",
      "appearance": "详细外观描述，与主对象有明显区别",
      "role": "该对象在MOD中的作用",
      "size": "small或medium或large"
    }}
  ],
  "stats": {{
    "health": null,
    "damage": null,
    "durability": null,
    "hunger": null,
    "sanity": null,
    "sanity_drain": null,
    "sanity_drain_rate": null
  }},
  "recipe": ["材料1 x数量", "材料2 x数量"],
  "special_effects": ["效果1（含代价描述）", "效果2"],
  "ecology": {{
    "pigman": "friendly或hostile或neutral",
    "merm": "friendly或hostile或neutral",
    "shadow": "friendly或hostile或neutral",
    "lunar": "friendly或hostile或neutral",
    "faction_notes": "阵营归属说明"
  }},
  "survival_impact": {{
    "sanity_effect": "理智影响描述",
    "hunger_effect": "饥饿影响描述",
    "is_edible": false,
    "eat_effect": "食用效果（不可食填null）"
  }},
  "risk_notes": "主要风险与代价说明",
  "image_prompts": [
    {{
      "label": "对象中文名或描述（如：暗影玫瑰）",
      "prompt_en": "该对象的英文绘图prompt，30词以内，聚焦外观差异"
    }}
  ],
  "sound_description": "音效需求中文描述",
  "sound_prompt_en": "英文音效prompt，15词以内"
}}

注意：
- sub_objects：如果MOD包含多种花/生物/物品变体，每种都列出来，最多3个
- image_prompts：每个对象（主+子）各生成一条，label与对象名对应
- stats中没有涉及的数值填null
- recipe中材料用饥荒内物品英文名"""


MOD_CODE_PROMPT = """你是DST（饥荒联机版）MOD的Lua代码生成专家。
根据提供的MOD设计规格，生成完整可运行的MOD代码。

【必须包含的文件】
- modinfo.lua：完整信息
- modmain.lua：主文件，包含生态关系/阵营逻辑，为每个子对象注册prefab
- prefabs/{name}.lua：每个对象各一个prefab文件

【代码规范】
- api_version = 10
- modinfo含：name, description, author, version, api_version, icon_atlas, icon
- prefab含完整Asset定义和所有组件
- 必须实现理智影响（如设计中有San代价）
- 必须实现阵营仇恨逻辑（如设计中有阵营关系）
- 配方用Recipe和Ingredient（含Placer）
- 食物必须用edible组件（如设计中可食）
- 所有字符串用双引号
- 如有多个对象变体，为每个生成独立prefab

只输出JSON（不要```标记）：
{
  "text": "铸造说明（中文饥荒风格，100字以内，包含主要代价提示）",
  "data": {
    "name": "mod英文名",
    "desc": "mod描述",
    "files": {
      "modinfo.lua": "完整lua代码",
      "modmain.lua": "完整lua代码",
      "prefabs/main_object.lua": "完整lua代码",
      "prefabs/sub_object_1.lua": "完整lua代码（如有）"
    }
  }
}"""


IMAGE_PROMPT_SYSTEM = """你是专门为《饥荒》(Don't Starve Together)风格AI绘图优化prompt的专家。

《饥荒》视觉风格关键特征（必须全部体现）：
- Tim Burton哥特卡通风格
- 粗黑色手绘勾线，线条不规则
- 夸张比例（大头、大眼、细长身体）
- 暗淡配色：棕褐、暗绿、灰黑、暗红
- 做旧纸张/羊皮纸质感
- 铅笔素描+水彩上色的混合质感
- 略显阴郁、诡异的黑色幽默氛围
- 物品有手工制作感，不精致不光滑
- 透明背景，2D游戏贴图风格

【必须包含的风格锚定词】
Don't Starve Together game art style, Tim Burton inspired gothic cartoon,
thick black ink outlines, hand-drawn sketch texture, muted earth tones,
parchment paper background, dark whimsical, 2D game asset

只输出JSON：
{
  "optimized_prompt": "完整英文prompt（60词以内，风格词+对象描述）",
  "negative_prompt": "realistic, 3d render, photographic, bright saturated colors, anime, smooth shading, modern, clean lines, digital painting, gradient",
  "style_tags": ["don't starve", "gothic cartoon", "tim burton", "hand-drawn"],
  "fallback_prompt": "Don't Starve Together game art style, Tim Burton gothic cartoon, thick black ink outlines, hand-drawn sketch, muted earth tones, dark whimsical game item icon, parchment background"
}"""


SOUND_PROMPT_SYSTEM = """你是游戏音效设计师，专门为《饥荒联机版》风格MOD设计音效方案。

《饥荒》音效特征：
- 略显怪异和神秘
- 自然材质（木头、石头、金属碰撞）
- 简短有力，不超过2秒
- 魔法/暗影氛围带有低频共鸣

根据MOD描述生成音效方案，每个音效提供触发条件、中文描述、英文搜索关键词（Freesound，3-5词）、时长。

只输出JSON：
{
  "sound_effects": [
    {
      "trigger": "触发条件中文",
      "description_cn": "音效中文描述",
      "search_keywords": "freesound search keywords in english",
      "prompt_en": "detailed english sound description",
      "duration": "short或medium"
    }
  ],
  "ambient_sound": {
    "needed": true或false,
    "description_cn": "环境音描述",
    "search_keywords": "ambient search keywords",
    "prompt_en": "ambient description"
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
    return None


def _format_conversation(messages: list) -> str:
    """格式化对话记录，避免多余空行"""
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

# ══════════════════════════════════════════════════════════════
# 🗣️ 对话引导
# ══════════════════════════════════════════════════════════════

def explore_with_llm(messages: list) -> dict:
    """探索模式多轮对话（DST老玩家风格）"""
    conversation = _format_conversation(messages)
    user_content = (
        f"当前对话记录：\n{conversation}\n\n"
        f"请以DST资深老玩家的语气继续引导设计。"
        f"必须追问生存代价/阵营关系/风险机制中至少1个维度。"
        f"回复末尾附上【设计进度】，格式：【设计进度】✓ 已确认：[...] ？ 待明确：[...]"
        f"类型/功能/外观/数值/代价全部明确后加 [DESIGN_COMPLETE]"
    )
    try:
        raw         = _call_llm(EXPLORE_SYSTEM_PROMPT, user_content,
                                temperature=0.75)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean       = raw.replace("[DESIGN_COMPLETE]", "").strip()
        clean       = re.sub(r'\n{3,}', '\n\n', clean)
        return {"text": clean, "data": None, "is_complete": is_complete}
    except Exception as e:
        return {"text": f"暗影失语了……（{e}）",
                "data": None, "is_complete": False}


def rapid_with_llm(messages: list) -> dict:
    """快速模式设计细化（官方数值策划风格）"""
    conversation = _format_conversation(messages)
    user_content = (
        f"用户MOD构想：\n{conversation}\n\n"
        f"按照强制设计约束检查并补全规格。"
        f"必须包含生存影响、生态关系、风险提示三个板块。"
        f"信息足够时输出完整规格卡并加 [DESIGN_COMPLETE]"
    )
    try:
        raw         = _call_llm(RAPID_SYSTEM_PROMPT, user_content,
                                temperature=0.6)
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
    """从对话提取结构化设计规格（含多对象支持）"""
    conversation = _format_conversation(messages)
    user_content = (
        f"请从以下对话中提取完整MOD设计规格（含多对象/多变体信息）：\n\n"
        f"{conversation}"
    )
    try:
        raw    = _call_llm(DESIGN_SUMMARY_PROMPT, user_content,
                           temperature=0.2)
        result = _safe_parse_json(raw)
        if result:
            # 兼容旧格式：若没有 image_prompts，从 main_object 构建
            if "image_prompts" not in result:
                result["image_prompts"] = _build_image_prompts_from_spec(result)
            # 兼容旧格式：若没有 sub_objects，初始化为空列表
            if "sub_objects" not in result:
                result["sub_objects"] = []
            return result
        return _fallback_design_summary(messages)
    except Exception as e:
        print(f"[WARN] summarize_design: {e}")
        return _fallback_design_summary(messages)


def _build_image_prompts_from_spec(spec: dict) -> list:
    """从规格中构建 image_prompts 列表（兼容旧格式）"""
    prompts = []
    obj = spec.get("main_object", {})
    if obj:
        prompts.append({
            "label":     obj.get("name_cn", "主对象"),
            "prompt_en": obj.get("appearance", "dark mysterious item")[:80],
        })
    for sub in spec.get("sub_objects", []):
        prompts.append({
            "label":     sub.get("name_cn", "子对象"),
            "prompt_en": sub.get("appearance", "dark item variant")[:80],
        })
    return prompts

# ══════════════════════════════════════════════════════════════
# 🎨 图片 Prompt（饥荒风格强化，支持多对象）
# ══════════════════════════════════════════════════════════════

DST_STYLE_ANCHOR = (
    "Don't Starve Together game art style, "
    "Tim Burton inspired gothic cartoon, "
    "thick black ink outlines, hand-drawn sketch texture, "
    "muted earth tones, parchment paper background, "
    "dark whimsical, 2D game asset, "
)

DST_NEGATIVE = (
    "realistic, 3d render, photographic, bright saturated colors, "
    "anime, smooth shading, modern, clean lines, digital painting, "
    "gradient, text, watermark, logo, blurry"
)


def optimize_visual_prompt(design_spec: dict) -> dict:
    """
    生成饥荒风格 AI 绘图 prompt。
    返回值新增 `all_prompts` 列表，对应每个对象的独立 prompt。
    格式：[{"label": "暗影玫瑰", "prompt": "...", "negative": "..."}, ...]
    """
    obj        = design_spec.get("main_object", {})
    appearance = obj.get("appearance", "")
    name_cn    = obj.get("name_cn", "物品")
    name_en    = obj.get("name_en", "item")
    mod_type   = design_spec.get("mod_type", "item")
    ecology    = design_spec.get("ecology", {})
    faction    = ecology.get("faction_notes", "")

    # 从 design_spec 提取预设 image_prompts（summarize_design 填充的）
    preset_prompts = design_spec.get("image_prompts", [])

    user_content = (
        f"对象名称：{name_cn}（{name_en}）\n"
        f"类型：{mod_type}\n"
        f"外观描述：{appearance}\n"
        f"阵营特征：{faction}\n\n"
        f"请生成符合饥荒官方美术风格的绘图prompt，必须包含所有风格锚定词。"
    )

    try:
        raw    = _call_llm(IMAGE_PROMPT_SYSTEM, user_content, temperature=0.4)
        result = _safe_parse_json(raw)
        if result:
            opt = result.get("optimized_prompt", "")
            if "Don't Starve" not in opt:
                result["optimized_prompt"] = DST_STYLE_ANCHOR + opt
            if "negative_prompt" not in result:
                result["negative_prompt"] = DST_NEGATIVE

            # 构建 all_prompts：优先用 preset_prompts，否则从 sub_objects 补充
            all_prompts = _build_all_prompts(
                design_spec, result["optimized_prompt"], result["negative_prompt"]
            )
            result["all_prompts"] = all_prompts
            return result

        return _fallback_visual_prompt(design_spec)

    except Exception:
        return _fallback_visual_prompt(design_spec)


def _build_all_prompts(design_spec: dict,
                       base_prompt: str,
                       negative: str) -> list:
    """
    根据 image_prompts / sub_objects 构建每个对象的独立绘图 prompt 列表。
    每条：{"label": str, "prompt": str, "negative": str}
    """
    preset = design_spec.get("image_prompts", [])
    obj    = design_spec.get("main_object", {})
    subs   = design_spec.get("sub_objects", [])
    result = []

    if preset:
        # 有预设 prompt：为每个预设条目生成带风格锚定词的完整 prompt
        for item in preset:
            raw_prompt = item.get("prompt_en", "")
            label      = item.get("label", "")
            full_prompt = (
                DST_STYLE_ANCHOR + raw_prompt
                if "Don't Starve" not in raw_prompt
                else raw_prompt
            )
            result.append({
                "label":    label,
                "prompt":   full_prompt,
                "negative": negative,
            })
    else:
        # 无预设：主对象用 base_prompt，子对象加差异词
        main_label = obj.get("name_cn", "主对象")
        result.append({
            "label":    main_label,
            "prompt":   base_prompt,
            "negative": negative,
        })
        variant_suffixes = [
            "different color variation, same art style",
            "alternate design variant, same art style",
            "different composition, same art style",
        ]
        for idx, sub in enumerate(subs[:3]):
            sub_appearance = sub.get("appearance", "")
            sub_label      = sub.get("name_cn", f"变体{idx+1}")
            suffix         = variant_suffixes[idx % len(variant_suffixes)]
            sub_prompt     = (
                f"{DST_STYLE_ANCHOR}{sub_appearance}, {suffix}"
                if sub_appearance
                else f"{base_prompt}, {suffix}"
            )
            result.append({
                "label":    sub_label,
                "prompt":   sub_prompt,
                "negative": negative,
            })

    return result


def _fallback_visual_prompt(design_spec) -> dict:
    desc = ""
    if isinstance(design_spec, dict):
        obj  = design_spec.get("main_object", {})
        desc = obj.get("appearance", str(design_spec)[:60])
    else:
        desc = str(design_spec)[:60]

    base = DST_STYLE_ANCHOR + (desc or "mysterious dark item")
    return {
        "optimized_prompt": base,
        "negative_prompt":  DST_NEGATIVE,
        "style_tags":       ["don't starve", "gothic cartoon",
                             "tim burton", "hand-drawn"],
        "fallback_prompt":  DST_STYLE_ANCHOR + "mysterious dark fantasy game item icon",
        "all_prompts": [{
            "label":    "主对象",
            "prompt":   base,
            "negative": DST_NEGATIVE,
        }],
    }

# ══════════════════════════════════════════════════════════════
# 🔊 音效方案生成
# ══════════════════════════════════════════════════════════════

def generate_sound_prompts(design_spec: dict) -> dict:
    """生成音效需求方案（含搜索关键词）"""
    obj      = design_spec.get("main_object", {})
    survival = design_spec.get("survival_impact", {})
    ecology  = design_spec.get("ecology", {})
    user_content = (
        f"MOD类型：{design_spec.get('mod_type', 'item')}\n"
        f"主要对象：{obj.get('name_cn', '物品')}（{obj.get('name_en', 'item')}）\n"
        f"核心功能：{design_spec.get('core_function', '')}\n"
        f"理智影响：{survival.get('sanity_effect', '')}\n"
        f"阵营归属：{ecology.get('faction_notes', '')}\n"
        f"音效需求：{design_spec.get('sound_description', '')}\n\n"
        f"请生成饥荒风格音效方案，体现阵营特色（影系偏低沉/月亮系偏空灵）。"
    )
    try:
        raw    = _call_llm(SOUND_PROMPT_SYSTEM, user_content, temperature=0.6)
        result = _safe_parse_json(raw)
        return (result if result
                else _fallback_sound_prompts(design_spec.get("mod_type", "item")))
    except Exception:
        return _fallback_sound_prompts(design_spec.get("mod_type", "item"))

# ══════════════════════════════════════════════════════════════
# 🔊 音效合成参数生成
# ══════════════════════════════════════════════════════════════

def generate_sound_effect(search_keywords: str, prompt_en: str,
                          duration: str = "short") -> dict:
    """获取音效（Web Audio API 合成参数）"""
    synth = _generate_synth_params(prompt_en or search_keywords, duration)
    if synth:
        return {"ok": True, "source": "synth",
                "synth_params": synth, "format": "synth"}
    return {"ok": False, "err": "暂无可用音效源，请手动添加音效文件"}


def _generate_synth_params(prompt_en: str, duration: str) -> dict:
    """根据音效描述生成 Web Audio API 合成参数"""
    dur_sec      = 1.5 if duration == "medium" else 0.6
    prompt_lower = (prompt_en or "").lower()

    if any(w in prompt_lower for w in
           ["shadow", "dark", "nightmare", "horror", "void"]):
        return {"type": "shadow", "duration": dur_sec,
                "oscillator": "sawtooth",
                "frequency_start": 120, "frequency_end": 40,
                "gain_start": 0.6, "gain_end": 0.0,
                "noise_mix": 0.5, "vibrato": True, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["lunar", "moon", "celestial", "pure", "light"]):
        return {"type": "lunar", "duration": dur_sec,
                "oscillator": "sine",
                "frequency_start": 800, "frequency_end": 1600,
                "gain_start": 0.4, "gain_end": 0.0,
                "noise_mix": 0.05, "vibrato": True, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["hit", "attack", "slash", "smash", "strike"]):
        return {"type": "attack", "duration": dur_sec,
                "oscillator": "sawtooth",
                "frequency_start": 300, "frequency_end": 80,
                "gain_start": 0.8, "gain_end": 0.0,
                "noise_mix": 0.4, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["pickup", "collect", "grab", "get", "item"]):
        return {"type": "pickup", "duration": dur_sec,
                "oscillator": "sine",
                "frequency_start": 400, "frequency_end": 800,
                "gain_start": 0.5, "gain_end": 0.0,
                "noise_mix": 0.1, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["magic", "spell", "enchant", "mystic", "summon"]):
        return {"type": "magic", "duration": dur_sec,
                "oscillator": "sine",
                "frequency_start": 200, "frequency_end": 1200,
                "gain_start": 0.4, "gain_end": 0.0,
                "noise_mix": 0.2, "vibrato": True, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["hurt", "pain", "damage", "yelp", "cry"]):
        return {"type": "hurt", "duration": dur_sec,
                "oscillator": "square",
                "frequency_start": 500, "frequency_end": 150,
                "gain_start": 0.7, "gain_end": 0.0,
                "noise_mix": 0.3, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["ambient", "loop", "atmosphere", "idle", "wind"]):
        return {"type": "ambient", "duration": max(dur_sec, 2.0),
                "oscillator": "sine",
                "frequency_start": 80, "frequency_end": 120,
                "gain_start": 0.15, "gain_end": 0.15,
                "noise_mix": 0.6, "lfo": True, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["spawn", "appear", "create", "craft", "forge"]):
        return {"type": "spawn", "duration": dur_sec,
                "oscillator": "triangle",
                "frequency_start": 100, "frequency_end": 600,
                "gain_start": 0.3, "gain_end": 0.6,
                "noise_mix": 0.2, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["wood", "stick", "branch", "tree", "nature",
            "flower", "petal", "leaf", "bloom", "plant"]):
        return {"type": "wood", "duration": dur_sec,
                "oscillator": "triangle",
                "frequency_start": 200, "frequency_end": 100,
                "gain_start": 0.6, "gain_end": 0.0,
                "noise_mix": 0.5, "description": prompt_en}

    if any(w in prompt_lower for w in
           ["metal", "sword", "blade", "clang", "iron", "gold"]):
        return {"type": "metal", "duration": dur_sec,
                "oscillator": "square",
                "frequency_start": 800, "frequency_end": 200,
                "gain_start": 0.7, "gain_end": 0.0,
                "noise_mix": 0.3, "description": prompt_en}

    return {"type": "generic", "duration": dur_sec,
            "oscillator": "triangle",
            "frequency_start": 300, "frequency_end": 150,
            "gain_start": 0.5, "gain_end": 0.0,
            "noise_mix": 0.2, "description": prompt_en}

# ══════════════════════════════════════════════════════════════
# ⚙️ MOD 代码生成
# ══════════════════════════════════════════════════════════════

def design_with_llm(design_summary: str,
                    previous_conversation: list = None) -> dict:
    """根据设计规格生成完整MOD代码（支持多prefab）"""
    user_content = (
        f"根据以下MOD设计规格生成完整Lua代码"
        f"（包含San影响、阵营逻辑，如有多个对象变体请各自生成prefab）：\n\n"
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
        "mod_name_en":   f"CustomMod_{ts}",
        "mod_name_cn":   "自定义MOD",
        "mod_type":      "item",
        "description":   all_text[:100],
        "core_function": all_text[:200],
        "main_object": {
            "name_en":    "custom_item",
            "name_cn":    "自定义物品",
            "appearance": "dark mysterious item with thick black outlines",
            "size":       "medium"
        },
        "sub_objects": [],
        "stats": {
            "health": None, "damage": 34, "durability": 100,
            "hunger": None, "sanity": None,
            "sanity_drain": None, "sanity_drain_rate": None
        },
        "recipe":          ["twigs x2", "flint x1"],
        "special_effects": [],
        "ecology": {
            "pigman": "neutral", "merm": "neutral",
            "shadow": "neutral", "lunar": "neutral",
            "faction_notes": "无特殊阵营"
        },
        "survival_impact": {
            "sanity_effect": "无影响",
            "hunger_effect": "无影响",
            "is_edible":     False,
            "eat_effect":    None
        },
        "risk_notes":        "无特殊风险",
        "image_prompts": [{
            "label":     "自定义物品",
            "prompt_en": "dark mysterious item with thick black outlines",
        }],
        "sound_description": "拾取和使用音效",
        "sound_prompt_en":   "short wooden item pickup sound",
    }


def _fallback_sound_prompts(mod_type: str) -> dict:
    presets = {
        "item": {
            "sound_effects": [
                {"trigger": "拾取", "description_cn": "拾起物品的短促声响",
                 "search_keywords": "item pickup wood",
                 "prompt_en": "short woody thud pickup sound",
                 "duration": "short"},
                {"trigger": "使用", "description_cn": "使用物品的激活音效",
                 "search_keywords": "magical activation whoosh",
                 "prompt_en": "magical whoosh activation sound",
                 "duration": "short"},
            ],
            "ambient_sound": {
                "needed": False, "description_cn": "",
                "search_keywords": "", "prompt_en": ""}
        },
        "creature": {
            "sound_effects": [
                {"trigger": "出现", "description_cn": "生物出现的低吼声",
                 "search_keywords": "creature growl dark shadow",
                 "prompt_en": "dark shadow creature spawn growl",
                 "duration": "medium"},
                {"trigger": "攻击", "description_cn": "攻击时的嘶吼",
                 "search_keywords": "monster attack hit screech",
                 "prompt_en": "monster attack screech",
                 "duration": "short"},
                {"trigger": "受伤", "description_cn": "受伤时的嗷叫",
                 "search_keywords": "creature hurt pain yelp",
                 "prompt_en": "creature hurt yelp",
                 "duration": "short"},
            ],
            "ambient_sound": {
                "needed": True,
                "description_cn": "低沉的威慑性嗡鸣",
                "search_keywords": "ominous dark ambient creature",
                "prompt_en": "deep ominous creature idle ambient"}
        },
        "character": {
            "sound_effects": [
                {"trigger": "出现", "description_cn": "角色登场音效",
                 "search_keywords": "character intro whoosh",
                 "prompt_en": "character introduction whoosh",
                 "duration": "medium"},
                {"trigger": "受伤", "description_cn": "角色受伤呼声",
                 "search_keywords": "human hurt grunt",
                 "prompt_en": "character hurt grunt",
                 "duration": "short"},
            ],
            "ambient_sound": {
                "needed": False, "description_cn": "",
                "search_keywords": "", "prompt_en": ""}
        },
    }
    return presets.get(mod_type, presets["item"])


def _create_fallback_mod(design_summary: str) -> dict:
    ts   = datetime.now().strftime("%Y%m%d%H%M")
    name = f"AiMod_{ts}"
    desc = str(design_summary)[:100]

    modinfo = f'''name = "{name}"
description = "{desc}"
author = "DST MOD Generator · LETITIA"
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

PrefabFiles = { "custom_item" }

AddSimPostInit(function()
    print("[AI MOD] Loaded successfully!")
end)
'''
    prefab = '''local Assets = {
    Asset("ANIM", "anim/custom_item.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("custom_item")
    inst.AnimState:SetBuild("custom_item")
    inst.AnimState:PlayAnimation("idle")

    if not TheWorld.ismastersim then return inst end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(34)

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(100)
    inst.components.finiteuses:SetUses(100)
    inst.components.finiteuses:SetOnFinished(inst.Remove)

    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.HANDS
    inst.components.equippable:SetOnEquip(function(inst, owner)
        owner.components.sanity.dapperness = TUNING.DAPPERNESS_SMALL * -1
    end)
    inst.components.equippable:SetOnUnequip(function(inst, owner)
        owner.components.sanity.dapperness = 0
    end)

    return inst
end

return Prefab("custom_item", fn, Assets)
'''
    return {
        "text": (
            "✦ 混沌已凝固，MOD 框架已铸造。\n"
            "⚠️ 注意：装备时会持续消耗理智，这是强力的代价。"
        ),
        "data": {
            "name": name, "desc": desc,
            "files": {
                "modinfo.lua":             modinfo,
                "modmain.lua":             modmain,
                "prefabs/custom_item.lua": prefab,
            }
        }
    }
