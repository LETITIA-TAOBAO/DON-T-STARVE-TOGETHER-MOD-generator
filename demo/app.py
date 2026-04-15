import streamlit as st
import os
import base64
import io
import zipfile
import requests
from datetime import datetime

# ========================
# ⚠️ LLM 导入
# ========================
try:
    from qwen_client import explore_with_llm, design_with_llm, optimize_visual_prompt
except ImportError as e:
    st.error(f"❌ 模块加载失败：{e}")
    st.stop()

# ========================
# 🔧 Session State (关键！修复流程问题)
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []
if "final_design" not in st.session_state:
    st.session_state.final_design = ""
# ⭐⭐⭐⭐⭐ 新增：确认标志 ⭐⭐⭐⭐⭐
if "confirmed_generate" not in st.session_state:
    st.session_state.confirmed_generate = False

# ========================
# 📸 图片资源路径（GitHub Raw）
# ========================
GITHUB_USER = "LETITIA-TAOBAO"
GITHUB_REPO = "DON-T-STARVE-TOGETHER-MOD-generator"
ASSETS_PATH = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/assets/"

IMAGES = {
    "bg": f"{ASSETS_PATH}background.jpg.png",
    "btn_rapid": f"{ASSETS_PATH}btn_play.png",
    "btn_explore": f"{ASSETS_PATH}btn_explore.png",
    "chat_box": f"{ASSETS_PATH}txt_box_bg.png"
}

# ========================
# 🎨 CSS 样式（重点：应用你的图片）
# ========================
STYLES = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

/* ========== 全局背景 ========== */
.stApp {{
    background-image: url("{IMAGES['bg']}");
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    min-height: 100vh;
}}

html, body, [class*="css"] {{
    background-color: transparent !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -1;
    background: linear-gradient(rgba(20,15,10,0.6), rgba(15,10,5,0.8));
}}

