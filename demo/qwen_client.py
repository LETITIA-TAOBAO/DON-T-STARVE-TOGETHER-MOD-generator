import os
import re
import json
from datetime import datetime

try:
    import dashscope
    from dashscope import Generation
except ImportError:
    print("[ERROR] 请先安装: pip install dashscope")
    raise

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    print("[WARN] 请设置 DASHSCOPE_API_KEY 环境变量")

# ══════════════════════════════════════════════════════════════
# 📋 PROMPT 模板
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
- 用饥荒世界的神秘语气说话，但信息要清晰准确
- 当用户描述外观时，追问细节（颜色、材质、大小、风格）
- 当用户描述功能时，追问数值（造成多少伤害？需要什么材料合成？）
- 每次回复末尾用【设计进度】列出已确认的要素
- 当所有核心要素都已明确后，输出【设计完成】标记，并给出完整的设计总结

【输出格式】
正文回复（饥荒风格，中文为主，100-200字）

【设计进度】
✓ 已确认：[列出已明确的要素]
？ 待明确：[列出还需要确认的要素]

注意：不要过早说"设计完成"，至少要明确类型、功能、外观、数值这四个核心要素才能完成。"""


RAPID_SYSTEM_PROMPT = """你是一位饥荒联机版（Don't Starve Together）的资深MOD架构师。
用户已有明确的MOD想法，你的任务是：

1. 将用户的想法转化为精确的DST MOD设计规格
2. 检查是否有遗漏的必要信息
3. 补全游戏平衡性相关的数值设计
4. 确认视觉和音效需求

【检查清单】
□ MOD名称（英文，用于文件夹命名）
□ 核心功能描述（精确的游戏机制）
□ 主要对象的外观（颜色、风格、特征）
□ 游戏数值（生命值/攻击力/耐久/配方等）
□ 特殊效果（光效、粒子、动画）
□ 音效需求（动作音效、环境音效）
□ 平衡性考量（是否过于强力或无用）

【输出格式】
分析用户的想法，指出已知信息和缺失信息。
如果信息充足，给出完整的MOD设计规格卡：

═══════ MOD设计规格卡 ═══════
名称：[英文名] / [中文名]
类型：[物品/角色/生物/机制]
核心功能：[精确描述]
外观描述：[详细的视觉描述]
游戏数值：[具体数值]
特殊效果：[效果描述]
合成配方：[材料 × 数量]
音效需求：[音效描述]
═══════════════════════════

如果信息不足，用饥荒风格语气询问缺失的关键信息（每次最多问2个问题）。"""


DESIGN_SUMMARY_PROMPT = """你是DST MOD设计总结师。
根据用户与助手的完整对话，提取并整理出最终的MOD设计规格。

输出严格的JSON格式：
{
  "mod_name_en": "英文名（字母数字下划线）",
  "mod_name_cn": "中文名",
  "mod_type": "item/character/creature/mechanic",
  "description": "MOD简介（100字以内）",
  "core_function": "核心功能的精确描述",
  "main_object": {
    "name_en": "主要对象英文名",
    "name_cn": "主要对象中文名",
    "appearance": "详细外观描述（用于AI绘图）",
    "size": "大小描述"
  },
  "stats": {
    "health": 数字或null,
    "damage": 数字或null,
    "durability": 数字或null,
    "hunger": 数字或null,
    "sanity": 数字或null
  },
  "recipe": ["材料1 x数量", "材料2 x数量"],
  "special_effects": ["效果1", "效果2"],
  "image_prompt_en": "英文绘图prompt（50词以内，Don't Starve风格，描述主要对象外观）",
  "sound_description": "音效描述（中文，描述需要什么类型的音效）",
  "sound_prompt_en": "英文音效prompt（用于AI生成，20词以内）"
}

只输出JSON，不要其他文字。"""


MOD_CODE_PROMPT = """你是DST（饥荒联机版）MOD的Lua代码生成专家。
根据提供的MOD设计规格，生成完整可运行的MOD代码。

