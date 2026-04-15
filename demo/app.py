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
    from qwen_client import explore_with_llm, design_with_llm, optimize_visual_prompt
except ImportError as e:
    st.error(f"❌ 模块加载失败：{e}")
    st.stop()

# ========================
# 🔧 Session State
# ========================
for key, val in {
    "mode": "home",
    "messages": [],
    "generated_mods": [],
    "final_design": "",
    "generating": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========================
# 📸 背景图路径
# ========================
BASE_URL = "https://raw.githubusercontent.com/LETITIA-TAOBAO/DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
BG_URL = BASE_URL + "background.jpg.png"

# ========================
# 🎨 CSS —— 全部重构
# ========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC:ital@0;1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');

/* ══════════════════════════════════════
   背景
══════════════════════════════════════ */
.stApp {{
    background-image: url("{BG_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* 全局半透明遮罩，让文字可读但背景可见 */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(8, 4, 0, 0.45);
    z-index: 0;
    pointer-events: none;
}}

/* 主内容区微透明深棕 */
.stAppViewContainer .stMainBlockContainer,
.block-container {{
    background: rgba(20, 11, 3, 0.55) !important;
    backdrop-filter: blur(2px);
    border-left: 1px solid rgba(180,130,40,0.15);
    border-right: 1px solid rgba(180,130,40,0.15);
}}

/* 侧边栏 —— 与背景同色调但半透明 */
section[data-testid="stSidebar"] {{
    background: rgba(15, 8, 2, 0.70) !important;
    border-right: 2px solid rgba(160, 100, 30, 0.40) !important;
    backdrop-filter: blur(4px);
}}
section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

/* ══════════════════════════════════════
   全局字体与颜色
══════════════════════════════════════ */
html, body, [class*="css"] {{
    background-color: transparent !important;
}}

h1, h2, h3 {{
    font-family: 'Cinzel Decorative', serif !important;
    color: #D4A843 !important;
    text-shadow: 0 0 20px rgba(200,160,60,0.45), 2px 2px 4px rgba(0,0,0,0.8) !important;
    letter-spacing: 2px !important;
}}

p, span, div, label, li {{
    font-family: 'IM Fell English SC', serif !important;
    color: #EDD9A3 !important;
}}

/* ══════════════════════════════════════
   Banner
══════════════════════════════════════ */
.dst-banner {{
    background: rgba(15, 8, 2, 0.78);
    border: 2px solid #8B6420;
    border-top: 3px solid #C8A84B;
    border-bottom: 3px solid #C8A84B;
    padding: 40px 50px 36px;
    border-radius: 4px;
    text-align: center;
    margin: 10px auto 32px auto;
    max-width: 820px;
    box-shadow:
        0 0 60px rgba(0,0,0,0.7),
        inset 0 0 30px rgba(0,0,0,0.4),
        0 0 0 4px rgba(100,60,10,0.3);
    position: relative;
}}
.dst-banner::before, .dst-banner::after {{
    content: "✦";
    position: absolute;
    top: 12px;
    color: #8B6420;
    font-size: 1.2rem;
}}
.dst-banner::before {{ left: 18px; }}
.dst-banner::after  {{ right: 18px; }}
.dst-banner .banner-sub {{
    font-family: 'Cinzel', serif !important;
    color: #8B6420 !important;
    font-size: 0.82rem;
    letter-spacing: 4px;
    margin-top: 6px;
}}
.dst-banner .banner-divider {{
    width: 40%;
    border: none;
    border-top: 1px solid #6B4A18;
    margin: 18px auto;
}}
.dst-banner .banner-quote {{
    font-family: 'IM Fell English SC', serif !important;
    font-size: 1rem;
    line-height: 1.9;
    color: #C8A86A !important;
    font-style: italic;
}}

/* ══════════════════════════════════════
   ⭐ 模式选择卡片（替代图片按钮）
══════════════════════════════════════ */
.mode-cards {{
    display: flex;
    gap: 28px;
    justify-content: center;
    margin: 0 auto 36px auto;
    max-width: 900px;
}}

.mode-card {{
    flex: 1;
    max-width: 420px;
    background: rgba(18, 10, 3, 0.82);
    border: 2px solid #6B4A18;
    border-radius: 6px;
    padding: 28px 24px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}}
.mode-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #C8A84B, transparent);
}}
.mode-card:hover {{
    border-color: #C8A84B;
    background: rgba(35, 18, 5, 0.90);
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.65), 0 0 20px rgba(200,168,75,0.15);
}}

