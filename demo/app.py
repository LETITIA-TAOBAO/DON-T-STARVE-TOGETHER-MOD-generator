import streamlit as st
import io
import json
import zipfile
import requests
import base64
from datetime import datetime

# ========================
# ⚠️ LLM 导入
# ========================
try:
    from qwen_client import (
        explore_with_llm,
        rapid_with_llm,
        summarize_design,
        design_with_llm,
        optimize_visual_prompt,
        generate_sound_prompts,
        generate_sound_effect,
    )
except ImportError as e:
    st.error(f"❌ 永恒大陆加载失败：{e}")
    st.stop()

# ========================
# 🔧 Session State
# ========================
for key, val in {
    "mode": "home",
    "messages": [],
    "generated_mods": [],
    "final_design": "",
    "design_spec": None,
    "visual_result": None,
    "sound_result": None,
    "preview_image_url": None,
    "preview_image_b64": None,
    "preview_approved": False,
    "stage": "chat",
    "generating": False,
    "sound_audio_cache": {},
    "show_producer_msg": False,
    "show_install_guide": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========================
# 📸 背景图
# ========================
BASE_URL = (
    "https://raw.githubusercontent.com/LETITIA-TAOBAO/"
    "DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
)
BG_URL = BASE_URL + "background.jpg.png"

# ========================
# 🎨 CSS
# ========================
# 根据当前模式决定是否显示创作者信息框
creator_tag_css = ""
if st.session_state.mode == "home":
    creator_tag_css = """
    /* ── 创作者信息水印（仅主页显示） ── */
    .creator-tag {
        position: fixed;
        bottom: 20px;
        right: 24px;
        z-index: 9999;
        text-align: right;
        pointer-events: auto;
        background: rgba(15,8,2,0.88);
        border: 2px solid rgba(139,100,32,0.5);
        border-radius: 6px;
        padding: 14px 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.7);
        opacity: 0.85;
        transition: all 0.3s ease;
    }
    .creator-tag:hover {
        opacity: 1.0;
        border-color: rgba(200,168,75,0.75);
        box-shadow: 0 6px 24px rgba(0,0,0,0.8), 0 0 20px rgba(200,168,75,0.2);
    }
    .creator-tag p {
        font-family: 'Cinzel', serif !important;
        font-size: 0.75rem !important;
        color: #C8A868 !important;
        letter-spacing: 2px !important;
        margin: 4px 0 !important;
        line-height: 1.7 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.9) !important;
    }
    .creator-tag .creator-name {
        font-weight: 600 !important;
        color: #D4A843 !important;
        font-size: 0.82rem !important;
    }
    .creator-tag .creator-divider {
        border: none;
        border-top: 1px solid rgba(139,100,32,0.4);
        margin: 8px 0;
        width: 100%;
    }
    """

# 构建完整的CSS
css_content = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC:ital@0;1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');

.stApp {{
    background-image: url("{BG_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp::before {{
    content:"";
    position:fixed;
    inset:0;
    background:rgba(8,4,0,0.45);
    z-index:0;
    pointer-events:none;
}}

.stAppViewContainer .stMainBlockContainer, .block-container {{
    background:rgba(20,11,3,0.55) !important;
    backdrop-filter:blur(2px);
}}

html,[class*="css"] {{
    background-color:transparent !important;
}}

section[data-testid="stSidebar"] {{
    background:rgba(15,8,2,0.72) !important;
    border-right:2px solid rgba(160,100,30,0.35) !important;
    backdrop-filter:blur(4px);
}}

section[data-testid="stSidebar"]>div {{
    background:transparent !important;
}}

section[data-testid="stSidebar"] * {{
    color:#C8A868 !important;
}}

section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
    color:#D4A843 !important;
}}

h1,h2,h3 {{
    font-family:'Cinzel Decorative',serif !important;
    color:#D4A843 !important;
    text-shadow:0 0 20px rgba(200,160,60,0.4),2px 2px 4px rgba(0,0,0,0.8) !important;
    letter-spacing:2px !important;
}}

p,span,div,label,li {{
    font-family:'IM Fell English SC',serif !important;
    color:#EDD9A3 !important;
}}

.dst-banner {{
    background:rgba(15,8,2,0.82);
    border:2px solid #7B5820;
    border-top:3px solid #C8A84B;
    border-bottom:3px solid #C8A84B;
    padding:36px 44px 30px;
    border-radius:4px;
    text-align:center;
    margin:10px auto 28px;
    max-width:820px;
    box-shadow:0 0 60px rgba(0,0,0,0.7),inset 0 0 30px rgba(0,0,0,0.4);
    position:relative;
}}

.dst-banner::before,.dst-banner::after {{
    content:"✦";
    position:absolute;
    top:12px;
    color:#7B5820;
    font-size:1.2rem;
}}

.dst-banner::before {{
    left:18px;
}}

.dst-banner::after {{
    right:18px;
}}

.banner-sub {{
    font-family:'Cinzel',serif !important;
    color:#7B5820 !important;
    font-size:0.8rem;
    letter-spacing:4px;
    margin-top:5px;
}}

.banner-divider {{
    border:none;
    border-top:1px solid #5a3a10;
    width:40%;
    margin:16px auto;
}}

