import streamlit as st
import os
import base64
import io
import zipfile
import requests
from datetime import datetime

# 导入 LLM 模块
try:
    from qwen_client import explore_with_llm, design_with_llm, optimize_visual_prompt
except ImportError as e:
    st.error(f"❌ 无法导入模块：{e}")
    st.stop()

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
if "final_design" not in st.session_state:
    st.session_state.final_design = ""

# ========================
# 📸 图片资源路径
# ========================
GITHUB_REPO_NAME = "LETITIA-TAOBAO/DON-T-STARVE-TOGETHER-MOD-generator"
ASSETS_PATH = f"https://raw.githubusercontent.com/{GITHUB_REPO_NAME}/main/assets/"

IMAGES = {
    "bg": f"{ASSETS_PATH}background.jpg.png",
    "btn_rapid": f"{ASSETS_PATH}btn_play.png",
    "btn_explore": f"{ASSETS_PATH}btn_explore.png",
    "chat_box": f"{ASSETS_PATH}txt_box_bg.png"
}

# ========================
# 🎨 CSS 样式（使用你的自定义图片）
# ========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

/* ========== 全局背景 ========== */
.stApp {
    background-image: url("https://raw.githubusercontent.com/LETITIA-TAOBAO/DON-T-STARVE-TOGETHER-MOD-generator/main/assets/background.jpg.png");
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-color: transparent !important;
    min-height: 100vh;
}

html, body, [class*="css"] {
    background-color: transparent !important;
    background: transparent !important;
}

/* ========== 暗色遮罩层 ========== */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: -1 !important;
    background: linear-gradient(rgba(20,15,10,0.6), rgba(15,10,5,0.8));
    pointer-events: none;
}

h1, h2, h3 {
    font-family: 'Creepster', cursive !important;
    color: #FFD700 !important;
    text-shadow: 0 0 15px rgba(255,215,0,0.5);
}

p, span, div, label {
    font-family: 'IM Fell English SC', serif !important;
    color: #F5E6C8 !important;
}