.mode-card-icon {{
    font-size: 2.4rem;
    margin-bottom: 10px;
    display: block;
}}
.mode-card-title {{
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 1.15rem !important;
    color: #D4A843 !important;
    margin: 0 0 6px 0 !important;
    letter-spacing: 1px;
}}
.mode-card-sub {{
    font-family: 'Cinzel', serif !important;
    font-size: 0.72rem !important;
    color: #7a5a28 !important;
    letter-spacing: 3px;
    margin-bottom: 14px !important;
    display: block;
}}
.mode-card-divider {{
    border: none;
    border-top: 1px solid #4a3010;
    margin: 12px auto;
    width: 60%;
}}
.mode-card-desc {{
    font-size: 0.88rem !important;
    line-height: 1.85 !important;
    color: #B89A62 !important;
    margin: 0 !important;
}}
.mode-card-en {{
    font-style: italic !important;
    color: #6a5030 !important;
    font-size: 0.78em !important;
    display: block !important;
    margin-top: 12px !important;
}}
.mode-card-btn-hint {{
    display: inline-block;
    margin-top: 18px;
    padding: 6px 20px;
    border: 1px solid #8B6420;
    border-radius: 3px;
    font-family: 'IM Fell English SC', serif !important;
    font-size: 0.82rem !important;
    color: #C8A84B !important;
    background: rgba(100,60,10,0.20);
    letter-spacing: 1px;
}}

/* ══════════════════════════════════════
   ⭐ Streamlit 按钮 —— 饥荒风格
══════════════════════════════════════ */
div[data-testid="stButton"] > button {{
    background: rgba(20, 10, 3, 0.85) !important;
    border: 2px solid #7a5020 !important;
    color: #D4A843 !important;
    font-family: 'IM Fell English SC', serif !important;
    font-size: 1rem !important;
    letter-spacing: 1px !important;
    padding: 10px 24px !important;
    border-radius: 4px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
    text-shadow: 0 0 8px rgba(200,160,60,0.4) !important;
    position: relative !important;
}}
div[data-testid="stButton"] > button:hover {{
    background: rgba(50, 25, 5, 0.95) !important;
    border-color: #C8A84B !important;
    color: #FFD700 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.6), 0 0 15px rgba(200,168,75,0.2) !important;
}}
div[data-testid="stButton"] > button:active {{
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5) !important;
}}

/* 特殊：生成MOD 大按钮 */
.gen-btn div[data-testid="stButton"] > button {{
    background: rgba(60, 25, 5, 0.90) !important;
    border: 2px solid #C8A84B !important;
    font-size: 1.1rem !important;
    padding: 14px 32px !important;
    letter-spacing: 2px !important;
    width: 100% !important;
}}
.gen-btn div[data-testid="stButton"] > button:hover {{
    background: rgba(90, 40, 8, 0.95) !important;
    box-shadow: 0 0 30px rgba(200,168,75,0.30), 0 6px 20px rgba(0,0,0,0.6) !important;
}}

/* ══════════════════════════════════════
   模式页面 Header
══════════════════════════════════════ */
.mode-header {{
    background: rgba(12, 6, 1, 0.75);
    border: 1px solid #5a3810;
    border-top: 3px solid #9B7830;
    border-radius: 4px;
    padding: 22px 30px 18px;
    text-align: center;
    margin-bottom: 20px;
}}
.mode-header h3 {{
    font-size: 1.6rem !important;
    margin: 0 0 6px 0 !important;
}}
.mode-header p {{
    font-size: 0.88rem !important;
    color: #8a7050 !important;
    margin: 0 !important;
}}