【DST MOD 结构要求】
必须包含以下文件：
1. modinfo.lua - MOD信息文件
2. modmain.lua - MOD主文件
3. prefabs/{name}.lua - 预制体文件（物品/角色/生物）

【代码质量要求】
- 所有Lua代码必须符合DST API规范
- modinfo.lua必须包含：name, description, author, version, api_version=10, icon_atlas, icon
- prefab文件必须包含完整的Asset定义和正确的组件添加方式
- 使用DST常用组件：health, combat, inventory, equippable, finiteuses等
- 配方使用Ingredient和Recipe构造函数
- 所有字符串使用双引号

【输出格式】
严格输出JSON：
{
  "text": "给用户看的生成说明（中文，饥荒风格，100字以内）",
  "data": {
    "name": "mod英文名",
    "desc": "mod描述",
    "files": {
      "modinfo.lua": "完整的lua代码",
      "modmain.lua": "完整的lua代码", 
      "prefabs/对象英文名.lua": "完整的lua代码"
    }
  }
}

只输出JSON，不要代码块标记。"""


IMAGE_PROMPT_OPTIMIZER = """你是专门为AI图像生成优化prompt的专家，专注于《饥荒》（Don't Starve）风格。

《饥荒》的视觉特征：
- Tim Burton哥特风格
- 黑色勾线，夸张比例
- 手绘素描质感
- 暗色系，棕褐色调
- 卡通但略显阴暗

根据输入的对象描述，生成最优的英文绘图prompt。

输出格式（JSON）：
{
  "optimized_prompt": "主prompt（40-60词，包含风格词）",
  "negative_prompt": "negative prompt（排除不需要的元素）",
  "style_tags": ["风格标签1", "风格标签2"],
  "fallback_prompt": "简化版prompt（20词，保底用）"
}

只输出JSON。"""


SOUND_PROMPT_GENERATOR = """你是游戏音效设计师，专门为《饥荒联机版》风格的MOD生成音效描述。

《饥荒》音效特征：
- 略显怪异和神秘
- 自然音效（树木、石头、动物）
- 适当的魔法/暗影音效
- 简短有力，不超过2秒

根据MOD的描述，生成音效需求。

输出格式（JSON）：
{
  "sound_effects": [
    {
      "trigger": "触发条件（如：拾取/使用/攻击/受伤）",
      "description_cn": "中文描述",
      "prompt_en": "英文音效prompt（用于AI生成，15词以内）",
      "duration": "时长（short/medium，即<1s或1-2s）"
    }
  ],
  "ambient_sound": {
    "needed": true或false,
    "description_cn": "环境音描述",
    "prompt_en": "英文prompt"
  }
}

只输出JSON。"""


# ══════════════════════════════════════════════════════════════
# 🔧 通用 LLM 调用函数
# ══════════════════════════════════════════════════════════════

def _call_llm(system_prompt: str, user_content: str,
              temperature: float = 0.7, max_tokens: int = 2000) -> str:
    """底层LLM调用，返回原始文本"""
    try:
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
    except Exception as e:
        raise RuntimeError(f"LLM调用失败: {e}")


def _safe_parse_json(text: str) -> dict | None:
    """安全解析JSON，处理常见格式问题"""
    # 去掉 markdown 代码块标记
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取第一个完整JSON对象
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass

    return None


# ══════════════════════════════════════════════════════════════
# 🗣️ 对话引导函数
# ══════════════════════════════════════════════════════════════

def explore_with_llm(messages: list) -> dict:
    """
    探索模式：引导用户逐步明确MOD设计。
    messages: [{"role": "user"/"assistant", "content": "..."}]
    返回: {"text": "回复文本", "data": None, "is_complete": bool}
    """
    # 把历史消息拼成上下文
    conversation_text = _format_conversation(messages)

    user_content = f"""以下是目前的对话记录：

