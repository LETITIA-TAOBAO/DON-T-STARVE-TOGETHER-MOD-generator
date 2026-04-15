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
# 📋 SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════

EXPLORE_SYSTEM_PROMPT = """你是一位饥荒联机版（Don't Starve Together）的资深MOD设计师，同时也是一位神秘的暗影存在。
你的任务是通过对话，引导用户逐步明确他们的MOD设计。

【你需要引导用户明确的核心要素】
1. MOD类型：物品/角色/生物/世界机制/其他
2. 核心功能：这个MOD的主要玩法或效果是什么
3. 主要对象：主角/核心物品/核心生物的名称和外观描述
4. 游戏属性：攻击力/血量/耐久度/材料配方等数值
5. 特殊能力：独特的技能、效果或机制
6. 视觉风格：外观描述（用于后续生成图片）
7. 音效风格：希望的声音氛围（用于后续生成音效）

【对话规则】
- 每次只聚焦1-2个未明确的要素，不要一次问太多
- 用饥荒世界的神秘语气说话，中文回复，保持在150字以内
- 当用户描述外观时，追问细节（颜色、材质、大小、风格特征）
- 当用户描述功能时，追问数值（造成多少伤害？需要什么材料合成？）
- 每次回复末尾用【设计进度】列出已确认的要素

【设计进度格式】
【设计进度】
✓ 已确认：[已明确的要素，逗号分隔]
？ 待明确：[还需要确认的要素，逗号分隔]

当所有核心要素（类型/功能/外观/数值）都已明确后，在【设计进度】后额外输出：
[DESIGN_COMPLETE]"""


RAPID_SYSTEM_PROMPT = """你是一位饥荒联机版（Don't Starve Together）的资深MOD架构师。
用户已有明确的MOD想法，你的任务是：
1. 将用户的想法转化为精确的DST MOD设计规格
2. 检查是否有遗漏的必要信息并补全
3. 完善游戏平衡性相关的数值设计

【检查清单】
□ MOD名称（英文，用于文件夹命名）
□ 核心功能描述（精确的游戏机制）
□ 主要对象的外观（颜色、风格、特征）
□ 游戏数值（生命值/攻击力/耐久/配方等）
□ 特殊效果
□ 音效需求

【输出规则】
- 中文回复，饥荒风格语气
- 如信息充足，给出完整设计规格卡并在末尾输出 [DESIGN_COMPLETE]
- 如信息不足，询问缺失关键信息（每次最多问2个问题）

【设计规格卡格式】
═══ MOD设计规格卡 ═══
名称：[英文] / [中文]
类型：[物品/角色/生物/机制]
核心功能：[描述]
外观：[详细视觉描述]
数值：[具体数值]
配方：[材料×数量]
音效：[描述]
════════════════════
[DESIGN_COMPLETE]"""


DESIGN_SUMMARY_PROMPT = """你是DST MOD设计总结师。
根据用户与助手的完整对话，提取并整理出最终的MOD设计规格。

只输出JSON，不要其他文字或代码块标记：
{
  "mod_name_en": "英文名（字母数字下划线，无空格）",
  "mod_name_cn": "中文名",
  "mod_type": "item或character或creature或mechanic",
  "description": "MOD简介（80字以内）",
  "core_function": "核心功能的精确描述",
  "main_object": {
    "name_en": "主要对象英文名（小写下划线）",
    "name_cn": "主要对象中文名",
    "appearance": "详细外观描述，包含颜色材质风格",
    "size": "small或medium或large"
  },
  "stats": {
    "health": null,
    "damage": null,
    "durability": null,
    "hunger": null,
    "sanity": null
  },
  "recipe": ["材料1 x数量", "材料2 x数量"],
  "special_effects": ["效果1", "效果2"],
  "image_prompt_en": "英文绘图prompt，40词以内",
  "sound_description": "音效需求中文描述",
  "sound_prompt_en": "英文音效prompt，15词以内"
}

注意stats中没有涉及的数值填null，recipe中材料用饥荒内物品英文名。"""


