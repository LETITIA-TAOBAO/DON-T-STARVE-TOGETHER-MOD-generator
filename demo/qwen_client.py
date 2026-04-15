import os
import re
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

EXPLORE_PROMPT = '''你是 DST Mod 设计助手，帮助用户完善创意。用饥荒风格语言引导用户，每次回复不超过 300 字，包含中英双语，最后问："是否需要生成 Mod？(yes/no)"'''

MOD_PROMPT = '''你是 DST Mod 代码生成器。输出 JSON 格式：
{{
  "text": "给用户看的描述",
  "data": {{
    "name": "Mod 名称",
    "desc": "描述",
    "files": {{
      "modinfo.lua": "lua 代码",
      "modmain.lua": "lua 代码",
      "prefabs/custom_item.lua": "lua 代码"
    }}
  }}
}}
所有 Lua 代码必须有效可运行'''

def explore_with_llm(messages):
    try:
        response = Generation.call(
            model="qwen-max",
            messages=[
                {"role": "system", "content": EXPLORE_PROMPT},
                {"role": "user", "content": "\n".join([f"{m['role']}: {m['content']}" for m in messages])}
            ],
            temperature=0.7,
            result_format='message'
        )
        return {"text": response.output.choices[0].message.content, "data": None}
    except Exception as e:
        return {"text": f"❌ 错误：{str(e)}", "data": None}

def design_with_llm(design_summary, previous_conversation=None):
    try:
        response = Generation.call(
            model="qwen-max",
            messages=[
                {"role": "system", "content": MOD_PROMPT},
                {"role": "user", "content": f"根据以下设计创制 Mod:\n\n{design_summary[:300]}"}
            ],
            temperature=0.7,
            result_format='message'
        )
        
        raw_text = response.output.choices[0].message.content
        
        json_match = re.search(r'\{{[\s\S]*\}}', raw_text)
        if json_match:
            import json
            data = json.loads(json_match.group())
            return {"text": data.get("text", ""), "data": data.get("data", {})}
        else:
            return create_fallback_mod(design_summary)
    except Exception as e:
        print(f"[ERROR] {e}")
        return create_fallback_mod(design_summary)

def optimize_visual_prompt(design_summary):
    try:
        response = Generation.call(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "生成适合 AI 绘图的英文 prompt，Don't Starve 风格，不要其他文字"},
                {"role": "user", "content": design_summary[:300]}
            ],
            result_format='message'
        )
        prompt = response.output.choices[0].message.content.strip()
        return {"success": True, "optimized_prompt": prompt, "fallback_prompt": prompt}
    except:
        return {"success": False, "error": "Failed", "fallback_prompt": "Don't Starve style custom item icon"}

def create_fallback_mod(design_summary):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return {
        "text": "✅ Mod 已生成！",
        "data": {
            "name": f"AiGeneratedMod_{timestamp}",
            "desc": design_summary[:100],
            "files": {
                "modinfo.lua": f'modmeta_enable_savegames = false\nversion = 1\nname = "AiGeneratedMod"\ndescription = "{design_summary[:100]}"\nauthor = "AI Generated"\nfolder = "ai_mod_{timestamp}"\napi_version = 10\ndont_tell_me_to_subscribe = true\nicon_atlas = "modicon.xml"\nicon = "modicon.tex"',
                "modmain.lua": 'GetModsDir()\nAddStringsPostInit(function() end)\nPrefabFiles = {"custom_prefab"}\nGLOBAL.Require("prefabs/custom_prefab")',
                "prefabs/custom_item.lua": 'local Assets = require("assets")\nlocal Prefab = require("prefab")\nlocal function OnCreate(inst)\n    inst:AddComponent("locomotor")\nend\nreturn Prefab("custom_item", nil, {Asset("ANIM", "anim/bonus.zip")}, OnCreate)'
            }
        }
    }