{conversation_text}

请继续引导用户明确MOD设计。记住：
- 当前最新的用户输入是最后一条user消息
- 根据已有信息判断还缺少哪些核心要素
- 如果所有核心要素都已确认，在回复末尾加上标记：[DESIGN_COMPLETE]"""

    try:
        raw = _call_llm(EXPLORE_SYSTEM_PROMPT, user_content, temperature=0.75)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean_text = raw.replace("[DESIGN_COMPLETE]", "").strip()
        return {
            "text": clean_text,
            "data": None,
            "is_complete": is_complete
        }
    except Exception as e:
        return {
            "text": f"暗影失语了……（{e}）",
            "data": None,
            "is_complete": False
        }


def rapid_with_llm(messages: list) -> dict:
    """
    快速模式：将用户想法转化为精确设计规格。
    返回: {"text": "回复文本", "data": None, "is_complete": bool}
    """
    conversation_text = _format_conversation(messages)

    user_content = f"""用户的MOD构想如下：

{conversation_text}

请分析并补全设计规格。如果信息已足够完整，在回复末尾加上标记：[DESIGN_COMPLETE]"""

    try:
        raw = _call_llm(RAPID_SYSTEM_PROMPT, user_content, temperature=0.6)
        is_complete = "[DESIGN_COMPLETE]" in raw
        clean_text = raw.replace("[DESIGN_COMPLETE]", "").strip()
        return {
            "text": clean_text,
            "data": None,
            "is_complete": is_complete
        }
    except Exception as e:
        return {
            "text": f"意志解读失败……（{e}）",
            "data": None,
            "is_complete": False
        }


# ══════════════════════════════════════════════════════════════
# 📋 设计总结函数（生成MOD前调用）
# ══════════════════════════════════════════════════════════════

def summarize_design(messages: list) -> dict:
    """
    从对话历史中提取完整的MOD设计规格。
    在用户点击"铸造MOD"后、实际生成代码前调用。
    返回: 设计规格dict 或 None（解析失败时）
    """
    conversation_text = _format_conversation(messages)

    user_content = f"""请从以下对话中提取完整的MOD设计规格：

{conversation_text}

输出标准JSON格式的设计规格。"""

    try:
        raw = _call_llm(DESIGN_SUMMARY_PROMPT, user_content, temperature=0.3)
        result = _safe_parse_json(raw)
        if result:
            return result
        else:
            # 解析失败时返回基础结构
            return _fallback_design_summary(messages)
    except Exception as e:
        print(f"[WARN] summarize_design 失败: {e}")
        return _fallback_design_summary(messages)


# ══════════════════════════════════════════════════════════════
# 🎨 图片 Prompt 生成
# ══════════════════════════════════════════════════════════════

def optimize_visual_prompt(design_summary: str | dict) -> dict:
    """
    生成最优的AI绘图prompt。
    design_summary: 设计描述文本 或 summarize_design返回的dict
    返回: {"optimized_prompt": str, "negative_prompt": str,
           "style_tags": list, "fallback_prompt": str}
    """
    if isinstance(design_summary, dict):
        # 从规格dict提取关键信息
        obj = design_summary.get("main_object", {})
        appearance = obj.get("appearance", "")
        name = obj.get("name_en", "item")
        existing_prompt = design_summary.get("image_prompt_en", "")
        user_content = f"""
对象名称：{name}
外观描述：{appearance}
已有prompt参考：{existing_prompt}
MOD类型：{design_summary.get("mod_type", "item")}