/* ══════════════════════════════════════
   聊天气泡
══════════════════════════════════════ */
.chat-user {{
    background: rgba(25, 14, 4, 0.88);
    border-left: 3px solid #C8820C;
    border-bottom: 1px solid rgba(200,130,12,0.20);
    padding: 12px 16px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
}}
.chat-ai {{
    background: rgba(8, 20, 10, 0.88);
    border-left: 3px solid #4A9A50;
    border-bottom: 1px solid rgba(74,154,80,0.20);
    padding: 12px 16px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
}}
.chat-name {{
    font-family: 'Cinzel', serif !important;
    font-size: 0.82rem !important;
    letter-spacing: 2px !important;
    display: block;
    margin-bottom: 6px;
}}
.chat-content {{
    font-family: 'IM Fell English SC', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
    color: #D4BC88 !important;
    white-space: pre-wrap;
}}

/* ══════════════════════════════════════
   生成进度区
══════════════════════════════════════ */
.gen-progress-box {{
    background: rgba(12, 6, 1, 0.88);
    border: 2px solid #7a4010;
    border-top: 3px solid #C8A84B;
    border-radius: 6px;
    padding: 32px;
    text-align: center;
    margin: 16px auto;
    max-width: 620px;
}}

/* ══════════════════════════════════════
   分隔线
══════════════════════════════════════ */
hr {{
    border: none !important;
    border-top: 1px solid rgba(139,100,32,0.35) !important;
    margin: 20px 0 !important;
}}

/* ══════════════════════════════════════
   聊天输入框
══════════════════════════════════════ */
[data-testid="stChatInput"] {{
    background: rgba(15, 8, 2, 0.80) !important;
    border-top: 1px solid rgba(139,100,32,0.40) !important;
}}
[data-testid="stChatInput"] textarea {{
    background: rgba(20, 11, 3, 0.90) !important;
    border: 1px solid #5a3810 !important;
    color: #EDD9A3 !important;
    font-family: 'IM Fell English SC', serif !important;
    border-radius: 4px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #C8A84B !important;
    outline: none !important;
    box-shadow: 0 0 10px rgba(200,168,75,0.20) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: #6a5030 !important;
    font-style: italic !important;
}}

/* ── 进度条 ─ */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, #6B3A08, #C8A84B, #F0D070) !important;
    border-radius: 4px !important;
}}

/* ── 侧边栏文字 ─ */
section[data-testid="stSidebar"] * {{
    color: #C8A868 !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: #D4A843 !important;
}}

/* ── expander ─ */
.st-expander {{
    background: rgba(20,11,3,0.70) !important;
    border: 1px solid #5a3810 !important;
    border-radius: 4px !important;
}}

