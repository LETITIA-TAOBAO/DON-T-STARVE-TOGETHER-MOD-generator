import streamlit as st
import os
import base64
from datetime import datetime
import time

# ========================
# ⚠️ LLM 安全导入 + 降级模式
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"⚠️ LLM 模块加载失败，使用降级模式：{str(e)}")
    
    def mock_explore(messages):
        return {
            "text": f"""👁️ **暗影回应了你的召唤**...

让我来帮你完善这个疯狂的想法。

你提到了关于 "{messages[-1]['content'][:30]}..." 的想法，这是一个非常有趣的方向！

✨ **建议继续探索的方向**：
- 你希望创建什么样的生物/物品？
- 它应该有什么样的特殊能力？
- 是否符合饥荒的世界观？

(The shadows respond to your summoning...)""",
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
- 可直接下载到游戏

The shadows have woven your madness into reality.""",
            "data": {
                "name": f"疯狂Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea[:100] + "...",
                "status": "ready"
            }
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore

# ========================
# 🎨 主题样式 (内嵌)
# ========================
THEME_HTML = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

:root {
    --thorn-brown: #8B4513;
    --highlight-gold: #FFD700;
    --orange-glow: #ffaa60;
    --green-glow: #66aa66;
    --dark-wood: #2a1a0c;
    --text-primary: #F5E6C8;
    --border-gold: #A67C3B;
    --overlay-black: rgba(5, 3, 1, 0.95);
}

html, body, .stApp {
    background-color: transparent !important;
    background: transparent !important;
}

.stApp {
    position: relative !important;
    min-height: 100vh;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -2 !important;
    background: 
        linear-gradient(rgba(10,6,3,0.7), rgba(5,3,1,0.9)),
        url('https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80') center/cover no-repeat;
    filter: contrast(1.1) brightness(0.9);
}

.stApp::after {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -1 !important;
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23A67C3B' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.5;
    pointer-events: none;
}

header, footer, #MainMenu, [data-testid="stHeader"], [data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stBlockContainer"],
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
    background: transparent !important;
}

section[data-testid="stSidebar"] {
    background: rgba(25,15,8,0.98) !important;
    border-right: 2px solid var(--border-gold) !important;
    backdrop-filter: blur(10px);
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
    letter-spacing: 8px;
    text-align: center;
    pointer-events: none;
}

div[data-testid="stButton"] > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 25px rgba(255,170,96,0.5), inset 0 0 20px rgba(0,0,0,0.8) !important;
    color: #FFF !important;
    border-color: var(--highlight-gold) !important;
}

[data-testid="stChatInput"] textarea {
    background-color: rgba(25,20,15,0.95) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border-gold) !important;
    border-radius: 0 !important;
    font-family: 'IM Fell English SC', serif !important;
    font-size: 16px !important;
    padding: 15px !important;
    min-height: 80px !important;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
}

[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    border-color: var(--highlight-gold) !important;
    box-shadow: 0 0 20px rgba(255,215,0,0.3) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Creepster', cursive !important;
    color: var(--highlight-gold) !important;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3) !important;
}

h1 { letter-spacing: 4px !important; }

p, span, label {
    font-family: 'IM Fell English SC', serif !important;
    color: var(--text-primary) !important;
}

.subtitle {
    font-family: 'Griffy', cursive !important;
}

::-webkit-scrollbar { width: 8px !important; }
::-webkit-scrollbar-track { background: rgba(10,6,3,0.8) !important; }
::-webkit-scrollbar-thumb { background: rgba(166,124,59,0.5) !important; border-radius: 4px !important; }

[aria-label*="info"] {
    background: rgba(30,20,10,0.8) !important;
    border: 2px solid var(--border-gold) !important;
    color: var(--text-primary) !important;
    border-radius: 0 !important;
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
</style>
'''

st.markdown(THEME_HTML, unsafe_allow_html=True)

# ========================
# 🔧 Session State 初始化
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []

if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ========================
# 📄 Banner (HTML 直接嵌入)
# ========================
st.markdown('''
<div style="text-align:center;margin:20px auto;max-width:950px;padding:40px;">
    <h1 style="font-family:'Creepster';font-size:3.5rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.4rem;letter-spacing:3px;margin-top:5px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:20px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.7;font-size:1.1rem;max-width:800px;margin:0 auto 30px;">
    当理智的 san 值归零，现实的法则在此崩塌。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <div style="display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-top:20px;">
        <div style="flex:1;min-width:320px;background:rgba(30,20,10,0.75);border:2px solid #aa7733;padding:20px;">
            <h3 style="font-family:'Creepster';color:#ffaa60;font-size:1.6rem;">🔥 快速生成 / RAPID</h3>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.6;margin-top:10px;">适用于意志坚定的造物主。<br>当你已明确 Mod 的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。</p>
            <span style="color:#888;font-size:0.8em;display:block;margin-top:10px;font-style:italic;">For when your vision is clear. Forge it now.</span>
        </div>
        
        <div style="flex:1;min-width:320px;background:rgba(20,30,20,0.75);border:2px solid #668844;padding:20px;">
            <h3 style="font-family:'Creepster';color:#aadd88;font-size:1.6rem;">👁️ 探索设计 / EXPLORE</h3>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.6;margin-top:10px;">适用于在迷雾中低语的探索者。<br>当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。</p>
            <span style="color:#888;font-size:0.8em;display:block;margin-top:10px;font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

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
    st.markdown(f'<div style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.3);border:2px dashed {color};animation: pulse 1.5s infinite;"><h3 style="font-family:Creepster;color:{color};">{icon} {text}</h3></div>', unsafe_allow_html=True)

# ========================
# 💬 聊天输入处理
# ========================
if st.session_state.mode == "explore":
    st.info("💬 **与暗影对话以明确设计思路**<br>Talk to the Shadow to refine your ideas", unsafe_allow_html=True)
    
    user_input = st.chat_input("描述你的想法 / Describe your ideas...")
    
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想 / Enter your concept...")
    
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

# ========================
# ⏳ 加载动画 + AI 生成
# ========================
if st.session_state.is_generating:
    st.markdown('''
    <div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 style="font-family:Creepster;color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);animation: flicker 1.5s infinite alternate;">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:Griffy;color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation: rotate 3s linear infinite;">✦</div>
    </div>
    ''', unsafe_allow_html=True)
    
    time.sleep(2.5)
    
    try:
        if st.session_state.mode == "explore":
            result = explore_with_llm(st.session_state.messages)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        reply_text = result.get('text', '暗影已回应...')
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply_text
        })
        
        mod_data = result.get('data', {})
        if mod_data and st.session_state.mode == "rapid":
            new_mod = {
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.generated_mods.append(new_mod)
    
    except Exception as e:
        print(f"❌ 生成错误：{e}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ 暗影沉默了... {str(e)}"
        })
    
    st.session_state.is_generating = False
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
            
            st.markdown(f'''
            <div style="
                background: rgba(25,20,15,0.9);
                border-left: 4px solid {color};
                border: 1px solid rgba(166,124,59,0.3);
                padding: 15px;
                margin: 15px 0;
                border-radius: 0;
                color: #F5E6C8;
                font-family: 'IM Fell English SC', serif;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
            ">
                <b style="font-family:'Creepster';color:{color};font-size:1.2rem;">{name}</b><br>
                <span style="font-family:'IM Fell English SC';font-size:1.1rem;line-height:1.7;">{content}</span>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:rgba(25,20,15,0.9);padding:15px;margin:15px 0;border:1px solid rgba(166,124,59,0.3);color:#F5E6C8;'>{msg}</div>", unsafe_allow_html=True)

# ========================
# ✨ 探索模式最终生成按钮
# ========================
if st.session_state.mode == "explore" and len(st.session_state.messages) >= 4:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
            summary = "\\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
            st.session_state.final_prompt = summary
            st.session_state.mode = "generating"
            st.session_state.is_generating = True
            st.rerun()

# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("""
    <div style="background:rgba(30,20,10,0.95);border:2px solid #A67C3B;border-radius:6px;padding:15px;margin-bottom:20px;text-align:center;">
        <h3 style="font-family:'Creepster';color:#FFD700;margin-top:0;">📦 Mod 库</h3>
        <p style="font-family:'IM Fell English SC';color:#AA8855;font-size:0.85rem;margin-bottom:0;">Your Mod Archive</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.generated_mods:
        st.markdown('<div style="background:rgba(0,0,0,0.3);border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
        for mod in st.session_state.generated_mods:
            st.markdown(f'''
            <div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;padding:12px;margin-bottom:10px;box-shadow:inset 0 0 10px rgba(0,0,0,0.5);">
                <strong style="font-family:'Creepster';color:#FFD700;">{mod['name']}</strong><br>
                <small style="color:#888;">{mod['date']}</small>
            </div>
            ''', unsafe_allow_html=True)
    
    st.divider()
    st.write(f"💬 对话记录：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        st.markdown("---")
        mod = st.session_state.generated_mods[-1]
        st.markdown(f'''
        <div style="background:rgba(30,20,10,0.8);border:2px solid #FFD700;padding:15px;box-shadow:0 0 20px rgba(255,215,0,0.2);">
            <h4 style="font-family:'Creepster';color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4>
            <p style="color:#aaa;font-size:0.9rem;margin-bottom:15px;">{mod.get('desc', '无描述')}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 立即下载", key=f"download_{mod['id']}", use_container_width=True):
                st.success(f"✅ {mod['name']} 已开始下载!")
        with col2:
            if st.button("🔄 重新生成", key=f"regen_{mod['id']}", use_container_width=True):
                st.info("正在重新生成该 Mod...")
    
    st.divider()
    if st.button("🗑️ 清除全部记录", key="clear_all"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