/* ========== ⭐⭐⭐⭐⭐ 自定义按钮样式 ⭐⭐⭐⭐⭐ ========== */
.custom-mode-btn {
    width: 100% !important;
    height: 90px !important;
    background-size: cover !important;
    background-position: center !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0.95;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.custom-mode-btn:hover {
    transform: scale(1.08) translateY(-3px) !important;
    opacity: 1 !important;
    filter: brightness(1.15) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
}

.custom-mode-btn:active {
    transform: scale(0.98) !important;
}

/* ========== ⭐⭐⭐⭐⭐ 自定义对话框样式 ⭐⭐⭐⭐⭐ ========== */
.chat-box-custom {
    background: transparent !important;
    border: none !important;
    position: relative !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    color: #F5E6C8 !important;
}

.chat-box-custom::before {
    content: "";
    position: absolute;
    top: -10px; left: -10px; right: -10px; bottom: -10px;
    border-radius: 12px;
    z-index: -1;
}

[data-testid="stChatInput"] textarea {
    background-color: rgba(40,30,20,0.95) !important;
    border: 3px solid #8B4513 !important;
    color: #F5E6C8 !important;
    border-radius: 8px !important;
    font-family: 'IM Fell English SC', serif !important;
    font-size: 16px !important;
    padding: 20px !important;
    min-height: 100px !important;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
}

[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    border-color: #FFA726 !important;
}

/* ========== 侧边栏 ========== */
section[data-testid="stSidebar"] {
    background: rgba(25,15,8,0.98) !important;
    border-right: 4px solid #8B4513 !important;
}

section[data-testid="stSidebar"] * {
    color: #F5E6C8 !important;
}

/* ========== 滚动条 ========== */
::-webkit-scrollbar { width: 8px !important; }
::-webkit-scrollbar-thumb { background: #8B4513 !important; border-radius: 4px !important; }
::-webkit-scrollbar-track { background: rgba(10,5,3,0.8) !important; }

/* ========== Banner 框 ========== */
.banner-box {
    background: rgba(30,20,10,0.75) !important;
    border: 3px solid #A67C3B !important;
    padding: 40px !important;
    border-radius: 12px !important;
    box-shadow: 0 0 40px rgba(0,0,0,0.8), inset 0 0 30px rgba(0,0,0,0.5) !important;
}

/* ========== 模式说明卡片 ========== */
.mode-card {
    flex: 1;
    min-width: 280px;
    max-width: 450px;
    padding: 25px !important;
    border-radius: 8px !important;
    position: relative !important;
    transition: all 0.3s ease !important;
}

.mode-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
}

.card-rapid {
    background: rgba(30,20,10,0.75) !important;
    border: 2px solid #aa7733 !important;
}

.card-explore {
    background: rgba(20,30,20,0.75) !important;
    border: 2px solid #668844 !important;
}

.card-icon {
    position: absolute;
    top: -15px; right: -15px;
    font-size: 30px !important;
    transform: rotate(45deg);
}

.card-title {
    font-family: Creepster, cursive !important;
    text-align: center !important;
    margin: 0 0 15px 0 !important;
}

.card-text {
    font-family: "IM Fell English SC", serif !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
    text-align: center !important;
    color: #d4c4a0 !important;
}

.card-english {
    color: #888 !important;
    font-size: 0.8em !important;
    font-style: italic !important;
    display: block !important;
    margin-top: 12px !important;
}

.cards-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 30px !important;
}
</style>
""", unsafe_allow_html=True)

# ========================
# Banner
# ========================
st.markdown(f'''
<div class="banner-box" style='text-align:center;margin:30px auto;max-width:900px;'>
<h1 style='font-size:3.5rem;margin:0;text-shadow:0 0 25px rgba(255,215,0,0.6);'>饥荒 MOD 生成器</h1>
<p style='font-family:Griffy;color:#aa8855;font-size:1.4rem;letter-spacing:3px;margin-top:10px;'>DON'T STARVE TOGETHER MOD GENERATOR</p>
<hr style='width:50%;border:none;border-top:2px solid #8B4513;margin:20px auto;'>
<p style='line-height:1.8;font-size:1.1rem;max-width:800px;margin:0 auto;'>
当理智归零，现实崩塌。<br>
<span style='color:#FFA726;text-shadow:0 0 10px rgba(255,167,38,0.5);'>You are no longer a survivor, but a Creator.</span>
</p>
</div>
''', unsafe_allow_html=True)

# ========================
# ⭐⭐⭐⭐⭐ 自定义图片按钮 ⭐⭐⭐⭐⭐
# ========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown(f'''
    <style>
    #rapid_btn {{
        background-image: url('{IMAGES["btn_rapid"]}') !important;
        background-repeat: no-repeat !important;
    }}
    </style>
    ''', unsafe_allow_html=True)
    
    if st.button("", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.rerun()

with col2:
    st.markdown(f'''
    <style>
    #explore_btn {{
        background-image: url('{IMAGES["btn_explore"]}') !important;
        background-repeat: no-repeat !important;
    }}
    </style>
    ''', unsafe_allow_html=True)
    
    if st.button("", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# 按钮下方的模式说明卡片
st.markdown('<div class="cards-container">', unsafe_allow_html=True)

st.markdown(f'''
<div class="mode-card card-rapid">
    <div class="card-icon">✷</div>
    <h3 class="card-title" style="color: #ffaa60;">🔥 意志铸剑者</h3>
    <p class="card-text">当你已明晰 Mod 的核心法则与物品灵魂<br>无需徘徊于暗影之间<br>将你的疯狂构想直接锻造成可触及的现实<br><br><span class="card-english">For when your vision is clear. Forge it now.</span></p>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
    <div class="mode-card card-explore">
        <div class="card-icon">✷</div>
        <h3 class="card-title" style="color: #aadd88;">👁️ 迷雾探路者</h3>
        <p class="card-text">当灵感如迷雾般在你脑海中低语<br>混沌尚未凝聚成形<br>与暗影对话，在反复试探中让疯狂的蓝图逐渐清晰<br><br><span class="card-english">For when inspiration is foggy. Talk to the Shadow.</span></p>
    </div>
</div>
''', unsafe_allow_html=True)

# 模式确认
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
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()
    
    if len(st.session_state.messages) >= 2:
        last_msg = st.session_state.messages[-1]['content'].lower()
        if any(word in last_msg for word in ['yes', '是', '生成了', '生成', 'create']):
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
                    summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    st.session_state.final_design = summary
                    st.session_state.mode = "generating"
                    st.rerun()

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.final_design = user_input
        st.session_state.is_generating = True
        st.rerun()

# ========================
# ⏳ 生成阶段
# ========================
if st.session_state.is_generating:
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
            color = '#FF8C00' if role == 'user' else '#66BB6A'
            name = '求生者' if role == 'user' else '暗影设计助手'
            
            st.markdown(f"<div class='chat-box-custom' style='background:rgba(30,20,10,0.9);border-left:4px solid {color};padding:15px;margin:15px 0;color:#F5E6C8;'><b style='color:{color};font-family:Creepster;'>{name}</b><br>{content}</div>", unsafe_allow_html=True)

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
                    st.rerun()
    
    st.divider()
    st.write(f"对话：{len(st.session_state.messages)} 条")
    
    st.divider()
    if st.button("🗑️ 清除全部记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