/* ── 滚动条 ─ */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: rgba(10,5,0,0.3); }}
::-webkit-scrollbar-thumb {{ background: #5a3810; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: #8B6420; }}

/* ── success / warning / info ─ */
.stSuccess {{ background: rgba(10,30,12,0.80) !important; border-color: #4A9A50 !important; }}
.stWarning {{ background: rgba(30,18,4,0.80) !important; border-color: #C8820C !important; }}
</style>
""", unsafe_allow_html=True)


# ========================
# 🔧 工具函数
# ========================
def generate_atlas_xml() -> str:
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
  <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''

def fetch_icon(prompt: str) -> dict:
    try:
        enc = prompt.replace(" ", "+").replace("&", "%26")
        url = (f"https://image.pollinations.ai/prompt/{enc}"
               f"?width=512&height=512&nologo=true"
               f"&seed={int(datetime.now().timestamp())}")
        r = requests.get(url, timeout=50)
        if r.status_code == 200 and len(r.content) > 1000:
            return {"ok": True, "b64": base64.b64encode(r.content).decode(), "url": url}
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as exc:
        return {"ok": False, "err": str(exc)}

def make_zip(mod: dict) -> bytes:
    buf = io.BytesIO()
    install_txt = """══════════════════════════════
   饥荒联机版 MOD 安装指南
══════════════════════════════

① 将本文件夹整体复制到：
   Steam/steamapps/common/
   Don't Starve Together/mods/

② 启动游戏 → 主菜单 → 模组
   → 找到本 Mod → 启用

③ 创建或进入存档，Mod 即刻生效。

如遇问题请检查 modinfo.lua 中的
api_version 是否为 10。
══════════════════════════════
"""
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in mod.get("all_files", {}).items():
            zf.writestr(name, data.encode() if isinstance(data, str) else data)
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
                f'</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-ai">'
                f'<span class="chat-name" style="color:#4A9A50;">✦ SHADOW ARCHITECT</span>'
                f'<span class="chat-content">{m["content"]}</span>'
                f'</div>',
                unsafe_allow_html=True)

# ========================
# 🔄 MOD 生成主流程
# ========================
def do_generate():
    st.markdown("""
    <div class="gen-progress-box">
      <h2 style="font-size:1.8rem;margin:0 0 8px 0;">⚙ The World Bends...</h2>
      <p style="color:#8a7050;font-size:0.88rem;margin:0;font-style:italic;">
        混沌正在凝固成形，稍候片刻……
      </p>
    </div>""", unsafe_allow_html=True)

    bar = st.progress(0)

    with st.spinner("✦ 暗影法典正在书写代码……"):
        bar.progress(15)
        try:
            result = design_with_llm(
                st.session_state.final_design,
                st.session_state.messages
            )
        except Exception as e:
            result = {"text": f"铸造失败：{e}", "data": {}}
    bar.progress(40)

    with st.spinner("✦ 优化图腾描述……"):
        try:
            vis = optimize_visual_prompt(st.session_state.final_design)
            img_prompt = vis.get("optimized_prompt",
                        vis.get("fallback_prompt",
                        "Don't Starve Together dark fantasy mod icon"))
        except Exception:
            img_prompt = "Don't Starve Together dark fantasy mod icon"
    bar.progress(60)

    icon = {"ok": False, "err": "未执行"}
    with st.spinner("✦ 召唤图腾形象……"):
        icon = fetch_icon(img_prompt)
        if icon["ok"]:
            st.success("✦ 图腾形象已凝聚！")
            st.image(icon["url"], width=180, caption="MOD 图标")
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(icon["b64"])
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
        else:
            st.warning(f"图腾形象召唤失败：{icon['err']}")
    bar.progress(90)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("text", "✦ Mod 铸造完毕。")
    })

    d = result.get("data", {})
    if d:
        st.session_state.generated_mods.append({
            "id":        len(st.session_state.generated_mods) + 1,
            "name":      d.get("name", f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc":      d.get("desc", ""),
            "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
            "design":    st.session_state.final_design,
            "all_files": d.get("files", {}),
            "icon_ok":   icon["ok"],
        })

    bar.progress(100)
    st.session_state.generating = False
    st.session_state.mode = "done"
    st.rerun()


# ======================================================
# 🏠 主页
# ======================================================
if st.session_state.mode == "home":

    # Banner
    st.markdown("""
    <div class="dst-banner">
      <h1 style="font-size:2.8rem;margin:0;">饥荒 MOD 生成器</h1>
      <p class="banner-sub">DON'T STARVE TOGETHER · MOD GENERATOR</p>
      <hr class="banner-divider">
      <p class="banner-quote">
        当理智归零，现实崩塌。<br>
        <em>You are no longer a survivor — but a Creator.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)

    # 两个模式卡片（HTML展示）
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
          <span class="mode-card-en">For when your vision is clear. Forge it now.</span>
        </p>
        <span class="mode-card-btn-hint">点击下方按钮进入 ↓</span>
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
          <span class="mode-card-en">For when inspiration is foggy. Talk to the Shadow.</span>
        </p>
        <span class="mode-card-btn-hint">点击下方按钮进入 ↓</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 真实可点击按钮（在卡片正下方）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ 快速生成 · Rapid Forge", key="k_rapid", use_container_width=True):
            st.session_state.mode = "rapid"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.generating = False
            st.rerun()
    with col2:
        if st.button("👁 探索设计 · Shadow Explore", key="k_explore", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.generating = False
            st.rerun()


# ======================================================
# 👁 探索模式
# ======================================================
elif st.session_state.mode == "explore":

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#4CAF50 !important;">👁 迷雾探路者 · Shadow Explore</h3>
      <p>与暗影助手充分对话，设计确定后点击「铸造 MOD」</p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages)

    user_inp = st.chat_input("低语你的构想，暗影将倾听……")
    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("✦ 暗影正在低语……"):
            try:
                r = explore_with_llm(st.session_state.messages)
                reply = r.get("text", str(r)) if isinstance(r, dict) else str(r)
            except Exception as exc:
                reply = f"（暗影沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # MOD 生成按钮
    if len(st.session_state.messages) >= 2 and not st.session_state.generating:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align:center;font-size:0.85rem;color:#6a5030;
                  font-style:italic;margin-bottom:8px;letter-spacing:1px;">
          ✦ 当设计已足够清晰，令混沌凝固成形 ✦
        </p>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
            if st.button("⚙ 铸造 MOD · Forge the Mod", key="explore_gen", use_container_width=True):
                st.session_state.final_design = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.generating = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.generating:
        do_generate()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 归返主页 · Return", key="back_explore"):
        st.session_state.update(mode="home", messages=[], generating=False)
        st.rerun()


# ======================================================
# ⚡ 快速生成模式
# ======================================================
elif st.session_state.mode == "rapid":

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#D4A843 !important;">⚡ 意志铸剑者 · Rapid Forge</h3>
      <p>输入你的构想，暗影助手将细化设计，确认后点击「铸造 MOD」</p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages)

    user_inp = st.chat_input("将你的意志化为文字……")
    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("✦ 暗影正在解读你的意志……"):
            try:
                r = explore_with_llm(st.session_state.messages)
                reply = r.get("text", str(r)) if isinstance(r, dict) else str(r)
            except Exception as exc:
                reply = f"（暗影沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if len(st.session_state.messages) >= 2 and not st.session_state.generating:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align:center;font-size:0.85rem;color:#6a5030;
                  font-style:italic;margin-bottom:8px;letter-spacing:1px;">
          ✦ 当你的意志已足够坚定，令现实俯首 ✦
        </p>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
            if st.button("⚙ 铸造 MOD · Forge the Mod", key="rapid_gen", use_container_width=True):
                st.session_state.final_design = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.generating = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.generating:
        do_generate()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 归返主页 · Return", key="back_rapid"):
        st.session_state.update(mode="home", messages=[], generating=False)
        st.rerun()


# ======================================================
# ✅ 完成页
# ======================================================
elif st.session_state.mode == "done":

    st.markdown("""
    <div class="dst-banner">
      <h2 style="font-size:2rem;margin:0;">✨ MOD 已铸造完成</h2>
      <p class="banner-sub">THE MOD HAS BEEN FORGED</p>
      <hr class="banner-divider">
      <p class="banner-quote">
        混沌已凝固，你的疯狂已成为现实。<br>
        <em>Your madness has taken form. Download it from the sidebar.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages[-8:])

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        if st.button("✦ 继续雕琢 · Refine", use_container_width=True, key="continue_explore"):
            st.session_state.mode = "explore"
            st.rerun()
    with cb:
        if st.button("← 归返主页 · Return", use_container_width=True, key="done_home"):
            st.session_state.update(mode="home", messages=[])
            st.rerun()


# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("### ✦ MOD 典藏库")
    st.caption("— Mod Archive —")

    if not st.session_state.generated_mods:
        st.markdown("""
        <p style="color:#5a4020;font-style:italic;font-size:0.85rem;text-align:center;margin-top:16px;">
          典藏库空空如也<br>
          <em>The archive awaits your creations...</em>
        </p>
        """, unsafe_allow_html=True)
    else:
        for mod in reversed(st.session_state.generated_mods):
            with st.expander(f"📜 {mod['name']}"):
                st.caption(f"{mod['date']}")
                if mod.get("desc"):
                    st.caption(mod["desc"])
                z = make_zip(mod)
                st.download_button(
                    "⬇ 下载 MOD 包",
                    data=z,
                    file_name=f"{mod['name'].replace(' ','_')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key=f"dl_{mod['id']}"
                )
                if st.button("✦ 重新优化", key=f"re_{mod['id']}", use_container_width=True):
                    st.session_state.mode = "explore"
                    st.session_state.final_design = mod["design"]
                    st.session_state.messages = [{"role":"user","content":mod["design"]}]
                    st.rerun()

    st.divider()
    st.caption(f"本次对话：{len(st.session_state.messages)} 条")
    st.caption(f"已生成 Mod：{len(st.session_state.generated_mods)} 个")
    st.divider()
    if st.button("🗑 清除全部记录", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