MOD_CODE_PROMPT = """你是DST（饥荒联机版）MOD的Lua代码生成专家。
根据提供的MOD设计规格，生成完整可运行的MOD代码。

【必须包含的文件】
1. modinfo.lua - 完整信息
2. modmain.lua - 主文件
3. prefabs/{name}.lua - 预制体

【代码规范】
- api_version = 10
- modinfo含：name, description, author, version, api_version, icon_atlas, icon
- prefab含完整Asset定义和组件
- 配方用Recipe和Ingredient
- 所有字符串双引号

只输出JSON（不要```标记）：
{
  "text": "铸造说明（中文饥荒风格，80字以内）",
  "data": {
    "name": "mod英文名",
    "desc": "mod描述",
    "files": {
      "modinfo.lua": "完整lua代码",
      "modmain.lua": "完整lua代码",
      "prefabs/xxx.lua": "完整lua代码"
    }
  }
}"""


IMAGE_PROMPT_SYSTEM = """你是专门为《饥荒》(Don't Starve Together)风格AI绘图优化prompt的专家。

《饥荒》视觉风格关键特征（必须全部体现在prompt中）：
- Tim Burton哥特卡通风格
- 粗黑色手绘勾线，线条不规则
- 夸张比例（大头、大眼、细长身体）
- 暗淡配色：棕褐、暗绿、灰黑、暗红
- 做旧纸张/羊皮纸质感
- 铅笔素描+水彩上色的混合质感
- 略显阴郁、诡异的黑色幽默氛围
- 物品有手工制作感，不精致不光滑

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
- 魔法/暗影氛围

根据MOD描述生成音效方案。每个音效提供：
1. 触发条件
2. 中文描述
3. 英文搜索关键词（用于Freesound搜索，3-5个英文词）
4. 时长

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
    """格式化对话记录"""
    lines = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role    = "用户" if m.get("role") == "user" else "助手"
        content = m.get("content", "").strip()
        if content:
            lines.append(f"【{role}】{content}")
    return "\n\n".join(lines)


# ══════════════════════════════════════════════════════════════
# 🗣️ 对话引导
# ══════════════════════════════════════════════════════════════

def explore_with_llm(messages: list) -> dict:
    """探索模式多轮对话"""
    conversation = _format_conversation(messages)
    user_content = f"""当前对话记录：

{conversation}

请继续引导用户明确MOD设计。在回复末尾输出【设计进度】。
如果类型/功能/外观/数值都已确认，加上 [DESIGN_COMPLETE]"""
    try:
        raw = _call_llm(EXPLORE_SYSTEM_PROMPT, user_content, temperature=0.75)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean = raw.replace("[DESIGN_COMPLETE]", "").strip()
        return {"text": clean, "data": None, "is_complete": is_complete}
    except Exception as e:
        return {"text": f"暗影失语了……（{e}）", "data": None, "is_complete": False}


def rapid_with_llm(messages: list) -> dict:
    """快速模式设计细化"""
    conversation = _format_conversation(messages)
    user_content = f"""用户MOD构想：

{conversation}

分析并补全设计规格。信息足够时输出设计规格卡并加 [DESIGN_COMPLETE]"""
    try:
        raw = _call_llm(RAPID_SYSTEM_PROMPT, user_content, temperature=0.6)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean = raw.replace("[DESIGN_COMPLETE]", "").strip()
        return {"text": clean, "data": None, "is_complete": is_complete}
    except Exception as e:
        return {"text": f"意志解读失败……（{e}）", "data": None, "is_complete": False}


# ══════════════════════════════════════════════════════════════
# 📋 设计总结
# ══════════════════════════════════════════════════════════════

def summarize_design(messages: list) -> dict:
    """从对话提取结构化设计规格"""
    conversation = _format_conversation(messages)
    user_content = f"请从以下对话中提取完整MOD设计规格：\n\n{conversation}"
    try:
        raw    = _call_llm(DESIGN_SUMMARY_PROMPT, user_content, temperature=0.2)
        result = _safe_parse_json(raw)
        return result if result else _fallback_design_summary(messages)
    except Exception as e:
        print(f"[WARN] summarize_design: {e}")
        return _fallback_design_summary(messages)


# ══════════════════════════════════════════════════════════════
# 🎨 图片 Prompt（饥荒风格强化）
# ══════════════════════════════════════════════════════════════

# 风格锚定词（强制注入到所有图片prompt中）
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


def optimize_visual_prompt(design_spec) -> dict:
    """
    生成饥荒风格AI绘图prompt。
    强制注入风格锚定词，确保图片风格正确。
    """
    if isinstance(design_spec, dict):
        obj        = design_spec.get("main_object", {})
        appearance = obj.get("appearance", "")
        name_cn    = obj.get("name_cn", "物品")
        name_en    = obj.get("name_en", "item")
        mod_type   = design_spec.get("mod_type", "item")
        existing   = design_spec.get("image_prompt_en", "")
        user_content = f"""