请生成最优的绘图prompt。"""
    else:
        user_content = f"对象描述：{design_summary}\n\n请生成最优的绘图prompt。"

    try:
        raw = _call_llm(IMAGE_PROMPT_OPTIMIZER, user_content, temperature=0.5)
        result = _safe_parse_json(raw)
        if result:
            return result
        else:
            fallback = f"Don't Starve Together style, {str(design_summary)[:50]}, gothic cartoon, dark fantasy, hand-drawn"
            return {
                "optimized_prompt": fallback,
                "negative_prompt": "realistic, 3d, photo, bright colors",
                "style_tags": ["don't starve", "gothic", "cartoon"],
                "fallback_prompt": "Don't Starve style dark fantasy item icon"
            }
    except Exception as e:
        return {
            "optimized_prompt": "Don't Starve Together style item, gothic cartoon, dark fantasy",
            "negative_prompt": "realistic, 3d, photo",
            "style_tags": ["don't starve"],
            "fallback_prompt": "Don't Starve style item",
            "error": str(e)
        }


# ══════════════════════════════════════════════════════════════
# 🔊 音效 Prompt 生成
# ══════════════════════════════════════════════════════════════

def generate_sound_prompts(design_spec: dict) -> dict:
    """
    根据MOD设计规格生成音效需求。
    返回音效prompt列表供后续API调用。
    """
    mod_type = design_spec.get("mod_type", "item")
    core_func = design_spec.get("core_function", "")
    sound_desc = design_spec.get("sound_description", "")
    sound_prompt = design_spec.get("sound_prompt_en", "")
    obj_name = design_spec.get("main_object", {}).get("name_cn", "物品")

    user_content = f"""
MOD类型：{mod_type}
主要对象：{obj_name}
核心功能：{core_func}
音效需求描述：{sound_desc}
参考音效prompt：{sound_prompt}

请生成完整的音效方案。"""

    try:
        raw = _call_llm(SOUND_PROMPT_GENERATOR, user_content, temperature=0.6)
        result = _safe_parse_json(raw)
        if result:
            return result
        else:
            return _fallback_sound_prompts(mod_type)
    except Exception as e:
        return _fallback_sound_prompts(mod_type)


# ══════════════════════════════════════════════════════════════
# ⚙️ MOD 代码生成
# ══════════════════════════════════════════════════════════════

def design_with_llm(design_summary: str, previous_conversation: list = None) -> dict:
    """
    根据最终设计规格生成完整MOD代码。
    design_summary: 设计总结文本（来自summarize_design的JSON字符串）
    """
    user_content = f"""根据以下MOD设计规格生成完整代码：

{design_summary}

