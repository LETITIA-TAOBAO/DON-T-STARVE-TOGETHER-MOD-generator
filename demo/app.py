import streamlit as st
import io
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
    )
except ImportError as e:
    st.error(f"❌ 模块加载失败：{e}")
    st.stop()

# ========================
# 🔧 Session State
# ========================
for key, val in {
    "mode":            "home",
    "messages":        [],
    "generated_mods":  [],
    "final_design":    "",
    "design_spec":     None,   # summarize_design() 的结构化结果
    "visual_result":   None,   # optimize_visual_prompt() 的结果
    "sound_result":    None,   # generate_sound_prompts() 的结果
    "preview_image_url": None, # 预览图 URL
    "preview_approved": False, # 用户是否确认了预览
    "stage": "chat",           # chat → preview → generating → done
    "generating": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========================
# 📸 背景图路径
# ========================
BASE_URL = (
    "https://raw.githubusercontent.com/LETITIA-TAOBAO/"
    "DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
)
BG_URL = BASE_URL + "background.jpg.png"

# ========================
# 🎨 CSS
# ========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC:ital@0;1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');

/* ── 背景 ── */
.stApp {{
    background-image: url("{BG_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content: "";
    position: fixed; inset: 0;
    background: rgba(8,4,0,0.45);
    z-index: 0;
    pointer-events: none;
}}
.stAppViewContainer .stMainBlockContainer,
.block-container {{
    background: rgba(20,11,3,0.55) !important;
    backdrop-filter: blur(2px);
}}
html,[class*="css"] {{ background-color:transparent !important; }}

/* ── 侧边栏 ── */
section[data-testid="stSidebar"] {{
    background: rgba(15,8,2,0.72) !important;
    border-right: 2px solid rgba(160,100,30,0.35) !important;
    backdrop-filter: blur(4px);
}}
section[data-testid="stSidebar"] > div {{ background:transparent !important; }}
section[data-testid="stSidebar"] * {{ color:#C8A868 !important; }}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{ color:#D4A843 !important; }}

/* ── 字体 ── */
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

/* ── Banner ── */
.dst-banner {{
    background:rgba(15,8,2,0.80);
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
    content:"✦"; position:absolute; top:12px;
    color:#7B5820; font-size:1.2rem;
}}
.dst-banner::before {{ left:18px; }}
.dst-banner::after  {{ right:18px; }}
.banner-sub {{
    font-family:'Cinzel',serif !important;
    color:#7B5820 !important; font-size:0.8rem;
    letter-spacing:4px; margin-top:5px;
}}
.banner-divider {{
    border:none; border-top:1px solid #5a3a10;
    width:40%; margin:16px auto;
}}
.banner-quote {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.98rem; line-height:1.9;
    color:#C8A86A !important; font-style:italic;
}}

/* ── 模式卡片 ── */
.mode-cards {{
    display:flex; gap:24px; justify-content:center;
    margin:0 auto 28px; max-width:880px;
}}
.mode-card {{
    flex:1; max-width:420px;
    background:rgba(18,10,3,0.82);
    border:2px solid #5a3a10; border-radius:6px;
    padding:26px 22px 22px; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.5);
    position:relative; overflow:hidden;
    transition:all 0.3s ease;
}}
.mode-card::before {{
    content:""; position:absolute; top:0;left:0;right:0;
    height:3px;
    background:linear-gradient(90deg,transparent,#C8A84B,transparent);
}}
.mode-card-icon  {{ font-size:2.2rem; margin-bottom:8px; display:block; }}
.mode-card-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.1rem !important; color:#D4A843 !important;
    margin:0 0 4px !important;
}}
.mode-card-sub {{
    font-family:'Cinzel',serif !important;
    font-size:0.7rem !important; color:#7a5a28 !important;
    letter-spacing:3px; margin-bottom:12px !important; display:block;
}}
.mode-card-divider {{
    border:none; border-top:1px solid #3a2008;
    margin:10px auto; width:60%;
}}
.mode-card-desc {{
    font-size:0.88rem !important; line-height:1.8 !important;
    color:#B89A62 !important; margin:0 !important;
}}
.mode-card-en {{
    font-style:italic !important; color:#5a4020 !important;
    font-size:0.76em !important; display:block !important;
    margin-top:10px !important;
}}
.mode-card-hint {{
    display:inline-block; margin-top:16px; padding:5px 18px;
    border:1px solid #7B5820; border-radius:3px;
    font-size:0.8rem !important; color:#C8A84B !important;
    background:rgba(100,60,10,0.18); letter-spacing:1px;
}}

/* ── 按钮 ── */
div[data-testid="stButton"] > button {{
    background:rgba(20,10,3,0.85) !important;
    border:2px solid #7a5020 !important;
    color:#D4A843 !important;
    font-family:'IM Fell English SC',serif !important;
    font-size:1rem !important; letter-spacing:1px !important;
    padding:10px 24px !important; border-radius:4px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.5) !important;
    text-shadow:0 0 8px rgba(200,160,60,0.35) !important;
}}
div[data-testid="stButton"] > button:hover {{
    background:rgba(50,25,5,0.95) !important;
    border-color:#C8A84B !important; color:#FFD700 !important;
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(0,0,0,0.6),0 0 15px rgba(200,168,75,0.2) !important;
}}