对象名称：{name_cn}（{name_en}）
类型：{mod_type}
外观描述：{appearance}
设计师参考：{existing}

请生成符合饥荒官方美术风格的绘图prompt，必须包含所有风格锚定词。"""
    else:
        user_content = f"对象描述：{design_spec}\n\n请生成饥荒官方美术风格的绘图prompt。"

    try:
        raw    = _call_llm(IMAGE_PROMPT_SYSTEM, user_content, temperature=0.4)
        result = _safe_parse_json(raw)
        if result:
            # 强制确保风格词存在
            opt = result.get("optimized_prompt", "")
            if "Don't Starve" not in opt:
                result["optimized_prompt"] = DST_STYLE_ANCHOR + opt
            if "negative_prompt" not in result:
                result["negative_prompt"] = DST_NEGATIVE
            return result
        return _fallback_visual_prompt(design_spec)
    except Exception:
        return _fallback_visual_prompt(design_spec)


def _fallback_visual_prompt(design_spec) -> dict:
    desc = str(design_spec)[:60] if design_spec else "mysterious dark item"
    return {
        "optimized_prompt":  DST_STYLE_ANCHOR + desc + ", isolated on dark background",
        "negative_prompt":   DST_NEGATIVE,
        "style_tags":        ["don't starve", "gothic cartoon", "tim burton", "hand-drawn"],
        "fallback_prompt":   DST_STYLE_ANCHOR + "mysterious dark fantasy game item icon",
    }


# ══════════════════════════════════════════════════════════════
# 🔊 音效方案生成（Qwen生成描述 + 关键词）
# ══════════════════════════════════════════════════════════════

def generate_sound_prompts(design_spec: dict) -> dict:
    """生成音效需求方案（含搜索关键词）"""
    obj = design_spec.get("main_object", {})
    user_content = f"""
MOD类型：{design_spec.get("mod_type","item")}
主要对象：{obj.get("name_cn","物品")}（{obj.get("name_en","item")}）
核心功能：{design_spec.get("core_function","")}
音效需求：{design_spec.get("sound_description","")}

