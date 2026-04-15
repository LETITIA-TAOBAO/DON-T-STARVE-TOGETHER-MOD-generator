import streamlit as st
import os
import base64
from datetime import datetime
import time
import urllib.request
import io
import zipfile

# ========================
# ⚠️ LLM 安全导入 + 降级模式
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"⚠️ LLM模块加载失败，使用降级模式")
    
    def mock_explore(messages):
        return {
            "text": f"""👁️ **暗影回应了你的召唤**...

你提到了关于 '{messages[-1]['content'][:30]}...' 的想法，这很有趣！

✨ **建议继续探索的方向**：
- 你希望创建什么样的生物/物品？
- 它应该有什么样的特殊能力？
- 是否符合饥荒的世界观？""",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f"""✅ **Mod 已成功生成！**

📦 **名称**: 疯狂构想 #{datetime.now().strftime('%H:%M')}

📝 **描述**:
基于你的想法 "{idea[:50]}...", 我已生成了一个完整的 Mod 设计方案。

✨ **特性**：
- 全新生物/物品
- 符合 DST 世界观  
- 包含完整 Lua 代码

🔥 **点击下方按钮下载 .zip 文件**""",
            "data": {
                "name": f"疯狂Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea[:100] + "...",
                "lua_code": generate_sample_lua(idea),  # 生成示例Lua代码
                "modinfo": generate_modinfo(idea)  # 生成modinfo
            }
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore


# ========================
# 🔧 辅助函数：生成Lua代码
# ========================
def generate_sample_lua(user_idea):
    """根据用户想法生成基础Lua代码结构"""
    return f'''-- Don't Starve Together Mod
-- 基于创意：{user_idea[:100]}

local Prefab = require "prefab"
local GlobalState = require "globalsanity"

local function OnCreate(inst)
    inst:AddComponent("locomotor")
    -- 在这里添加你的自定义组件
end

return Prefab("custom_entity", OnCreate)
'''

def generate_modinfo(user_idea):
    """生成modinfo.lua文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f'''version = 1
name = "AI Generated Mod - {user_idea[:30]}"
description = "{user_idea[:100]}"
author = "AI Assistant"
folder = "ai_generated_mod"
api_version = 10
dont_tell_me_to_subscribe = true
icon_atlas = "modicon.tex"
icon = "modicon.tex"
'''


# ========================
# 🎨 CSS 主题 (保持不变)
# ========================
def get_theme_css(bg_url):
    return f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {{
        --bg-image: url('{bg_url}') center/cover no-repeat;
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
    }}
    
    html, body {{
        background-color: rgba(0,0,0,1) !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    .stApp, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stBlockContainer"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    body::before {{
        content: "" !important;
        position: fixed !important;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1000 !important;
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), var(--bg-image) !important;
        background-size: cover !important;
    }}
    
    h1, h2, h3 {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
    }}
    
    p, span, label, div {{
        font-family: 'IM Fell English SC', serif !important;
        color: var(--text-primary) !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(20,15,10,0.98) !important;
        border: 2px solid var(--border-gold) !important;
    }}
    
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166,124,59,0.5) !important; }}
    </style>
    '''


# ========================
# 🔧 Session State
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""


# ========================
# 🖼️ 背景图处理
# ========================
def get_background_base64():
    try:
        bg_path = os.path.join(os.path.dirname(__file__), "封面图.png")
        if os.path.exists(bg_path):
            with open(bg_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        
        url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
        with urllib.request.urlopen(url) as response:
            return base64.b64encode(response.read()).decode()
    except Exception as e:
        print(f"❌ 背景图加载失败：{e}")
        return None


bg_base64 = get_background_base64()
bg_url = f'data:image/png;base64,{bg_base64}' if bg_base64 else '#000000'


# ========================
# 🎨 注入主题
# ========================
print("=== 启动 App ===")
theme_css = get_theme_css(bg_url)
st.markdown(theme_css, unsafe_allow_html=True)


# ========================
# 📄 Banner HTML
# ========================
banner_html = '''
<div style="position:relative;z-index:5;text-align:center;margin:20px auto;max-width:950px;padding:50px;">
    <h1 style="font-family:'Creepster';font-size:3.8rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.5rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.8;font-size:1.15rem;max-width:850px;margin:0 auto 35px;">
    当理智的 san 值归零，现实的法则在此崩塌。<br>
    <span style="color:#88aa66;">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
    <span style="color:#88aa66;">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:30px auto;opacity:0.7;">
    
    <div style="display:flex;gap:25px;flex-wrap:wrap;justify-content:center;margin-top:30px;">
        <div style="flex:1;min-width:300px;background:rgba(30,20,10,0.85)!important;border:2px solid #aa7733;padding:25px;">
            <div style="font-family:'Creepster';color:#ffaa60;font-size:1.7rem;text-align:center;margin-bottom:15px;">🔥 快速生成 / RAPID</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">适用于意志坚定的造物主。当你已明确 Mod 的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。</p>
        </div>
        
        <div style="flex:1;min-width:300px;background:rgba(20,30,20,0.85)!important;border:2px solid #668844;padding:25px;">
            <div style="font-family:'Creepster';color:#aadd88;font-size:1.7rem;text-align:center;margin-bottom:15px;">👁️ 探索设计 / EXPLORE</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">适用于在迷雾中低语的探索者。当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。</p>
        </div>
    </div>
</div>
'''

st.markdown(banner_html, unsafe_allow_html=True)


# ========================
# 🔘 模式选择按钮
# ========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("**🔥 快速生成**\\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

# 模式确认
if st.session_state.mode != "home":
    mode_config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    icon, color, text = mode_config.get(st.session_state.mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f'<div style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.5)!important;border:2px dashed {color};"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>', unsafe_allow_html=True)


# ========================
# 💬 探索模式 - 添加生成按钮
# ========================
if st.session_state.mode == "explore":
    st.info("💬 **与暗影对话以明确设计思路**<br>Talk to the Shadow to refine your ideas", unsafe_allow_html=True)
    
    user_input = st.chat_input("描述你的想法...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()
    
    # ⭐⭐⭐⭐⭐ 核心修复：生成 Mod 按钮 ⭐⭐⭐⭐⭐
    # 当对话达到一定条数时显示生成按钮
    if len(st.session_state.messages) >= 2:
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;margin:20px 0;padding:15px;background:rgba(30,20,10,0.8);border:2px solid #FFD700;border-radius:8px;">
            <h4 style="font-family:Creepster;color:#FFD700;margin:0;">✨ 准备好生成 Mod 了吗？</h4>
            <p style="color:#aaa;font-size:0.9rem;margin:5px 0 0;">将您的对话内容整理为完整的 Mod 代码</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1_gen, col2_gen = st.columns([4, 1])
        with col2_gen:
            if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True, type="primary"):
                # 整理所有对话上下文
                summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                st.session_state.final_prompt = summary
                
                st.session_state.mode = "generating"
                st.session_state.is_generating = True
                st.rerun()


# ========================
# 💬 快速生成模式
# ========================
elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()


# ========================
# ⏳ 生成响应阶段
# ========================
if st.session_state.is_generating:
    loading_html = '''<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);animation:flicker 1.5s infinite alternate;">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
    </div>'''
    st.markdown(loading_html, unsafe_allow_html=True)
    
    time.sleep(2.5)
    
    try:
        if st.session_state.mode == "explore":
            result = design_with_llm(st.session_state.final_prompt)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get('text', '暗影已回应...')
        })
        
        # 保存 Mod 数据
        mod_data = result.get('data', {})
        if mod_data:
            new_mod = {
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "lua_code": mod_data.get('lua_code', ''),
                "modinfo": mod_data.get('modinfo', '')
            }
            st.session_state.generated_mods.append(new_mod)
    
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ 生成失败：{str(e)}"
        })
    
    st.session_state.is_generating = False
    st.session_state.mode = "generated"
    st.rerun()


# ========================
# 💬 显示聊天历史
# ========================
if st.session_state.messages:
    for msg in st.session_state.messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            chat_html = f'<div style="background:rgba(25,20,15,0.9)!important;border-left:4px solid {color}!important;padding:15px 20px!important;margin:15px 0!important;color:#F5E6C8;font-family:\'IM Fell English SC\',serif!important;"><b style="font-family:Creepster;color:{color};font-size:1.2rem;">{name}</b><br><span style="font-size:1.1rem;line-height:1.7;">{content}</span></div>'
            st.markdown(chat_html, unsafe_allow_html=True)


# ========================
# 📦 侧边栏 - Mod 库 + 下载功能
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    
    if not st.session_state.generated_mods:
        st.markdown('<div style="background:rgba(0,0,0,0.5)!important;border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
        for mod in st.session_state.generated_mods:
            st.markdown(f'<div style="background:rgba(30,20,10,0.7)!important;border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="font-family:Creepster;color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>', unsafe_allow_html=True)
    
    st.divider()
    st.write(f"💬 对话：{len(st.session_state.messages)} 条")
    
    # ⭐⭐⭐⭐⭐ Mod 下载功能 ⭐⭐⭐⭐⭐
    if st.session_state.generated_mods:
        st.markdown("---")
        mod = st.session_state.generated_mods[-1]
        
        st.markdown("""
        <div style="background:rgba(30,20,10,0.8)!important;border:2px solid #FFD700;padding:15px;box-shadow:0 0 20px rgba(255,215,0,0.2);">
            <h4 style="font-family:Creepster;color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4>
            <p style="color:#aaa;font-size:0.9rem;margin-bottom:15px;">Download Your Creation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建 ZIP 文件下载
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 添加 modinfo.lua
            zip_file.writestr("modinfo.lua", mod.get("modinfo", ""))
            # 添加 main.lua
            zip_file.writestr("main.lua", mod.get("lua_code", "") or "print('Hello DST Mod')")
        
        zip_buffer.seek(0)
        
        col1_dl, col2_dl = st.columns(2)
        with col1_dl:
            st.download_button(
                label="💾 下载 .ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"{mod['name'].replace(' ', '_')}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        with col2_dl:
            if st.button("🔄 重新生成", use_container_width=True):
                st.session_state.mode = "explore"
                st.session_state.messages = []
                st.rerun()
    
    st.divider()
    if st.button("🗑️ 清除记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