/* 大号主操作按钮 */
.primary-btn div[data-testid="stButton"] > button {{
    background:rgba(55,22,5,0.92) !important;
    border:2px solid #C8A84B !important;
    font-size:1.08rem !important; padding:13px 32px !important;
    letter-spacing:2px !important;
}}
.primary-btn div[data-testid="stButton"] > button:hover {{
    background:rgba(85,35,8,0.97) !important;
    box-shadow:0 0 30px rgba(200,168,75,0.28),0 6px 20px rgba(0,0,0,0.6) !important;
}}

/* 危险/否定按钮 */
.danger-btn div[data-testid="stButton"] > button {{
    border-color:#8B2020 !important; color:#CC6666 !important;
}}
.danger-btn div[data-testid="stButton"] > button:hover {{
    border-color:#CC3333 !important; color:#FF8888 !important;
    background:rgba(60,10,10,0.90) !important;
}}

/* ── 模式页 Header ── */
.mode-header {{
    background:rgba(12,6,1,0.78);
    border:1px solid #4a3010; border-top:3px solid #9B7830;
    border-radius:4px; padding:20px 28px 16px;
    text-align:center; margin-bottom:18px;
}}
.mode-header h3 {{ font-size:1.55rem !important; margin:0 0 5px !important; }}
.mode-header p  {{ font-size:0.86rem !important; color:#7a6040 !important; margin:0 !important; }}

/* ── 进度标签 ── */
.progress-tag {{
    display:inline-block; padding:3px 12px;
    border-radius:12px; font-size:0.78rem !important;
    letter-spacing:1px; margin:4px 3px;
}}
.tag-done    {{ background:rgba(30,70,30,0.6); border:1px solid #4a8a4a; color:#88cc88 !important; }}
.tag-pending {{ background:rgba(60,40,10,0.6); border:1px solid #7a5a20; color:#aa8840 !important; }}

/* ── 聊天气泡 ── */
.chat-user {{
    background:rgba(25,14,4,0.88);
    border-left:3px solid #C8820C;
    border-bottom:1px solid rgba(200,130,12,0.18);
    padding:12px 16px; margin:10px 0;
    border-radius:0 6px 6px 0;
}}
.chat-ai {{
    background:rgba(8,20,10,0.88);
    border-left:3px solid #4A9A50;
    border-bottom:1px solid rgba(74,154,80,0.18);
    padding:12px 16px; margin:10px 0;
    border-radius:0 6px 6px 0;
}}
.chat-name {{
    font-family:'Cinzel',serif !important;
    font-size:0.78rem !important; letter-spacing:2px !important;
    display:block; margin-bottom:5px;
}}
.chat-content {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.93rem !important; line-height:1.78 !important;
    color:#D4BC88 !important; white-space:pre-wrap;
}}

/* ── 预览卡片 ── */
.preview-box {{
    background:rgba(12,6,1,0.88);
    border:2px solid #7B5820; border-radius:6px;
    padding:24px; margin:16px 0;
}}
.preview-box-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.1rem !important; color:#D4A843 !important;
    text-align:center; margin-bottom:16px !important;
    letter-spacing:2px;
}}
.spec-grid {{
    display:grid; grid-template-columns:1fr 1fr;
    gap:10px; margin:12px 0;
}}
.spec-item {{
    background:rgba(25,14,4,0.70);
    border:1px solid #3a2510; border-radius:4px;
    padding:10px 14px;
}}
.spec-label {{
    font-family:'Cinzel',serif !important;
    font-size:0.7rem !important; color:#7a5a28 !important;
    letter-spacing:2px; display:block; margin-bottom:4px;
}}
.spec-value {{
    font-size:0.88rem !important; color:#D4BC88 !important;
}}

/* ── 音效卡片 ── */
.sound-card {{
    background:rgba(8,16,8,0.80);
    border:1px solid #2a4a2a; border-radius:4px;
    padding:10px 14px; margin:8px 0;
}}
.sound-trigger {{
    font-family:'Cinzel',serif !important;
    font-size:0.72rem !important; color:#4A9A50 !important;
    letter-spacing:2px; display:block; margin-bottom:3px;
}}

/* ── 生成进度 ── */
.gen-box {{
    background:rgba(12,6,1,0.90);
    border:2px solid #7a4010; border-top:3px solid #C8A84B;
    border-radius:6px; padding:30px;
    text-align:center; margin:14px auto; max-width:600px;
}}

/* ── 输入框 ── */
[data-testid="stChatInput"] {{
    background:rgba(15,8,2,0.80) !important;
    border-top:1px solid rgba(139,100,32,0.35) !important;
}}
[data-testid="stChatInput"] textarea {{
    background:rgba(20,11,3,0.92) !important;
    border:1px solid #4a3010 !important;
    color:#EDD9A3 !important;
    font-family:'IM Fell English SC',serif !important;
    border-radius:4px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color:#C8A84B !important;
    box-shadow:0 0 10px rgba(200,168,75,0.18) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color:#5a4028 !important; font-style:italic !important;
}}

/* ── 进度条 ── */
.stProgress > div > div > div > div {{
    background:linear-gradient(90deg,#6B3A08,#C8A84B,#F0D070) !important;
    border-radius:4px !important;
}}

/* ── Expander ── */
.st-expander {{
    background:rgba(20,11,3,0.72) !important;
    border:1px solid #4a3010 !important;
    border-radius:4px !important;
}}

hr {{ border:none !important; border-top:1px solid rgba(139,100,32,0.30) !important; margin:18px 0 !important; }}
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:rgba(10,5,0,0.3); }}
::-webkit-scrollbar-thumb {{ background:#5a3810; border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:#8B6420; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🔧 工具函数
# ══════════════════════════════════════════════════════════════

def generate_atlas_xml() -> str:
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
  <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''

def fetch_image(prompt: str) -> dict:
    try:
        enc = prompt.replace(" ", "+").replace("&", "%26")
        url = (f"https://image.pollinations.ai/prompt/{enc}"
               f"?width=512&height=512&nologo=true"
               f"&seed={int(datetime.now().timestamp())}")
        r = requests.get(url, timeout=55)
        if r.status_code == 200 and len(r.content) > 1000:
            return {"ok": True,
                    "b64": base64.b64encode(r.content).decode(),
                    "url": url}
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def make_zip(mod: dict) -> bytes:
    install_txt = """══════════════════════════════════════
   饥荒联机版 MOD 安装指南
══════════════════════════════════════

方法一（推荐）：Steam 创意工坊
  直接订阅即可，游戏自动下载

方法二：手动安装
  ① 解压本 ZIP 文件
  ② 将解压后的文件夹复制到：
     Windows：
     C:/Users/你的用户名/Documents/Klei/
     DoNotStarveTogether/mods/
     
     Steam 默认路径：
     Steam/steamapps/common/
     Don't Starve Together/mods/
     
  ③ 启动游戏 → 主菜单 → 模组
     找到本 Mod → 点击启用
     
  ④ 创建或进入存档，Mod 即刻生效

⚠️  注意事项：
  - api_version 必须为 10
  - 多人游戏中所有玩家需要安装
  - 如遇报错请检查 log.txt

══════════════════════════════════════
"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in mod.get("all_files", {}).items():
            if isinstance(data, str):
                zf.writestr(name, data.encode("utf-8"))
            elif isinstance(data, bytes):
                zf.writestr(name, data)
        for d in ["sounds/", "images/", "animations/"]:
            zf.writestr(d, b"")
        zf.writestr("安装说明_README.txt", install_txt.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()

def render_chat(messages: list):
    for m in messages:
        if not isinstance(m, dict):
            continue
        if m["role"] == "user":
            st.markdown(
                f'<div class="chat-user">'
                f'<span class="chat-name" style="color:#C8820C;">✦ SURVIVOR</span>'
                f'<span class="chat-content">{m["content"]}</span>'
                f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-ai">'
                f'<span class="chat-name" style="color:#4A9A50;">✦ SHADOW ARCHITECT</span>'
                f'<span class="chat-content">{m["content"]}</span>'
                f'</div>', unsafe_allow_html=True)

def reset_to_home():
    for k in ["messages","final_design","design_spec","visual_result",
              "sound_result","preview_image_url","preview_approved",
              "generating"]:
        st.session_state[k] = [] if k == "messages" else \
                               False if k in ["preview_approved","generating"] else None
    st.session_state.stage = "chat"
    st.session_state.mode  = "home"


# ══════════════════════════════════════════════════════════════
# 🎨 预览页面（图片 + 音效 + 设计规格确认）
# ══════════════════════════════════════════════════════════════

def render_preview_stage():
    """
    Stage: preview
    展示：设计规格卡 + 预览图 + 音效方案
    用户选择：✅ 确认铸造 / 🔄 重新设计
    """
    spec   = st.session_state.design_spec   or {}
    visual = st.session_state.visual_result or {}
    sound  = st.session_state.sound_result  or {}
    obj    = spec.get("main_object", {})

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#C8A84B !important;">✦ 设计预览 · Design Preview</h3>
      <p>在混沌凝固之前，确认你的设计——</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 1. 设计规格卡 ──────────────────────────────
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown(f'<p class="preview-box-title">📋 MOD 设计规格</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="spec-grid">
      <div class="spec-item">
        <span class="spec-label">MOD NAME</span>
        <span class="spec-value">{spec.get("mod_name_cn","—")} · {spec.get("mod_name_en","—")}</span>
      </div>
      <div class="spec-item">
        <span class="spec-label">TYPE</span>
        <span class="spec-value">{spec.get("mod_type","—")}</span>
      </div>
      <div class="spec-item" style="grid-column:span 2">
        <span class="spec-label">CORE FUNCTION</span>
        <span class="spec-value">{spec.get("core_function","—")}</span>
      </div>
      <div class="spec-item" style="grid-column:span 2">
        <span class="spec-label">MAIN OBJECT · {obj.get("name_cn","")}</span>
        <span class="spec-value">{obj.get("appearance","—")}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 数值
    stats = spec.get("stats", {})
    stat_items = [(k.upper(), v) for k, v in stats.items() if v is not None]
    if stat_items:
        stat_html = "".join(
            f'<div class="spec-item"><span class="spec-label">{k}</span>'
            f'<span class="spec-value">{v}</span></div>'
            for k, v in stat_items
        )
        st.markdown(f'<div class="spec-grid">{stat_html}</div>', unsafe_allow_html=True)

    # 配方
    recipe = spec.get("recipe", [])
    if recipe:
        recipe_str = "  +  ".join(recipe)
        st.markdown(
            f'<div class="spec-item" style="margin-top:8px;">'
            f'<span class="spec-label">RECIPE · 合成配方</span>'
            f'<span class="spec-value">{recipe_str}</span></div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 2. 预览图 ──────────────────────────────────
    col_img, col_sound = st.columns([1, 1])

    with col_img:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown('<p class="preview-box-title">🎨 外观预览</p>', unsafe_allow_html=True)

        img_url = st.session_state.preview_image_url
        if img_url:
            st.image(img_url, caption=obj.get("name_cn","MOD 图标"),
                     use_container_width=True)

            used_prompt = visual.get("optimized_prompt","")
            if used_prompt:
                st.markdown(
                    f'<p style="font-size:0.72rem;color:#5a4020;'
                    f'font-style:italic;text-align:center;margin-top:6px;">'
                    f'{used_prompt[:80]}…</p>',
                    unsafe_allow_html=True)

            # 重新生成按钮
            if st.button("🔄 重新生成图片", key="regen_img", use_container_width=True):
                with st.spinner("✦ 召唤新的图腾形象……"):
                    prompt = visual.get("optimized_prompt",
                             visual.get("fallback_prompt",
                             "Don't Starve style dark fantasy item"))
                    new_img = fetch_image(prompt)
                    if new_img["ok"]:
                        st.session_state.preview_image_url = new_img["url"]
                        st.session_state.preview_image_b64 = new_img["b64"]
                    else:
                        st.warning(f"生成失败：{new_img['err']}")
                st.rerun()
        else:
            st.markdown(
                '<p style="color:#5a4028;text-align:center;'
                'font-style:italic;padding:40px 0;">图腾尚未显现……</p>',
                unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── 3. 音效方案 ────────────────────────────────
    with col_sound:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown('<p class="preview-box-title">🔊 音效方案</p>', unsafe_allow_html=True)

        sfx_list = sound.get("sound_effects", [])
        if sfx_list:
            for sfx in sfx_list:
                trigger = sfx.get("trigger", "")
                desc_cn = sfx.get("description_cn", "")
                prompt  = sfx.get("prompt_en", "")
                dur     = sfx.get("duration", "short")
                st.markdown(
                    f'<div class="sound-card">'
                    f'<span class="sound-trigger">▶ {trigger.upper()}</span>'
                    f'<span class="spec-value">{desc_cn}</span><br>'
                    f'<span style="font-size:0.72rem;color:#3a5a3a;'
                    f'font-style:italic;">{prompt} [{dur}]</span>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="color:#5a4028;font-style:italic;'
                'text-align:center;padding:20px 0;">音效方案尚未凝聚……</p>',
                unsafe_allow_html=True)

        # 环境音
        ambient = sound.get("ambient_sound", {})
        if ambient.get("needed"):
            st.markdown(
                f'<div class="sound-card" style="border-color:#1a3a1a;">'
                f'<span class="sound-trigger">♪ AMBIENT</span>'
                f'<span class="spec-value">{ambient.get("description_cn","")}</span>'
                f'</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 4. 确认 / 重设计 按钮 ─────────────────────
    st.markdown("""
    <p style="text-align:center;font-size:0.85rem;color:#5a4020;
              font-style:italic;margin-bottom:10px;letter-spacing:1px;">
      ✦ 确认无误后，令混沌永久凝固 ✦
    </p>
    """, unsafe_allow_html=True)

    ca, cb, cc = st.columns([2, 3, 2])

    with cb:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("⚙ 确认并铸造 MOD · Forge",
                     key="confirm_forge", use_container_width=True):
            st.session_state.preview_approved = True
            st.session_state.stage = "generating"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✏ 继续调整设计", key="back_to_chat", use_container_width=True):
            st.session_state.stage = "chat"
            st.rerun()
    with c2:
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("✕ 放弃，返回主页", key="abort_preview", use_container_width=True):
            reset_to_home()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ⚙️ 生成阶段
# ══════════════════════════════════════════════════════════════

def render_generating_stage():
    spec = st.session_state.design_spec or {}

    st.markdown("""
    <div class="gen-box">
      <h2 style="font-size:1.75rem;margin:0 0 8px 0;">⚙ 混沌正在凝固……</h2>
      <p style="color:#7a6040;font-size:0.86rem;margin:0;font-style:italic;">
        The darkness weaves your will into reality...
      </p>
    </div>
    """, unsafe_allow_html=True)

    bar = st.progress(0)

    # Step 1: 生成代码
    with st.spinner("✦ 暗影法典正在书写 Lua 代码……"):
        bar.progress(20)
        design_str = st.session_state.final_design
        result = design_with_llm(design_str, st.session_state.messages)
    bar.progress(55)

    # Step 2: 附加图标
    with st.spinner("✦ 封印图腾形象……"):
        b64 = getattr(st.session_state, "preview_image_b64", None)
        # 从 session_state 取已生成的图
        b64 = st.session_state.get("preview_image_b64")
        if b64:
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(b64)
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
            st.success("✦ 图腾已封印！")
        else:
            st.warning("图腾形象缺失，跳过图标封印。")
    bar.progress(80)

    # Step 3: 整理入库
    with st.spinner("✦ 将混沌结晶归入典藏……"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("text", "✦ Mod 铸造完毕。")
        })
        d = result.get("data", {})
        if d:
            st.session_state.generated_mods.append({
                "id":        len(st.session_state.generated_mods) + 1,
                "name":      d.get("name", spec.get("mod_name_en",
                             f"Mod_{datetime.now().strftime('%H%M')}")),
                "name_cn":   spec.get("mod_name_cn", ""),
                "desc":      d.get("desc", spec.get("description", "")),
                "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                "design":    st.session_state.final_design,
                "spec":      spec,
                "all_files": d.get("files", {}),
                "image_url": st.session_state.preview_image_url,
            })
    bar.progress(100)

    st.session_state.stage     = "done"
    st.session_state.generating = False
    st.rerun()


# ══════════════════════════════════════════════════════════════
# 💬 对话阶段（chat → preview 的入口）
# ══════════════════════════════════════════════════════════════

def render_chat_stage(mode: str):
    """
    mode: "explore" 或 "rapid"
    对话完成后：点击「确认并预览」→ 调用 summarize + 生成图片 → 进入 preview
    """
    is_explore = (mode == "explore")

    if is_explore:
        st.markdown("""
        <div class="mode-header">
          <h3 style="color:#4CAF50 !important;">👁 迷雾探路者 · Shadow Explore</h3>
          <p>与暗影助手充分对话，明确设计后点击「预览并确认」</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="mode-header">
          <h3 style="color:#D4A843 !important;">⚡ 意志铸剑者 · Rapid Forge</h3>
          <p>输入你的构想，暗影助手将细化设计，确认后点击「预览并确认」</p>
        </div>
        """, unsafe_allow_html=True)

    # 渲染历史对话
    render_chat(st.session_state.messages)

    # 输入框
    placeholder = ("低语你的构想，暗影将倾听……"
                   if is_explore else "将你的意志化为文字……")
    user_inp = st.chat_input(placeholder)

    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("✦ 暗影正在回应……"):
            try:
                if is_explore:
                    r = explore_with_llm(st.session_state.messages)
                else:
                    r = rapid_with_llm(st.session_state.messages)
                reply = r.get("text", str(r)) if isinstance(r, dict) else str(r)
            except Exception as exc:
                reply = f"（暗影沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # ── 预览按钮（至少 1 轮对话后出现）──
    if len(st.session_state.messages) >= 2:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align:center;font-size:0.83rem;color:#5a4020;
                  font-style:italic;margin-bottom:8px;letter-spacing:1px;">
          ✦ 设计已足够清晰？令混沌凝固成形 ✦
        </p>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("✦ 预览并确认设计 · Preview & Confirm",
                         key=f"{mode}_preview_btn", use_container_width=True):
                _enter_preview()
            st.markdown('</div>', unsafe_allow_html=True)

    # 返回
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 归返主页 · Return", key=f"back_{mode}"):
        reset_to_home()
        st.rerun()


def _enter_preview():
    """点击「预览并确认」后的处理：总结设计 + 生成图片 + 生成音效"""
    with st.spinner("✦ 暗影正在整理设计蓝图……"):
        spec = summarize_design(st.session_state.messages)
        st.session_state.design_spec = spec
        # 把规格转为字符串作为 final_design
        import json
        st.session_state.final_design = json.dumps(spec, ensure_ascii=False, indent=2)

    with st.spinner("✦ 召唤图腾形象……"):
        visual = optimize_visual_prompt(spec)
        st.session_state.visual_result = visual
        prompt = visual.get("optimized_prompt",
                 visual.get("fallback_prompt",
                 "Don't Starve style dark fantasy item"))
        img = fetch_image(prompt)
        if img["ok"]:
            st.session_state.preview_image_url = img["url"]
            st.session_state.preview_image_b64 = img["b64"]
        else:
            st.session_state.preview_image_url = None
            st.session_state.preview_image_b64 = None

    with st.spinner("✦ 编排音效方案……"):
        sound = generate_sound_prompts(spec)
        st.session_state.sound_result = sound

    st.session_state.stage = "preview"
    st.rerun()


# ══════════════════════════════════════════════════════════════
# ✅ 完成页
# ══════════════════════════════════════════════════════════════

def render_done_stage():
    spec = st.session_state.design_spec or {}

    st.markdown(f"""
    <div class="dst-banner">
      <h2 style="font-size:1.9rem;margin:0;">✨ MOD 已铸造完成</h2>
      <p class="banner-sub">THE MOD HAS BEEN FORGED INTO REALITY</p>
      <hr class="banner-divider">
      <p class="banner-quote">
        {spec.get("mod_name_cn","你的 MOD")} · {spec.get("mod_name_en","")}<br>
        <em>混沌已凝固，你的疯狂已成为现实。</em>
      </p>
    </div>
    """, unsafe_allow_html=True)

    # 最后几条对话
    render_chat(st.session_state.messages[-4:])

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        if st.button("✦ 继续雕琢 · Refine",
                     use_container_width=True, key="done_refine"):
            st.session_state.stage = "chat"
            st.session_state.mode  = "explore"
            st.rerun()
    with cb:
        if st.button("← 归返主页 · Return",
                     use_container_width=True, key="done_home"):
            reset_to_home()
            st.rerun()


# ══════════════════════════════════════════════════════════════
# 🏠 主页
# ══════════════════════════════════════════════════════════════

def render_home():
    st.markdown("""
    <div class="dst-banner">
      <h1 style="font-size:2.7rem;margin:0;">饥荒 MOD 生成器</h1>
      <p class="banner-sub">DON'T STARVE TOGETHER · MOD GENERATOR</p>
      <hr class="banner-divider">
      <p class="banner-quote">
        当理智归零，现实崩塌。<br>
        <em>You are no longer a survivor — but a Creator.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="mode-cards">
      <div class="mode-card">
        <span class="mode-card-icon">⚡</span>
        <p class="mode-card-title">意志铸剑者</p>
        <span class="mode-card-sub">RAPID FORGE</span>
        <hr class="mode-card-divider">
        <p class="mode-card-desc">
          当你已明晰 Mod 的核心法则与物品灵魂<br>
          无需徘徊于暗影之间<br>
          将你的疯狂构想直接锻造成可触及的现实
          <span class="mode-card-en">For when your vision is clear.</span>
        </p>
        <span class="mode-card-hint">点击下方按钮进入 ↓</span>
      </div>
      <div class="mode-card">
        <span class="mode-card-icon">👁</span>
        <p class="mode-card-title">迷雾探路者</p>
        <span class="mode-card-sub">SHADOW EXPLORE</span>
        <hr class="mode-card-divider">
        <p class="mode-card-desc">
          当灵感如迷雾般在你脑海中低语<br>
          混沌尚未凝聚成形<br>
          与暗影对话，让疯狂的蓝图逐渐清晰
          <span class="mode-card-en">For when inspiration is foggy.</span>
        </p>
        <span class="mode-card-hint">点击下方按钮进入 ↓</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("⚡ 快速生成 · Rapid Forge",
                     key="k_rapid", use_container_width=True):
            st.session_state.mode  = "rapid"
            st.session_state.stage = "chat"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.design_spec = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("👁 探索设计 · Shadow Explore",
                     key="k_explore", use_container_width=True):
            st.session_state.mode  = "explore"
            st.session_state.stage = "chat"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.design_spec = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🚦 路由主控制器
# ══════════════════════════════════════════════════════════════

mode  = st.session_state.mode
stage = st.session_state.stage

if mode == "home":
    render_home()

elif mode in ("explore", "rapid"):
    if stage == "chat":
        render_chat_stage(mode)
    elif stage == "preview":
        render_preview_stage()
    elif stage == "generating":
        render_generating_stage()
    elif stage == "done":
        render_done_stage()

# ══════════════════════════════════════════════════════════════
# 📦 侧边栏
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ✦ MOD 典藏库")
    st.caption("— Mod Archive —")

    if not st.session_state.generated_mods:
        st.markdown("""
        <p style="color:#4a3018;font-style:italic;font-size:0.83rem;
                  text-align:center;margin-top:14px;">
          典藏库空空如也……<br>
          <em>The archive awaits your creations...</em>
        </p>
        """, unsafe_allow_html=True)
    else:
        for mod in reversed(st.session_state.generated_mods):
            label = f"📜 {mod.get('name_cn') or mod['name']}"
            with st.expander(label):
                st.caption(f"{mod['date']}  ·  {mod['name']}")
                if mod.get("desc"):
                    st.caption(mod["desc"])
                if mod.get("image_url"):
                    st.image(mod["image_url"], width=120)
                z = make_zip(mod)
                st.download_button(
                    "⬇ 下载 MOD 包",
                    data=z,
                    file_name=f"{mod['name']}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key=f"dl_{mod['id']}"
                )
                if st.button("✦ 重新优化",
                             key=f"re_{mod['id']}", use_container_width=True):
                    st.session_state.mode  = "explore"
                    st.session_state.stage = "chat"
                    st.session_state.final_design = mod["design"]
                    st.session_state.messages = [
                        {"role":"user","content": mod.get("design","")}
                    ]
                    st.rerun()

    st.divider()
    st.caption(f"本次对话：{len(st.session_state.messages)} 条")
    st.caption(f"已生成 Mod：{len(st.session_state.generated_mods)} 个")
    st.divider()
    if st.button("🗑 清除全部记录", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