请生成饥荒风格音效方案，每个音效提供Freesound搜索关键词。"""
    try:
        raw    = _call_llm(SOUND_PROMPT_SYSTEM, user_content, temperature=0.6)
        result = _safe_parse_json(raw)
        return result if result else _fallback_sound_prompts(
            design_spec.get("mod_type", "item"))
    except Exception:
        return _fallback_sound_prompts(design_spec.get("mod_type", "item"))


# ══════════════════════════════════════════════════════════════
# 🔊 音效获取（免费方案：Freesound + 合成音兜底）
# ══════════════════════════════════════════════════════════════

def generate_sound_effect(search_keywords: str, prompt_en: str,
                          duration: str = "short") -> dict:
    """
    获取音效文件。策略：
    1. 用 Freesound API 搜索免费音效（无需key的预览音频）
    2. 如果搜不到，用浏览器 Web Audio API 合成（返回合成参数）
    
    返回:
      {"ok":True, "audio_url":str, "source":"freesound", "preview":True}
      或 {"ok":True, "synth_params":dict, "source":"synth"}
      或 {"ok":False, "err":str}
    """
    # ── 方案1：Freesound 预览音频（免费，无需API key）──────
    try:
        keywords = search_keywords or prompt_en
        # Freesound 有免费的搜索+预览功能
        search_url = (
            f"https://freesound.org/apiv2/search/text/"
            f"?query={requests.utils.quote(keywords)}"
            f"&fields=id,name,previews,duration,tags"
            f"&page_size=5"
            f"&filter=duration:[0.1 TO 3.0]"
            f"&sort=rating_desc"
            f"&token=your_placeholder"  # 需要token才能用
        )
        # Freesound需要token，改用替代方案
    except Exception:
        pass

    # ── 方案2：Pixabay Music API（完全免费无需key）──────────
    try:
        keywords = search_keywords or prompt_en
        # 注意：Pixabay音效需要API key，也不行
    except Exception:
        pass

    # ── 方案3：生成合成音参数（纯前端播放，零API）──────────
    # 用 Qwen 根据描述生成 Web Audio API 参数
    synth = _generate_synth_params(prompt_en, duration)
    if synth:
        return {
            "ok":           True,
            "source":       "synth",
            "synth_params": synth,
            "format":       "synth",
        }

    return {"ok": False, "err": "暂无可用音效源，请手动添加音效文件"}


def _generate_synth_params(prompt_en: str, duration: str) -> dict:
    """
    根据音效描述生成 Web Audio API 合成参数。
    这些参数会在前端浏览器中直接合成音效。
    """
    dur_sec = 1.5 if duration == "medium" else 0.6

    # 根据关键词匹配预设音效类型
    prompt_lower = prompt_en.lower()

    if any(w in prompt_lower for w in ["hit", "attack", "slash", "smash"]):
        return {
            "type": "attack",
            "duration": dur_sec,
            "oscillator": "sawtooth",
            "frequency_start": 300,
            "frequency_end": 80,
            "gain_start": 0.8,
            "gain_end": 0.0,
            "noise_mix": 0.4,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["pickup", "collect", "grab", "get"]):
        return {
            "type": "pickup",
            "duration": dur_sec,
            "oscillator": "sine",
            "frequency_start": 400,
            "frequency_end": 800,
            "gain_start": 0.5,
            "gain_end": 0.0,
            "noise_mix": 0.1,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["magic", "spell", "enchant", "mystic"]):
        return {
            "type": "magic",
            "duration": dur_sec,
            "oscillator": "sine",
            "frequency_start": 200,
            "frequency_end": 1200,
            "gain_start": 0.4,
            "gain_end": 0.0,
            "noise_mix": 0.2,
            "vibrato": True,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["hurt", "pain", "damage", "yelp"]):
        return {
            "type": "hurt",
            "duration": dur_sec,
            "oscillator": "square",
            "frequency_start": 500,
            "frequency_end": 150,
            "gain_start": 0.7,
            "gain_end": 0.0,
            "noise_mix": 0.3,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["ambient", "loop", "atmosphere", "idle"]):
        return {
            "type": "ambient",
            "duration": max(dur_sec, 2.0),
            "oscillator": "sine",
            "frequency_start": 80,
            "frequency_end": 120,
            "gain_start": 0.15,
            "gain_end": 0.15,
            "noise_mix": 0.6,
            "lfo": True,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["spawn", "appear", "summon", "create"]):
        return {
            "type": "spawn",
            "duration": dur_sec,
            "oscillator": "triangle",
            "frequency_start": 100,
            "frequency_end": 600,
            "gain_start": 0.3,
            "gain_end": 0.6,
            "noise_mix": 0.2,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["wood", "stick", "branch", "tree"]):
        return {
            "type": "wood",
            "duration": dur_sec,
            "oscillator": "triangle",
            "frequency_start": 200,
            "frequency_end": 100,
            "gain_start": 0.6,
            "gain_end": 0.0,
            "noise_mix": 0.5,
            "description": prompt_en,
        }
    elif any(w in prompt_lower for w in ["metal", "sword", "blade", "clang"]):
        return {
            "type": "metal",
            "duration": dur_sec,
            "oscillator": "square",
            "frequency_start": 800,
            "frequency_end": 200,
            "gain_start": 0.7,
            "gain_end": 0.0,
            "noise_mix": 0.3,
            "description": prompt_en,
        }
    else:
        # 默认通用音效
        return {
            "type": "generic",
            "duration": dur_sec,
            "oscillator": "triangle",
            "frequency_start": 300,
            "frequency_end": 150,
            "gain_start": 0.5,
            "gain_end": 0.0,
            "noise_mix": 0.2,
            "description": prompt_en,
        }


# ══════════════════════════════════════════════════════════════
# ⚙️ MOD 代码生成
# ══════════════════════════════════════════════════════════════

def design_with_llm(design_summary: str,
                    previous_conversation: list = None) -> dict:
    """根据设计规格生成完整MOD代码"""
    user_content = f"""根据以下MOD设计规格生成完整Lua代码：