.banner-quote {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.98rem;
    line-height:1.9;
    color:#C8A86A !important;
    font-style:italic;
}}

.mode-cards {{
    display:flex;
    gap:24px;
    justify-content:center;
    margin:0 auto 28px;
    max-width:880px;
}}

.mode-card {{
    flex:1;
    max-width:420px;
    background:rgba(18,10,3,0.84);
    border:2px solid #5a3a10;
    border-radius:6px;
    padding:26px 22px 22px;
    text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.5);
    position:relative;
    overflow:hidden;
}}

.mode-card::before {{
    content:"";
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:3px;
    background:linear-gradient(90deg,transparent,#C8A84B,transparent);
}}

.mode-card-icon {{
    font-size:2.2rem;
    margin-bottom:8px;
    display:block;
}}

.mode-card-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.1rem !important;
    color:#D4A843 !important;
    margin:0 0 4px !important;
}}

.mode-card-sub {{
    font-family:'Cinzel',serif !important;
    font-size:0.7rem !important;
    color:#7a5a28 !important;
    letter-spacing:3px;
    margin-bottom:12px !important;
    display:block;
}}

.mode-card-divider {{
    border:none;
    border-top:1px solid #3a2008;
    margin:10px auto;
    width:60%;
}}

.mode-card-desc {{
    font-size:0.88rem !important;
    line-height:1.8 !important;
    color:#B89A62 !important;
    margin:0 !important;
}}

.mode-card-en {{
    font-style:italic !important;
    color:#5a4020 !important;
    font-size:0.76em !important;
    display:block !important;
    margin-top:10px !important;
}}

.mode-card-hint {{
    display:inline-block;
    margin-top:16px;
    padding:5px 18px;
    border:1px solid #7B5820;
    border-radius:3px;
    font-size:0.8rem !important;
    color:#C8A84B !important;
    background:rgba(100,60,10,0.18);
    letter-spacing:1px;
}}

div[data-testid="stButton"]>button {{
    background:rgba(20,10,3,0.87) !important;
    border:2px solid #7a5020 !important;
    color:#D4A843 !important;
    font-family:'IM Fell English SC',serif !important;
    font-size:1rem !important;
    letter-spacing:1px !important;
    padding:10px 24px !important;
    border-radius:4px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.5) !important;
    text-shadow:0 0 8px rgba(200,160,60,0.35) !important;
}}

div[data-testid="stButton"]>button:hover {{
    background:rgba(50,25,5,0.96) !important;
    border-color:#C8A84B !important;
    color:#FFD700 !important;
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(0,0,0,0.6),0 0 15px rgba(200,168,75,0.2) !important;
}}

.primary-btn div[data-testid="stButton"]>button {{
    background:rgba(55,22,5,0.92) !important;
    border:2px solid #C8A84B !important;
    font-size:1.08rem !important;
    padding:13px 32px !important;
    letter-spacing:2px !important;
}}

.primary-btn div[data-testid="stButton"]>button:hover {{
    background:rgba(85,35,8,0.97) !important;
    box-shadow:0 0 30px rgba(200,168,75,0.28),0 6px 20px rgba(0,0,0,0.6) !important;
}}

.danger-btn div[data-testid="stButton"]>button {{
    border-color:#6B2020 !important;
    color:#BB5555 !important;
}}

.danger-btn div[data-testid="stButton"]>button:hover {{
    border-color:#CC3333 !important;
    color:#FF7777 !important;
    background:rgba(50,8,8,0.92) !important;
}}

.mode-header {{
    background:rgba(12,6,1,0.80);
    border:1px solid #4a3010;
    border-top:3px solid #9B7830;
    border-radius:4px;
    padding:20px 28px 16px;
    text-align:center;
    margin-bottom:18px;
}}

.mode-header h3 {{
    font-size:1.55rem !important;
    margin:0 0 5px !important;
}}

.mode-header p {{
    font-size:0.86rem !important;
    color:#7a6040 !important;
    margin:0 !important;
}}

.chat-user {{
    background:rgba(25,14,4,0.90);
    border-left:3px solid #C8820C;
    border-bottom:1px solid rgba(200,130,12,0.18);
    padding:12px 16px;
    margin:10px 0;
    border-radius:0 6px 6px 0;
}}

.chat-ai {{
    background:rgba(8,20,10,0.90);
    border-left:3px solid #4A9A50;
    border-bottom:1px solid rgba(74,154,80,0.18);
    padding:12px 16px;
    margin:10px 0;
    border-radius:0 6px 6px 0;
}}

.chat-name {{
    font-family:'Cinzel',serif !important;
    font-size:0.78rem !important;
    letter-spacing:2px !important;
    display:block;
    margin-bottom:5px;
}}

.chat-content {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.93rem !important;
    line-height:1.78 !important;
    color:#D4BC88 !important;
    white-space:pre-wrap;
}}

.preview-box {{
    background:rgba(12,6,1,0.90);
    border:2px solid #6B5018;
    border-radius:6px;
    padding:22px;
    margin:14px 0;
}}

.preview-box-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.05rem !important;
    color:#D4A843 !important;
    text-align:center;
    margin-bottom:14px !important;
    letter-spacing:2px;
}}

.spec-grid {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:8px;
    margin:10px
