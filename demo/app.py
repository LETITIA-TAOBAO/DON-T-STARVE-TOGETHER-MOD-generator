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
    print(f"LLM module load failed, using mock mode")
    
    def mock_explore(messages):
        return {
            "text": f"👁️ **暗影回应了你的召唤**...\n\n关于 '{messages[-1]['content'][:30]}...' 的想法很有趣！\n请继续描述你的构想。",
            "data": None
        }
    
    def mock_design(idea):
        lua_code = f"""-- Don't Starve Together Mod
-- Based on: {idea[:100]}

local Prefab = require "prefab"

local function OnCreate(inst)
    inst:AddComponent("locomotor")
end

return Prefab("custom_entity", OnCreate)
"""
        modinfo = f"""version = 1
name = "{idea[:30]}"
description = "{idea[:100]}"
author = "AI Generated"
api_version = 10
"""
        return {
            "text": f"✅ **Mod 已成功生成！**\n\n名称：{datetime.now().strftime('%H:%M')}\n\n点击下方 ZIP 按钮下载！",
            "data": {
                "name": f"Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea[:100],
                "lua_code": lua_code,
                "modinfo": modinfo
            }
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore


# ========================
# 🎨 CSS 主题样式 (内嵌)
# ========================
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

:root {
    --thorn-brown: #8B4513;
    --highlight-gold: #FFD700;
    --text-primary: #F5E6C8;
    --border-gold: #A67C3B;
}

html, body, [class*="css"], .stApp, .st-emotion-cache {
    background-color: transparent !important;
    background: transparent !important;
}

.stApp {
    position: relative !important;
    min-height: 100vh;
}

/* 背景图层 */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -2 !important;
    background: linear-gradient(rgba(10,6,3,0.65), rgba(5,3,1,0.85)), var(--bg-url) center/cover no-repeat;
    filter: contrast(1.08) brightness(0.88);
}

/* 纹理叠加 */
.stApp::after {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -1 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.06'/%3E%3C/svg%3E");
    pointer-events: none;
}

header, footer, #MainMenu, [data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stAppViewContainer"], [data-testid="stBlockContainer"] {
    background-color: transparent !important;
    background: transparent !important;
}

[data-testid="stChatInput"].stSticky {
    background-color: transparent !important;
    border: none !important;
    margin-bottom: 0 !important;
}

[data-testid="stChatInput"] > div {
    background-color: transparent !important;
    border: none !important;
}

[data-testid="stChatInput"] textarea {
    background-color: rgba(25,20,15,0.95) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border-gold) !important;
    border-radius: 0 !important;
    font-family: 'IM Fell English SC', serif !important;
    font-size: 16px !important;
    padding: 15px !important;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
}

[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    border-color: var(--highlight-gold) !important;
}

section[data-testid="stSidebar"] {
    background: rgba(25,15,8,0.98) !important;
    border-right: 3px solid var(--border-gold) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

div[data-testid="stButton"] > button {
    font-family: 'Creepster', cursive !important;
    font-size: 18px !important;
    font-weight: bold !important;
    letter-spacing: 2px !important;
    line-height: 1.4 !important;
    padding: 20px 15px !important;
    background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
    color: var(--highlight-gold) !important;
    border: 3px solid var(--thorn-brown) !important;
    border-radius: 0 !important;
    box-shadow: 0 0 15px rgba(255,170,96,0.3), inset 0 0 20px rgba(0,0,0,0.7) !important;
    transition: all 0.3s ease !important;
    position: relative !important;
}

div[data-testid="stButton"] > button:before {
    content: "✦ ";
    position: absolute;
    top: 3px; left: 5px; right: 5px;
    color: rgba(139, 69, 19, 0.4);
    font-size: 16px;
    text-align: center;
    pointer-events: none;
}

div[data-testid="stButton"] > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 25px rgba(255,170,96,0.5), inset 0 0 20px rgba(0,0,0,0.8) !important;
    color: #FFF !important;
    border-color: var(--highlight-gold) !important;
}

h1, h2, h3 {
    font-family: 'Creepster', cursive !important;
    color: var(--highlight-gold) !important;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3) !important;
}

h1 { letter-spacing: 4px !important; }

p, span, label {
    font-family: 'IM Fell English SC', serif !important;
    color: var(--text-primary) !important;
}

.subtitle { font-family: 'Griffy', cursive !important; }

.info-card {
    background: rgba(30,20,10,0.75) !important;
    border: 2px solid var(--thorn-brown) !important;
    padding: 25px !important;
    box-shadow: 0 0 20px rgba(0,0,0,0.7), inset 0 0 15px rgba(0,0,0,0.5) !important;
    position: relative !important;
    border-radius: 0 !important;
}

.info-card::before {
    content: "✷";
    position: absolute;
    top: -12px; right: -12px;
    font-size: 28px;
    color: var(--thorn-brown);
    transform: rotate(45deg);
}

.chat-box {
    background: rgba(25,20,15,0.9) !important;
    border-left: 4px solid var(--highlight-gold) !important;
    border: 1px solid rgba(166,124,59,0.3) !important;
    padding: 15px 20px !important;
    margin: 15px 0 !important;
    color: var(--text-primary) !important;
    font-family: 'IM Fell English SC', serif !important;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
}