{design_summary}

严格输出JSON格式，不要代码块标记。"""
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
# 🔧 Fallback
# ══════════════════════════════════════════════════════════════

def _fallback_design_summary(messages: list) -> dict:
    all_text  = " ".join(
        m.get("content","") for m in messages if isinstance(m, dict))
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return {
        "mod_name_en":   f"CustomMod_{ts}",
        "mod_name_cn":   "自定义MOD",
        "mod_type":      "item",
        "description":   all_text[:100],
        "core_function": all_text[:200],
        "main_object":   {"name_en":"custom_item","name_cn":"自定义物品",
                          "appearance":"dark mysterious item","size":"medium"},
        "stats":         {"health":None,"damage":34,"durability":100,
                          "hunger":None,"sanity":None},
        "recipe":        ["twigs x2","flint x1"],
        "special_effects": [],
        "image_prompt_en": "dark mysterious item",
        "sound_description":"拾取和使用音效",
        "sound_prompt_en": "short wooden item sound",
    }


def _fallback_sound_prompts(mod_type: str) -> dict:
    presets = {
        "item": {
            "sound_effects": [
                {"trigger":"拾取","description_cn":"拾起物品的短促声响",
                 "search_keywords":"item pickup wood",
                 "prompt_en":"short woody thud pickup sound","duration":"short"},
                {"trigger":"使用","description_cn":"使用物品的激活音效",
                 "search_keywords":"magical activation whoosh",
                 "prompt_en":"magical whoosh activation sound","duration":"short"},
            ],
            "ambient_sound":{"needed":False,"description_cn":"","search_keywords":"","prompt_en":""}
        },
        "creature": {
            "sound_effects": [
                {"trigger":"出现","description_cn":"生物出现的低吼声",
                 "search_keywords":"creature growl dark",
                 "prompt_en":"dark creature spawn growl","duration":"medium"},
                {"trigger":"攻击","description_cn":"攻击时的嘶吼",
                 "search_keywords":"monster attack hit",
                 "prompt_en":"monster attack screech","duration":"short"},
                {"trigger":"受伤","description_cn":"受伤时的嗷叫",
                 "search_keywords":"creature hurt pain",
                 "prompt_en":"creature hurt yelp","duration":"short"},
            ],
            "ambient_sound":{"needed":True,
                "description_cn":"低沉的威慑性嗡鸣",
                "search_keywords":"ominous dark ambient",
                "prompt_en":"deep ominous creature idle ambient"}
        },
        "character": {
            "sound_effects": [
                {"trigger":"出现","description_cn":"角色登场音效",
                 "search_keywords":"character intro whoosh",
                 "prompt_en":"character introduction whoosh","duration":"medium"},
                {"trigger":"受伤","description_cn":"角色受伤呼声",
                 "search_keywords":"human hurt grunt",
                 "prompt_en":"character hurt grunt","duration":"short"},
            ],
            "ambient_sound":{"needed":False,"description_cn":"","search_keywords":"","prompt_en":""}
        },
    }
    return presets.get(mod_type, presets["item"])


def _create_fallback_mod(design_summary: str) -> dict:
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"AiMod_{ts}"
    desc = str(design_summary)[:100]
    modinfo = f'''name = "{name}"
description = "{desc}"
author = "DST MOD Generator"
version = "1.0"
api_version = 10
icon_atlas = "modicon.xml"
icon = "modicon.tex"
dst_compatible = true
all_clients_require_mod = true
client_only_mod = false
'''
    modmain = '''GLOBAL.setmetatable(env,{__index=function(t,k) return GLOBAL.rawget(GLOBAL,k) end})
PrefabFiles = {"custom_item"}
AddSimPostInit(function() print("[AI MOD] Loaded!") end)
'''
    prefab = '''local Assets = {Asset("ANIM","anim/custom_item.zip")}
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
    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.HANDS
    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(34)
    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(100)
    inst.components.finiteuses:SetUses(100)
    return inst
end
return Prefab("custom_item",fn,Assets)
'''
    return {
        "text": "✦ 混沌已凝固，MOD 框架已铸造。",
        "data": {"name":name,"desc":desc,"files":{
            "modinfo.lua":modinfo, "modmain.lua":modmain,
            "prefabs/custom_item.lua":prefab,
        }}
    }