h1, h2, h3 {{ font-family: 'Creepster' !important; color: #FFD700 !important; }}
p, span, div, label {{ font-family: 'IM Fell English SC' !important; color: #F5E6C8 !important; }}

/* ========== ⭐⭐⭐⭐⭐ 自定义按钮 ⭐⭐⭐⭐⭐ ========== */
.btn-mode-wrapper {{
    width: 100%;
    max-width: 450px;
    margin: 20px auto;
}}

.btn-custom {{
    width: 100% !important;
    height: 90px !important;
    border: none !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    opacity: 0.9;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}}

.btn-custom:hover {{
    transform: scale(1.05) translateY(-3px) !important;
    opacity: 1 !important;
    filter: brightness(1.15);
    box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
}}

.btn-custom:active {{ transform: scale(0.98) !important; }}

/* ========== ⭐⭐⭐⭐⭐ 对话框背景 ⭐⭐⭐⭐⭐ ========== */
[data-testid="stChatInput"] textarea {{
    background-image: url("{IMAGES['chat_box']}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-color: rgba(40,30,20,0.85) !important;
    border: none !important;
    color: #F5E6C8 !important;
    font-family: 'IM Fell English SC' !important;
    padding: 20px !important;
    min-height: 120px !important;
}}

[data-testid="stChatInput"] textarea:focus {{
    outline: none !important;
    border-color: #FFA726 !important;
}}

/* ========== 侧边栏 ========== */
section[data-testid="stSidebar"] {{
    background: rgba(25,15,8,0.98) !important;
    border-right: 4px solid #8B4513 !important;
}}
section[data-testid="stSidebar"] * {{ color: #F5E6C8 !important; }}

/* ========== Banner ========== */
.banner-box {{
    background: rgba(30,20,10,0.75) !important;
    border: 3px solid #A67C3B !important;
    padding: 40px !important;
    border-radius: 12px !important;
    text-align: center !important;
    margin: 30px auto !important;
    max-width: 900px !important;
    box-shadow: 0 0 40px rgba(0,0,0,0.8) !important;
}}

/* ========== ⭐⭐⭐⭐⭐ 说明卡片横排 ⭐⭐⭐⭐⭐ ========== */
.cards-container {{
    display: flex !important;
    gap: 30px !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    margin: 40px auto !important;
    max-width: 950px !important;
}}

.card-row {{
    display: flex !important;
    gap: 30px !important;
    justify-content: center !important;
}}

.mode-card {{
    flex: 1 !important;
    min-width: 320px !important;
    max-width: 480px !important;
    padding: 25px !important;
    border-radius: 8px !important;
    position: relative !important;
    transition: all 0.3s ease !important;
}}

.mode-card:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
}}

.card-rapid {{
    background: rgba(30,20,10,0.75) !important;
    border: 2px solid #aa7733 !important;
}}

.card-explore {{
    background: rgba(20,30,20,0.75) !important;
    border: 2px solid #668844 !important;
}}

.card-icon {{
    position: absolute;
    top: -15px; right: -15px;
    font-size: 30px !important;
    transform: rotate(45deg);
}}

.card-title {{
    font-family: Creepster !important;
    text-align: center !important;
    margin: 0 0 15px 0 !important;
    font-size: 1.5rem !important;
}}

.card-text {{
    font-family: "IM Fell English SC" !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
    text-align: center !important;
    color: #d4c4a0 !important;
}}

.card-english {{
    color: #888 !important;
    font-size: 0.8em !important;
    font-style: italic !important;
    display: block !important;
    margin-top: 12px !important;
}}

/* ========== 聊天消息框 ========== */
.chat-message {{
    background: rgba(30,20,10,0.9) !important;
    border-left: 4px solid #FF8C00 !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    border-radius: 0 8px 8px 0 !important;
}}

.chat-message-assistant {{
    background: rgba(20,30,20,0.9) !important;
    border-left: 4px solid #66BB6A !important;
}}

/* ========== 滚动条 ========== */
::-webkit-scrollbar {{ width: 8px !important; }}
::-webkit-scrollbar-thumb {{ background: #8B4513 !important; border-radius: 4px !important; }}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ========================
# Banner
# ========================
st.markdown('''
<div class="banner-box">
<h1 style="font-size:3.5rem;margin:0;text-shadow:0 0 25px rgba(255,215,0,0.6);">饥荒 MOD 生成器</h1>
<p style="font-family:Griffy;color:#aa8855;font-size:1.4rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
<hr style="width:50%;border:none;border-top:2px solid #8B4513;margin:20px auto;">
<p style="line-height:1.8;font-size:1.1rem;max-width:800px;margin:0 auto;">
当理智归零，现实崩塌。<br>
<span style="color:#FFA726;text-shadow:0 0 10px rgba(255,167,38,0.5);">You are no longer a survivor, but a Creator.</span>
</p>
</div>
''', unsafe_allow_html=True)

# ========================
# ⭐⭐⭐⭐⭐ 自定义按钮 ⭐⭐⭐⭐⭐
# ========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('''<div class="btn-mode-wrapper">''', unsafe_allow_html=True)
    
    if st.button("", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.session_state.final_design = ""
        st.session_state.confirmed_generate = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('''<div class="btn-mode-wrapper">''', unsafe_allow_html=True)
    
    if st.button("", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.session_state.final_design = ""
        st.session_state.confirmed_generate = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ⭐⭐⭐⭐⭐ 说明卡片横排 ⭐⭐⭐⭐⭐
st.markdown('<div class="cards-container">', unsafe_allow_html=True)

st.markdown('''
<div class="mode-card card-rapid">
    <div class="card-icon">✷</div>
    <h3 class="card-title" style="color: #ffaa60;">🔥 意志铸剑者</h3>
    <p class="card-text">当你已明晰 Mod 的核心法则与物品灵魂<br>无需徘徊于暗影之间<br>将你的疯狂构想直接锻造成可触及的现实<br><br><span class="card-english">For when your vision is clear. Forge it now.</span></p>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="mode-card card-explore">
    <div class="card-icon">✷</div>
    <h3 class="card-title" style="color: #aadd88;">👁️ 迷雾探路者</h3>
    <p class="card-text">当灵感如迷雾般在你脑海中低语<br>混沌尚未凝聚成形<br>与暗影对话，在反复试探中让疯狂的蓝图逐渐清晰<br><br><span class="card-english">For when inspiration is foggy. Talk to the Shadow.</span></p>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ========================
# 模式确认提示
# ========================
if st.session_state.mode != "home":
    mode_map = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**")
    }
    icon, color, text = mode_map.get(st.session_state.mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f"<div style='text-align:center;padding:15px;margin:20px 0;border:2px dashed {color};'><h3 style='color:{color};font-family:Creepster;'>{icon} {text}</h3></div>", unsafe_allow_html=True)

# ========================
# 💬 聊天处理（修复流程：先对话，再生成）
# ========================
def generate_atlas_xml():
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
    <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''

def generate_icon_with_pollinations(prompt):
    try:
        if not prompt or len(prompt) < 5:
            return {"success": False, "error": "无效的 Prompt"}
        
        encoded = prompt.replace(" ", "+").replace("&", "%26")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={int(datetime.now().timestamp())}"
        
        response = requests.get(url, timeout=45)
        
        if response.status_code == 200 and len(response.content) > 1000:
            return {
                "success": True,
                "base64": base64.b64encode(response.content).decode('utf-8'),
                "url": url
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_mod_zip(mod_data):
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        files = mod_data.get('all_files', {})
        
        for filename, content in files.items():
            if isinstance(content, str):
                zip_file.writestr(filename, content.encode('utf-8'))
            elif isinstance(content, bytes):
                zip_file.writestr(filename, content)
        
        for directory in ["sounds/", "images/", "animations/"]:
            zip_file.writestr(directory, "")
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if st.session_state.mode == "explore":
    st.write("💬 **与暗影设计助手对话以明确设计思路**")
    
    user_input = st.chat_input("描述你的想法...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()
    
    # ⭐⭐⭐⭐⭐ 检查是否有足够对话才显示生成按钮 ⭐⭐⭐⭐⭐
    if len(st.session_state.messages) >= 2:
        st.markdown("---")
        st.markdown("<div style='text-align:center;margin:30px 0;'>", unsafe_allow_html=True)
        
        col1_check, col2_check = st.columns([3, 1])
        with col2_check:
            if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
                summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                st.session_state.final_design = summary
                st.session_state.mode = "generating"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.final_design = user_input
        st.session_state.mode = "generating"
        st.rerun()

# ========================
# ⏳ 生成阶段（仅在点击生成按钮后）
# ========================
if st.session_state.mode == "generating":
    st.markdown("<div style='text-align:center;padding:40px;'><h2 style='font-family:Creepster;font-size:2.5rem;color:#FFD700;'>世界正在扭曲......</h2><p style='margin-top:20px;'>The shadows are weaving your madness...</p></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    
    with st.spinner("📝 Qwen 正在生成 Mod 代码..."):
        progress_bar.progress(20)
        result = design_with_llm(st.session_state.final_design, st.session_state.messages)
    
    with st.spinner("🎨 正在优化图标提示词..."):
        progress_bar.progress(50)
        visual_result = optimize_visual_prompt(st.session_state.final_design)
        image_prompt = visual_result.get('optimized_prompt', visual_result.get('fallback_prompt', ''))
    
    with st.spinner("🖼️ Pollinations.ai 正在绘制图标..."):
        progress_bar.progress(75)
        icon_result = generate_icon_with_pollinations(image_prompt)
        
        if icon_result["success"]:
            st.success("✅ 图标生成成功!")
            st.image(icon_result.get('url', ''), caption="生成的图标预览", width=200)
            
            if "files" not in result['data']:
                result['data']['files'] = {}
            result['data']['files']['modicon.tex'] = base64.b64decode(icon_result['base64'])
            result['data']['files']['modicon.xml'] = generate_atlas_xml()
        else:
            st.warning(f"⚠️ 图标生成失败：{icon_result['error']}")
    
    progress_bar.progress(100)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get('text', '已完成')
    })
    
    mod_data = result.get('data', {})
    if mod_data:
        st.session_state.generated_mods.append({
            "id": len(st.session_state.generated_mods) + 1,
            "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc": mod_data.get('desc', ''),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "design": st.session_state.final_design,
            "all_files": mod_data.get('files', {}),
            "icon_generated": icon_result["success"]
        })
    
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
            css_class = 'chat-message' if role == 'user' else 'chat-message chat-message-assistant'
            color = '#FF8C00' if role == 'user' else '#66BB6A'
            name = '求生者' if role == 'user' else '暗影设计助手'
            
            st.markdown(f"<div class='{css_class}'><b style='color:{color};font-family:Creepster;'>{name}</b><br>{content}</div>", unsafe_allow_html=True)

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
            
            col_dl, col_re = st.columns(2)
            with col_dl:
                zip_data = create_mod_zip(mod)
                st.download_button(
                    label="💾 下载",
                    data=zip_data,
                    file_name=f"{mod['name'].replace(' ', '_')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            with col_re:
                if st.button("🔄", key=f"regen_{mod['id']}", use_container_width=True):
                    st.session_state.mode = "explore"
                    st.session_state.final_design = mod.get('design', '')
                    st.session_state.messages = [{"role": "user", "content": mod.get('design', '')}]
                    st.session_state.generated_mods = [m for m in st.session_state.generated_mods if m['id'] != mod['id']]
                    st.rerun()
    
    st.divider()
    st.write(f"对话：{len(st.session_state.messages)} 条")
    
    st.divider()
    if st.button("🗑️ 清除全部记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
