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
# 🔧 Session State 初始化
# ========================
defaults = {
    "mode": "home",
    "messages": [],
    "generated_mods": [],
    "final_design": "",
    "generating": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ========================
# 📸 图片资源路径
# ========================
GITHUB_USER = "LETITIA-TAOBAO"
GITHUB_REPO = "DON-T-STARVE-TOGETHER-MOD-generator"
ASSETS_PATH = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/demo/assets/"

IMAGES = {
    "bg":           f"{ASSETS_PATH}background.jpg.png",
    "btn_rapid":    f"{ASSETS_PATH}btn_play.png",
    "btn_explore":  f"{ASSETS_PATH}btn_explore.png",
    "btn_generate": f"{ASSETS_PATH}mod_generate.png",
    "card_bg":      f"{ASSETS_PATH}txt_box_bg.png",
}

# ========================
# 🎨 全局 CSS (深度定制)
# ========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

/* ── 全局背景 ── */
.stApp {{
    background-image: url("{IMAGES['bg']}");
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}
html, body, [class*="css"] {{ background-color: transparent !important; }}
.stApp::before {{
    content: "";
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    background: linear-gradient(rgba(20,15,10,0.6), rgba(15,10,5,0.8));
}}

/* ── 字体 ── */
h1,h2,h3 {{ font-family:'Creepster' !important; color:#FFD700 !important; }}
p,span,div,label {{ font-family:'IM Fell English SC' !important; color:#F5E6C8 !important; }}

/* ── Banner ── */
.banner-box {{
    background: rgba(30,20,10,0.8);
    border: 3px solid #A67C3B;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    margin: 20px auto;
    max-width: 800px;
    box-shadow: 0 0 30px rgba(0,0,0,0.8);
}}

/* ══════════════════════════════════════
   ⭐ 核心修复：将按钮直接变成图片
   ══════════════════════════════════════ */
/* 移除所有 Streamlit 按钮的默认丑陋样式 */
div.stButton > button {{
    border: none !important;
    background-image: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
    color: transparent !important; /* 隐藏按钮文字 */
    transition: transform 0.2s ease !important;
    cursor: pointer !important;
}}
div.stButton > button:hover {{
    transform: scale(1.05) !important;
    border: none !important;
    background-color: transparent !important;
    color: transparent !important;
}}
div.stButton > button:active {{
    transform: scale(0.95) !important;
    background-color: transparent !important;
}}

/* 分别为 快速 和 探索 按钮设置背景图 */
div[data-testid="stButton"] button[key="rapid_btn"] {{
    background-image: url("{IMAGES['btn_rapid']}") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 400px !important;
    height: 120px !important;
}}

div[data-testid="stButton"] button[key="explore_btn"] {{
    background-image: url("{IMAGES['btn_explore']}") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 400px !important;
    height: 120px !important;
}}

div[data-testid="stButton"] button[key="gen_btn"] {{
    background-image: url("{IMAGES['btn_generate']}") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 450px !important;
    height: 130px !important;
}}

/* ── 说明卡片 (修复背景显示) ── */
.cards-row {{
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 20px auto 50px auto;
    max-width: 1100px;
}}
.card-item {{
    flex: 1;
    max-width: 480px;
    min-height: 220px;
    background-image: url("{IMAGES['card_bg']}");
    background-size: 100% 100% !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    padding: 50px 40px 40px 40px;
    text-align: center;
    box-sizing: border-box;
}}
.card-title {{
    font-family: Creepster !important;
    font-size: 1.6rem !important;
    margin-bottom: 10px !important;
}}
.card-text {{
    font-size: 1rem !important;
    line-height: 1.6 !important;
    color: #d4c4a0 !important;
}}
.card-en {{
    display: block;
    font-style: italic;
    font-size: 0.85rem;
    color: #998877;
    margin-top: 10px;
}}

/* ── 聊天和进度 ── */
.chat-msg {{
    background: rgba(30,20,10,0.9);
    border-left: 4px solid #FF8C00;
    padding: 15px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}}
.chat-msg.assistant {{
    background: rgba(20,30,20,0.9);
    border-left-color: #66BB6A;
}}
.gen-progress-box {{
    background: rgba(30,20,10,0.9);
    border: 2px solid #8B4513;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    margin: 20px auto;
    max-width: 600px;
}}

/* 侧边栏样式 */
section[data-testid="stSidebar"] {{
    background: rgba(20,10,5,0.98) !important;
    border-right: 3px solid #8B4513 !important;
}}
</style>
""", unsafe_allow_html=True)

# ========================
# 🏴 Banner
# ========================
st.markdown("""
<div class="banner-box">
  <h1 style="font-size:3rem;margin:0;">饥荒 MOD 生成器</h1>
  <p style="font-family:Griffy;color:#aa8855;font-size:1.2rem;letter-spacing:2px;margin-top:5px;">
    DON'T STARVE TOGETHER MOD GENERATOR
  </p>
  <hr style="width:40%;border:none;border-top:2px solid #8B4513;margin:15px auto;">
  <p style="font-size:1rem;line-height:1.6;">
    当理智归零，现实崩塌。<br>
    <span style="color:#FFA726;">You are no longer a survivor, but a Creator.</span>
  </p>
</div>
""", unsafe_allow_html=True)

# ========================
# 🏠 主页界面
# ========================
if st.session_state.mode == "home":
    # 按钮行
    col1, col2 = st.columns(2)
    with col1:
        if st.button("快速生成", key="rapid_btn"):
            st.session_state.mode = "rapid"
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("探索设计", key="explore_btn"):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.rerun()

    # 说明卡片行
    st.markdown(f"""
    <div class="cards-row">
      <div class="card-item">
        <div class="card-title" style="color:#ffaa60;">🔥 意志铸剑者</div>
        <div class="card-text">
          当你已明晰 Mod 的核心法则与物品灵魂<br>
          无需徘徊于暗影之间<br>
          将你的疯狂构想直接锻造成可触及的现实
          <span class="card-en">For when your vision is clear. Forge it now.</span>
        </div>
      </div>
      <div class="card-item">
        <div class="card-title" style="color:#aadd88;">👁️ 迷雾探路者</div>
        <div class="card-text">
          当灵感如迷雾般在你脑海中低语<br>
          混沌尚未凝聚成形<br>
          与暗影对话，在反复试探中让疯狂的蓝图逐渐清晰
          <span class="card-en">For when inspiration is foggy. Talk to the Shadow.</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ========================
# 🛠️ 工具函数
# ========================
def generate_atlas_xml():
    return '<?xml version="1.0" encoding="utf-8"?><TextureAtlas imagePath="modicon.tex"><SubTexture name="default" x="0" y="0" width="512" height="512"/></TextureAtlas>'

def generate_icon_with_pollinations(prompt):
    try:
        encoded = prompt.replace(" ", "+").replace("&", "%26")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={int(datetime.now().timestamp())}"
        resp = requests.get(url, timeout=45)
        if resp.status_code == 200:
            return {"success": True, "base64": base64.b64encode(resp.content).decode(), "url": url}
        return {"success": False, "error": "HTTP Error"}
    except: return {"success": False, "error": "Request Failed"}

def create_mod_zip(mod_data):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in mod_data.get("all_files", {}).items():
            zf.writestr(name, content.encode("utf-8") if isinstance(content, str) else content)
        for d in ["sounds/", "images/", "animations/"]: zf.writestr(d, "")
    buf.seek(0)
    return buf.getvalue()

# ========================
# 🚀 生成逻辑 (包含加载动画)
# ========================
def start_full_generation():
    st.markdown('<div class="gen-progress-box">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#FFD700;margin-bottom:10px;">世界正在扭曲...</h2>', unsafe_allow_html=True)
    st.markdown('<p>The shadows are weaving your madness...</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    
    with st.spinner("📝 Qwen 正在锻造 Mod 代码..."):
        progress_bar.progress(30)
        result = design_with_llm(st.session_state.final_design, st.session_state.messages)
    
    with st.spinner("🎨 正在优化视觉图腾..."):
        progress_bar.progress(60)
        visual = optimize_visual_prompt(st.session_state.final_design)
        prompt = visual.get("optimized_prompt", "dst mod icon")
        
    with st.spinner("🖼️ Pollinations.ai 正在绘制灵魂图像..."):
        progress_bar.progress(80)
        icon = generate_icon_with_pollinations(prompt)
        if icon["success"]:
            st.image(icon["url"], width=200)
            result.setdefault("data", {}).setdefault("files", {})["modicon.tex"] = base64.b64decode(icon["base64"])
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
        
    progress_bar.progress(100)
    st.success("✅ MOD 铸造成功！")
    
    # 保存结果
    mod_data = result.get("data", {})
    st.session_state.generated_mods.append({
        "id": len(st.session_state.generated_mods)+1,
        "name": mod_data.get("name", "Unnamed Mod"),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "design": st.session_state.final_design,
        "all_files": mod_data.get("files", {})
    })
    st.session_state.mode = "done"
    st.rerun()

# ========================
# 💬 聊天界面 (Explore & Rapid)
# ========================
if st.session_state.mode in ["explore", "rapid"]:
    title = "👁️ 迷雾探路者" if st.session_state.mode == "explore" else "🔥 意志铸剑者"
    st.markdown(f"<h3 style='text-align:center;color:#FFD700;'>{title} - { '探索设计模式' if st.session_state.mode == 'explore' else '快速生成模式'}</h3>", unsafe_allow_html=True)

    # 渲染对话记录
    for msg in st.session_state.messages:
        role_class = "assistant" if msg["role"] == "assistant" else ""
        name = "暗影设计助手" if msg["role"] == "assistant" else "求生者"
        color = "#66BB6A" if msg["role"] == "assistant" else "#FF8C00"
        st.markdown(f'<div class="chat-msg {role_class}"><b style="color:{color};">{name}</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    # 输入框
    user_input = st.chat_input("输入你的想法...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("暗影低语中..."):
            # 无论哪个模式，初步对话都用 explore_with_llm 来细化
            reply = explore_with_llm(user_input, st.session_state.messages[:-1])
            st.session_state.messages.append({"role": "assistant", "content": reply if isinstance(reply, str) else reply.get("text", "...")})
        st.rerun()

    # MOD 生成按钮 (点击后才开始生成流程)
    if len(st.session_state.messages) >= 2:
        st.markdown("<div style='text-align:center;margin-top:30px;'>", unsafe_allow_html=True)
        if st.button("确认生成", key="gen_btn"):
            st.session_state.final_design = "\n".join([f"{m['role']}:{m['content']}" for m in st.session_state.messages])
            st.session_state.generating = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.generating:
        start_full_generation()

    if st.button("← 返回主页"):
        st.session_state.mode = "home"
        st.session_state.messages = []
        st.session_state.generating = False
        st.rerun()

# ========================
# ✅ 完成界面
# ========================
elif st.session_state.mode == "done":
    st.markdown("<h2 style='text-align:center;'>✨ MOD 铸造完成！</h2>", unsafe_allow_html=True)
    st.info("请在侧边栏的 Mod 库中下载你的作品。")
    if st.button("🏠 返回主页"):
        st.session_state.mode = "home"
        st.rerun()

# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    if not st.session_state.generated_mods:
        st.write("暂无 Mod 创作")
    else:
        for mod in st.session_state.generated_mods:
            st.write(f"**{mod['name']}**")
            st.download_button("💾 下载", data=create_mod_zip(mod), file_name=f"{mod['name']}.zip", key=f"dl_{mod['id']}")
    
    st.divider()
    if st.button("🗑️ 清除全部记录"):
        st.session_state.clear()
        st.rerun()
