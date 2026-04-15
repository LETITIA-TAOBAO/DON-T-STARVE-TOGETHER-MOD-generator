import json
from llm.qwen_client import call_qwen


def recommend(intent):
    intent_text = {
        "entity": intent.entity,
        "triggers": intent.triggers,
        "behaviors": intent.behaviors
    }

    prompt = f"""
你是《饥荒 Don't Starve》高级Mod开发AI。

请根据以下设计意图，生成完整开发方案：

【设计意图】
{json.dumps(intent_text, ensure_ascii=False)}

【必须输出JSON格式如下】：

{{
  "apis": ["游戏API列表（如 SpawnPrefab, AddComponent）"],
  "steps": ["详细开发步骤（必须可执行）"],
  "code": "完整Lua代码（可以直接作为prefab使用）"
}}

【要求】
- API必须真实存在于Don't Starve Mod API
- steps必须是开发步骤，不要空话
- code必须是完整Lua prefab文件
- 不要解释，只输出JSON
"""

    result = call_qwen([
        {"role": "system", "content": "你是饥荒Mod专家"},
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(result)
    except:
        start = result.find("{")
        end = result.rfind("}") + 1

        if start != -1 and end != -1:
            try:
                return json.loads(result[start:end])
            except:
                pass

    return {
        "apis": [],
        "steps": [],
        "code": "-- LLM生成失败"
    }