@keyframes flicker {
    0% { opacity: 0.7; text-shadow: 0 0 10px rgba(255,215,0,0.5); }
    50% { opacity: 1; text-shadow: 0 0 20px rgba(255,215,0,0.9); }
    100% { opacity: 0.8; text-shadow: 0 0 15px rgba(255,215,0,0.7); }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); }
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.loading-text { animation: flicker 1.5s infinite alternate; }
.mode-confirm { animation: pulse 1.5s infinite; }

::-webkit-scrollbar { width: 8px !important; }
::-webkit-scrollbar-track { background: rgba(10,6,3,0.8) !important; }
::-webkit-scrollbar-thumb { background: rgba(166,124,59,0.5) !important; border-radius: 4px !important; }
</style>
"""


# ========================
# 🔧 Session State 初始化
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
                bg64 = base64.b64encode(f.read()).decode()
                print(f"[SUCCESS] Background loaded: {bg_path}")
                return bg64
        
        url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
        with urllib.request.urlopen(url) as response:
            return base64.b64encode(response.read()).decode()
    except Exception as e:
        print(f"[ERROR] Background failed: {e}")
        return None


bg_base64 = get_background_base64()
bg_url = f'data:image/png;base64,{bg_base64}' if bg_base64 else ''


# ========================
# 🎨 注入主题
# ========================
print("[INIT] App Starting...")
final_css = THEME_CSS.replace("var(--bg-url)", f"url('{bg_url}')")
st.markdown(final_css, unsafe_allow_html=True)


# ========================
# 📄 Banner HTML
# ========================
banner_html = """
<div style="position:relative;z-index:5;text-align:center;margin:20px auto;max-width:950px;padding:50px;">
    <h1 style="font-family:'Creepster';font-size:3.8rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.5rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.8;font-size:1.15rem;max-width:850px;margin:0 auto 35px;background:transparent!important;">
    When sanity reaches zero, reality collapses.<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    Not a desperate survivor, but a creator weaving nightmares.<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:30px auto;opacity:0.7;">
    
    <div style="display:flex;gap:25px;flex-wrap:wrap;justify-content:center;margin-top:30px;">
        <div class="info-card" style="flex:1;min-width:300px;background:rgba(30,20,10,0.75)!important;border:2px solid #aa7733;padding:25px;">
            <div style="font-family:'Creepster';color:#ffaa60;font-size:1.7rem;text-align:center;margin-bottom:15px;">🔥 快速生成 / RAPID</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">For creators with clear vision. Directly forge your concept into downloadable files.<br><span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when your vision is clear. Forge it now.</span></p>
        </div>
        
        <div class="info-card" style="flex:1;min-width:300px;background:rgba(20,30,20,0.75)!important;border:2px solid #668844;padding:25px;">
            <div style="font-family:'Creepster';color:#aadd88;font-size:1.7rem;text-align:center;margin-bottom:15px;">👁️ 探索设计 / EXPLORE</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">For explorers in foggy inspiration. Dialogue with shadows to clarify your design.<br><span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span></p>
        </div>
    </div>
</div>
"""

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
    st.markdown(f'<div class="mode-confirm" style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.3);border:2px dashed {color};"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>', unsafe_allow_html=True)


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
    
    # 🌟 核心：生成 Mod 按钮
    if len(st.session_state.messages) >= 2:
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;margin:20px 0;padding:15px;background:rgba(30,20,10,0.8);border:2px solid #FFD700;border-radius:8px;">
            <h4 style="font-family:Creepster;color:#FFD700;margin:0;">✨ 准备好生成 Mod 了吗？</h4>
            <p style="color:#aaa;font-size:0.9rem;margin:5px 0 0;">将对话内容整理为完整的 Mod 代码</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1_gen, col2_gen = st.columns([4, 1])
        with col2_gen:
            if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
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
    loading_html = """<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 class="loading-text" style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
    </div>"""
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
        
        mod_data = result.get('data', {})
        if mod_data:
            new_mod = {
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "lua_code": mod_data.get('lua_code', 'print("Hello DST Mod")'),
                "modinfo": mod_data.get('modinfo', 'version = 1\\nname = "AI Mod"')
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
            chat_html = f'<div class="chat-box" style="border-left-color:{color}!important;"><b style="font-family:Creepster;color:{color};font-size:1.2rem;">{name}</b><br><span style="font-size:1.1rem;line-height:1.7;">{content}</span></div>'
            st.markdown(chat_html, unsafe_allow_html=True)


# ========================
# 📦 侧边栏 - Mod 库 + ZIP 下载
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    
    if not st.session_state.generated_mods:
        st.markdown('<div style="background:rgba(0,0,0,0.3);border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
        for mod in st.session_state.generated_mods:
            st.markdown(f'<div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="font-family:Creepster;color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>', unsafe_allow_html=True)
    
    st.divider()
    st.write(f"💬 对话：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        st.markdown("---")
        mod = st.session_state.generated_mods[-1]
        
        st.markdown("""
        <div style="background:rgba(30,20,10,0.8);border:2px solid #FFD700;padding:15px;box-shadow:0 0 20px rgba(255,215,0,0.2);">
            <h4 style="font-family:Creepster;color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4>
            <p style="color:#aaa;font-size:0.9rem;margin-bottom:15px;">Download Your Creation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建 ZIP 文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("modinfo.lua", mod.get("modinfo", ""))
            zip_file.writestr("main.lua", mod.get("lua_code", ""))
        
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