要求：
- 生成完整可运行的Lua代码
- modinfo.lua必须完整
- prefab文件必须包含所有必要组件
- 严格输出JSON格式"""

    try:
        raw = _call_llm(MOD_CODE_PROMPT, user_content, temperature=0.3, max_tokens=4000)
        result = _safe_parse_json(raw)
        if result and "data" in result:
            return result
        else:
            print(f"[WARN] design_with_llm JSON解析失败，使用fallback")
            return _create_fallback_mod(design_summary)
    except Exception as e:
        print(f"[ERROR] design_with_llm: {e}")
        return _create_fallback_mod(design_summary)


# ══════════════════════════════════════════════════════════════
# 🔧 内部辅助函数
# ══════════════════════════════════════════════════════════════

def _format_conversation(messages: list) -> str:
    """将消息列表格式化为对话文本"""
    lines = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = "用户" if m.get("role") == "user" else "助手"
        content = m.get("content", "").strip()
        if content:
            lines.append(f"【{role}】{content}")
    return "\n\n".join(lines)


def _fallback_design_summary(messages: list) -> dict:
    """JSON解析失败时的备用设计总结"""
    # 从对话中提取最基本的信息
    all_text = " ".join([m.get("content", "") for m in messages if isinstance(m, dict)])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return {
        "mod_name_en": f"CustomMod_{timestamp}",
        "mod_name_cn": "自定义MOD",
        "mod_type": "item",
        "description": all_text[:100],
        "core_function": all_text[:200],
        "main_object": {
            "name_en": "custom_item",
            "name_cn": "自定义物品",
            "appearance": "Don't Starve style dark fantasy item",
            "size": "medium"
        },
        "stats": {
            "health": None, "damage": 34,
            "durability": 100, "hunger": None, "sanity": None
        },
        "recipe": ["twigs x2", "flint x1"],
        "special_effects": [],
        "image_prompt_en": "Don't Starve Together style item, gothic cartoon, dark fantasy, hand drawn",
        "sound_description": "拾取和使用音效",
        "sound_prompt_en": "short wooden item pickup sound effect"
    }


def _fallback_sound_prompts(mod_type: str) -> dict:
    """音效生成失败时的备用方案"""
    defaults = {
        "item": {
            "sound_effects": [
                {"trigger": "拾取", "description_cn": "拾取物品声",
                 "prompt_en": "short wooden item pickup sound", "duration": "short"},
                {"trigger": "使用", "description_cn": "使用物品声",
                 "prompt_en": "item use activation sound effect", "duration": "short"}
            ],
            "ambient_sound": {"needed": False, "description_cn": "", "prompt_en": ""}
        },
        "creature": {
            "sound_effects": [
                {"trigger": "出现", "description_cn": "生物出现声",
                 "prompt_en": "creature spawn dark fantasy sound", "duration": "medium"},
                {"trigger": "攻击", "description_cn": "攻击音效",
                 "prompt_en": "creature attack hit sound effect", "duration": "short"},
                {"trigger": "受伤", "description_cn": "受伤音效",
                 "prompt_en": "creature hurt pain sound", "duration": "short"}
            ],
            "ambient_sound": {"needed": True,
                              "description_cn": "低沉的环境嗡嗡声",
                              "prompt_en": "dark ambient creature idle sound loop"}
        }
    }
    return defaults.get(mod_type, defaults["item"])


def _create_fallback_mod(design_summary: str) -> dict:
    """代码生成失败时的备用MOD"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"AiMod_{timestamp}"
    desc = design_summary[:100] if design_summary else "AI Generated Mod"

    modinfo = f'''name = "{name}"
description = "{desc}"
author = "DST MOD Generator"
version = "1.0"
api_version = 10
icon_atlas = "modicon.xml"
icon = "modicon.tex"
dont_starve_compatible = false
reign_of_giants_compatible = false
dst_compatible = true
all_clients_require_mod = true
client_only_mod = false
'''

    modmain = '''GLOBAL.setmetatable(env, {__index = function(t, k) return GLOBAL.rawget(GLOBAL, k) end})

PrefabFiles = {
    "custom_item",
}

AddSimPostInit(function()
    print("[AI MOD] Loaded successfully!")
end)
'''

    prefab = f'''local Assets = {{
    Asset("ANIM", "anim/custom_item.zip"),
}}

local function OnEquip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "custom_item", "swap_custom_item")
    owner.AnimState:Show("ARM_carry")
    owner.AnimState:Hide("ARM_normal")
end

local function OnUnequip(inst, owner)
    owner.AnimState:Hide("ARM_carry")
    owner.AnimState:Show("ARM_normal")
end

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

    inst:AddTag("sharp")

    if not TheWorld.ismastersim then
        return inst
    end

    inst.entity:AddLight()

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "custom_item"

    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.HANDS
    inst.components.equippable:SetOnEquip(OnEquip)
    inst.components.equippable:SetOnUnequip(OnUnequip)

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(34)

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(100)
    inst.components.finiteuses:SetUses(100)

    MakeHauntableLaunch(inst)
    return inst
end

return Prefab("custom_item", fn, Assets)
'''

    return {
        "text": f"✦ 混沌已凝固，MOD框架已铸造完毕。（基础模板，建议进一步优化）",
        "data": {
            "name": name,
            "desc": desc,
            "files": {
                "modinfo.lua": modinfo,
                "modmain.lua": modmain,
                "prefabs/custom_item.lua": prefab,
            }
        }
    }
