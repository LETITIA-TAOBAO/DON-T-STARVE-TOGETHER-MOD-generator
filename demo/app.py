import streamlit as st
import os
import base64
from datetime import datetime
import time
import urllib.request
import io
import zipfile

# ========================
# ⚠️ LLM 安全导入 (关键！不能降级)
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
    print("[SUCCESS] LLM module loaded successfully!")
except Exception as e:
    st.error(f"❌ **LLM 模块加载失败**：{str(e)}")
    st.error("请确保 `qwen_client.py` 文件存在于当前目录")
    st.stop()


# ========================
# 🎨 CSS + JavaScript (保持背景透明度)
# ========================
def inject_theme_css_js(bg_url):
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {{
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
    }}
    
    /* ===== 全局强制透明 ===== */
    html, body {{
        background-color: transparent !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }}
    
    .stApp, [class*="css"], .st-emotion-cache, [data-testid="stApp"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    /* ===== 背景图层（提高不透明度）===== */
    body::before {{
        content: "" !important;
        position: fixed !important;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1000 !important;
        background: linear-gradient(rgba(10,6,3,0.4), rgba(5,3,1,0.6)), url('{bg_url}') center/cover no-repeat !important;
        filter: contrast(1.08) brightness(0.95) !important;
    }}
    
    /* ===== Chat Input 深度覆盖 ===== */
    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] form,
    div[data-testid="stChatInput"] form > div,
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] button,
    div.stSticky,
    div.stSticky > div,
    div.stSticky form,
    div.stSticky form > div,
    div.stSticky textarea,
    div.stSticky button {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    
    div[data-testid="stChatInput"] textarea {{
        background-color: rgba(25,20,15,0.98) !important;
        border: 2px solid var(--border-gold) !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        padding: 15px !important;
        min-height: 80px !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
    }}
    
    div[data-testid="stChatInput"] button {{
        background-color: rgba(25,20,15,0.98) !important;
        border: 2px solid var(--border-gold) !important;
        color: var(--highlight-gold) !important;
    }}
    
    /* ===== 块级元素透明 ===== */
    [data-testid="stAppViewContainer"],
    [data-testid="stBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stColumn"],
    [data-testid="stMainBlockContainer"],
    div.block-container,
    section.st-section {{
        background-color: transparent !important;
        background: transparent !important;
        padding: 0 !important;
    }}
    
    /* ===== 隐藏默认元素 ===== */
    header, footer, #MainMenu, [data-testid="stHeader"], [data-testid="stDecoration"], 
    [data-testid="stToolbar"], [data-testid="stSidebarClose"] {{
        display: none !important;
    }}
    
    /* ===== 侧边栏 ===== */
    section[data-testid="stSidebar"] {{
        background: rgba(25,15,8,0.98) !important;
        border-right: 3px solid var(--border-gold) !important;
    }}
    section[data-testid="stSidebar"] * {{ color: var(--text-primary) !important; }}
    
    /* ===== 按钮风格 ===== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
        background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
        border: 3px solid var(--thorn-brown) !important;
    }}
    
    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166,124,59,0.5) !important; }}
    </style>
    
    <!-- JavaScript 强制清理 -->
    <script>
    setTimeout(function() {{
        const containers = document.querySelectorAll(
            'div[data-testid*="stApp"],' +
            'div[data-testid*="Container"],' +
            'div.stSticky,' +
            '[class*="css"],' +
            '.block-container,' +
            '.st-emotion-cache'
        );
        
        containers.forEach(el => {{
            el.style.backgroundColor = 'transparent' + '!important';
            el.style.background = 'transparent' + '!important';
        }});
        
        const chatInput = document.querySelector('[data-testid="stChatInput"]');
        if (chatInput) {{
            chatInput.style.backgroundColor = 'transparent' + '!important';
            const forms = chatInput.querySelectorAll('form, div');
            forms.forEach(form => {{
                form.style.backgroundColor = 'transparent' + '!important';
                form.style.border = 'none' + '!important';
                form.style.boxShadow = 'none' + '!important';
            }});
        }}
        
        console.log('[DEBUG] JavaScript forced transparency applied');
    }}, 100);
    </script>
    """
    return css


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
        print(f"[ERROR] Background failed: {e}")
        return None


bg_base64 = get_background_base64()
bg_url = f'data:image/png;base64,{bg_base64}' if bg_base64 else ''


# ========================
# 🎨 注入 CSS + JS
# ========================
print("[INIT] Injecting theme CSS + JavaScript...")
st.markdown(inject_theme_css_js(bg_url), unsafe_allow_html=True)


# ========================
# Banner
# ========================
st.markdown("""
<div style='text-align:center;margin:30px auto;max-width:900px;padding:40px;background:rgba(30,20,10,0.7);border:2px solid #A67C3B;border-radius:10px;'>
<h1 style='font-family:Creepster;font-size:3.5rem;color:#ffaa60;text-shadow:0 0 25px rgba(255,170,96,0.8);margin:0;'>饥荒 MOD 生成器</h1>
<p style='font-family:Griffy;color:#aa8855;font-size:1.4rem;letter-spacing:3px;margin-top:10px;'>DON'T STARVE TOGETHER MOD GENERATOR</p>
<hr style='width:50%;border:none;border-top:2px solid #5a3a1a;margin:20px auto;'>
<p style='font-family:IM Fell English SC;color:#d4c4a0;line-height:1.8;font-size:1.1rem;max-width:800px;margin:0 auto;'>当理智归零，现实崩塌。<span style='color:#88aa66;'>You are no longer a survivor, but a Creator.</span></p>
</div>
""", unsafe_allow_html=True)


# ========================
# 模式选择按钮
# ========================
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔥 快速生成 / RAPID", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("👁️ 探索设计 / EXPLORE", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()


# ========================
# 按钮下方说明卡片
# ========================
st.markdown("""
<div style='display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-top:20px;'>
    <div style='flex:1;min-width:280px;background:rgba(30,20,10,0.75);border:2px solid #aa7733;padding:25px;border-radius:8px;position:relative;'>
        <div style='position:absolute;top:-15px;right:-15px;font-size:30px;color:#aa7733;transform:rotate(45deg);'>✷</div>
        <h3 style='font-family:Creepster;color:#ffaa60;font-size:1.5rem;text-align:center;margin:0 0 10px;'>🔥 意志铸剑者</h3>
        <p style='font-family:IM Fell English SC;color:#d4c4a0;font-size:0.95rem;line-height:1.7;text-align:center;'>
        当你已明晰 Mod 的核心法则与物品灵魂，<br>
        无需徘徊于暗影之间，<br>
        将你的疯狂构想直接锻造成可触及的现实。<br><br>
        <span style='color:#888;font-size:0.8em;font-style:italic;'>For when your vision is clear. Forge it now.</span>
        </p>
    </div>
    
    <div style='flex:1;min-width:280px;background:rgba(20,30,20,0.75);border:2px solid #668844;padding:25px;border-radius:8px;position:relative;'>
        <div style='position:absolute;top:-15px;right:-15px;font-size:30px;color:#668844;transform:rotate(45deg);'>✷</div>
        <h3 style='font-family:Creepster;color:#aadd88;font-size:1.5rem;text-align:center;margin:0 0 10px;'>👁️ 迷雾探路者</h3>
        <p style='font-family:IM Fell English SC;color:#d4c4a0;font-size:0.95rem;line-height:1.7;text-align:center;'>
        当灵感如迷雾般在你脑海中低语，<br>
        混沌尚未凝聚成形，<br>
        与暗影对话，在反复试探中让疯狂的蓝图逐渐清晰。<br><br>
        <span style='color:#888;font-size:0.8em;font-style:italic;'>For when inspiration is foggy. Talk to the Shadow.</span>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# ========================
# 模式确认
# ========================
if st.session_state.mode != "home":
    mode_map = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**")
    }
    icon, color, text = mode_map.get(st.session_state.mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f"<div style='text-align:center;padding:15px;margin:20px 0;border:2px dashed {color};'><h3 style='color:{color};font-family:Creepster;'>{icon} {text}</h3></div>", unsafe_allow_html=True)


# ========================
# 💬 聊天处理
# ========================
if st.session_state.mode == "explore":
    st.write("💬 **与暗影对话以明确设计思路**")
    
    user_input = st.chat_input("描述你的想法...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()
    
    if len(st.session_state.messages) >= 2:
        st.markdown("---")
        if st.button("✨ 生成最终 Mod", key="gen_from_explore"):
            summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            st.session_state.final_prompt = summary
            st.session_state.mode = "generating"
            st.session_state.is_generating = True
            st.rerun()

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()


# ========================
# ⏳ 生成阶段 (完整 LLM 调用)
# ========================
if st.session_state.is_generating:
    st.markdown("<div style='text-align:center;padding:40px;'><h2 style='font-family:Creepster;color:#FFD700;font-size:2.5rem;'>世界正在扭曲......</h2><p style='font-family:Griffy;color:#aa8855;margin-top:20px;'>The shadows are weaving your madness...</p></div>", unsafe_allow_html=True)
    
    time.sleep(2.5)
    
    try:
        # ⭐⭐⭐⭐⭐ 完整 LLM 调用 (无降级) ⭐⭐⭐⭐⭐
        if st.session_state.mode == "explore":
            result = explore_with_llm(st.session_state.messages)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        # 添加到聊天记录
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get('text', '已完成')
        })
        
        # 保存 Mod 数据
        mod_data = result.get('data', {})
        if mod_data:
            st.session_state.generated_mods.append({
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "lua_code": mod_data.get('lua_code', ''),
                "modinfo": mod_data.get('modinfo', '')
            })
    
    except Exception as e:
        # LLM 调用出错时记录错误信息
        print(f"[ERROR] LLM call failed: {str(e)}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ **生成失败**：\n\n{str(e)}\n\n请检查你的 API Key 和网络连接。"
        })
    
    st.session_state.is_generating = False
    st.session_state.mode = "generated"
    st.rerun()


# ========================
# 💬 显示聊天记录
# ========================
if st.session_state.messages:
    for msg in st.session_state.messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '求生者' if role == 'user' else '暗影'
            
            st.markdown(f"<div style='background:rgba(25,20,15,0.9);border-left:4px solid {color};padding:15px;margin:15px 0;color:#F5E6C8;font-family:IM Fell English SC;'><b style='color:{color};'>{name}</b><br>{content}</div>", unsafe_allow_html=True)


# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    
    if not st.session_state.generated_mods:
        st.write("暂无 Mod 创作")
    else:
        for mod in st.session_state.generated_mods:
            st.write(f"**{mod['name']}** ({mod['date']})")
    
    st.divider()
    st.write(f"对话：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        mod = st.session_state.generated_mods[-1]
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("modinfo.lua", mod.get("modinfo", ""))
            zip_file.writestr("main.lua", mod.get("lua_code", ""))
        
        st.download_button(
            label=f"💾 下载 {mod['name']}.zip",
            data=zip_buffer.getvalue(),
            file_name=f"{mod['name']}.zip",
            mime="application/zip",
            use_container_width=True
        )
        
        if st.button("🔄 重新生成", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    if st.button("🗑️ 清除记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
