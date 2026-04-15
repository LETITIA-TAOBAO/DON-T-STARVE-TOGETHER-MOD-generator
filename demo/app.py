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
# 📸 图片路径
# ========================
BASE_URL = "https://raw.githubusercontent.com/LETITIA-TAOBAO/DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
IMG = {
    "bg":       BASE_URL + "background.jpg.png",
    "rapid":    BASE_URL + "btn_play.png",
    "explore":  BASE_URL + "btn_explore.png",
    "generate": BASE_URL + "mod_generate.png",
    "card":     BASE_URL + "txt_box_bg.png",
}

# ========================
# 🎨 CSS
# ========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

/* ─ 背景 ─ */
.stApp {{
    background-image: url("{IMG['bg']}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}
.stApp::before {{
    content: "";
    position: fixed; top:0; left:0; width:100%; height:100%;
    z-index: -1;
    background: linear-gradient(rgba(20,15,10,0.62), rgba(10,6,2,0.80));
}}
html, body, [class*="css"],
.stAppViewContainer, .stAppViewBlockContainer,
.block-container, .st-emotion-cache-z5fcl4 {{
    background: transparent !important;
    background-color: transparent !important;
}}

/* ─ 字体 ─ */
h1,h2,h3 {{ font-family:'Creepster',cursive !important; color:#FFD700 !important; }}
p,li,label,div,span {{ font-family:'IM Fell English SC',serif !important; color:#F5E6C8 !important; }}

/* ─ Banner ─ */
.banner-box {{
    background: rgba(25,15,6,0.82);
    border: 3px solid #A67C3B;
    padding: 40px 50px;
    border-radius: 14px;
    text-align: center;
    margin: 20px auto 30px auto;
    max-width: 860px;
    box-shadow: 0 0 50px rgba(0,0,0,0.85);
}}

/* ─────────────────────────────────────────
   ⭐ 模式按钮：完全透明覆盖在图片上方
   ─────────────────────────────────────────
   原理：图片用 <img> 渲染，
   Streamlit 按钮用 CSS 让背景全透明，
   两者用同一列 col 包裹，按钮紧跟图片下方，
   通过负 margin-top 上移覆盖图片
*/
.mode-img {{
    display: block;
    width: 100%;
    max-width: 380px;
    margin: 0 auto 0 auto;
    filter: drop-shadow(0 8px 20px rgba(0,0,0,0.75));
    transition: transform 0.25s ease, filter 0.25s ease;
    cursor: pointer;
    pointer-events: none;   /* 点击穿透给按钮 */
}}

/* 把 Streamlit 按钮变成透明热区 */
div[data-testid="stButton"] > button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    color: transparent !important;
    width: 100% !important;
    height: 80px !important;
    margin-top: -90px !important;   /* 上移覆盖图片 */
    cursor: pointer !important;
    font-size: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stButton"] > button:hover ~ .mode-img,
div[data-testid="stButton"] > button:hover {{
    background: transparent !important;
}}
/* 图片悬停效果（用兄弟选择器无法做，改用 JS 或直接 filter） */

/* ─────────────────────────────────────────
   ⭐ 说明卡片（横排 + txt_box_bg 背景）
   ─────────────────────────────────────────*/
.cards-row {{
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 10px auto 40px auto;
    max-width: 1050px;
    padding: 0 20px;
    align-items: stretch;
}}
.card-item {{
    flex: 1;
    max-width: 470px;
    min-height: 260px;
    background-image: url("{IMG['card']}");
    background-size: 100% 100%;
    background-repeat: no-repeat;
    padding: 55px 38px 38px 38px;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.3s;
}}
.card-item:hover {{ transform: translateY(-5px); }}
.card-title {{
    font-family: 'Creepster', cursive !important;
    font-size: 1.55rem !important;
    margin-bottom: 12px !important;
}}
.card-rapid  .card-title {{ color: #ffaa60 !important; }}
.card-explore .card-title {{ color: #aadd88 !important; }}
.card-text {{
    font-size: 0.92rem !important;
    line-height: 1.85 !important;
    color: #cfc0a0 !important;
    margin: 0 !important;
}}
.card-en {{
    color: #99887a !important;
    font-size: 0.8em !important;
    font-style: italic !important;
    display: block !important;
    margin-top: 14px !important;
}}

/* ─ MOD 生成图片按钮（去透明格子） ─ */
.gen-img {{
    display: block;
    max-width: 420px;
    width: 65%;
    margin: 20px auto 0 auto;
    filter: drop-shadow(0 6px 16px rgba(0,0,0,0.8));
    /* drop-shadow 保留 PNG 透明通道，不产生白底 */
    transition: transform 0.25s, filter 0.25s;
    pointer-events: none;
}}
.gen-btn-wrap {{
    text-align: center;
    margin: 10px 0 2px 0;
}}
/* 透明覆盖按钮 */
.gen-btn-wrap div[data-testid="stButton"] > button {{
    margin-top: -70px !important;
    height: 70px !important;
    width: 65% !important;
    max-width: 420px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
}}

/* ─ 聊天消息 ─ */
.chat-user {{
    background: rgba(30,18,8,0.90);
    border-left: 4px solid #E8820C;
    padding: 12px 18px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}}
.chat-ai {{
    background: rgba(12,25,14,0.90);
    border-left: 4px solid #55AA60;
    padding: 12px 18px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}}
.chat-name {{
    font-family: 'Creepster', cursive !important;
    font-size: 1.05rem;
    display: block;
    margin-bottom: 5px;
}}

/* ─ 聊天输入框 ─ */
[data-testid="stChatInput"] textarea {{
    background: rgba(35,22,10,0.93) !important;
    border: 2px solid #7a3c10 !important;
    color: #F0E0C0 !important;
    font-family: 'IM Fell English SC', serif !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #E8820C !important;
}}

/* ─ 进度条 ─ */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, #8B4513, #FFD700) !important;
}}

/* ─ 侧边栏 ─ */
section[data-testid="stSidebar"] {{
    background: rgba(18,10,4,0.97) !important;
    border-right: 3px solid #6B3010 !important;
}}
section[data-testid="stSidebar"] * {{ color: #E8D8B8 !important; }}

/* ─ 滚动条 ─ */
::-webkit-scrollbar {{ width: 7px; }}
::-webkit-scrollbar-thumb {{ background: #7a3c10; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# ========================
# 🏴 Banner
# ========================
st.markdown("""
<div class="banner-box">
  <h1 style="font-size:3.2rem;margin:0;
             text-shadow:0 0 28px rgba(255,215,0,0.55);">饥荒 MOD 生成器</h1>
  <p style="font-family:Griffy,cursive;color:#a07830;
            font-size:1.3rem;letter-spacing:3px;margin-top:8px;">
    DON'T STARVE TOGETHER MOD GENERATOR
  </p>
  <hr style="width:44%;border:none;border-top:2px solid #7a5020;margin:16px auto;">
  <p style="line-height:1.85;font-size:1.05rem;max-width:750px;margin:0 auto;">
    当理智归零，现实崩塌。<br>
    <span style="color:#FFA726;text-shadow:0 0 10px rgba(255,167,38,0.45);">
      You are no longer a survivor, but a Creator.
    </span>
  </p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# ⭐ 主页 —— 关键修复：st.columns 保证按钮可点击
# ======================================================
if st.session_state.mode == "home":

    # ── 两个模式按钮 ──
    col_r, col_e = st.columns(2)

    with col_r:
        # 1. 先渲染图片
        st.markdown(f'<img class="mode-img" src="{IMG["rapid"]}" alt="快速生成">',
                    unsafe_allow_html=True)
        # 2. 透明按钮覆盖（margin-top 负值上移）
        if st.button("rapid", key="k_rapid", use_container_width=True):
            st.session_state.mode  = "rapid"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.generating = False
            st.rerun()

    with col_e:
        st.markdown(f'<img class="mode-img" src="{IMG["explore"]}" alt="探索设计">',
                    unsafe_allow_html=True)
        if st.button("explore", key="k_explore", use_container_width=True):
            st.session_state.mode  = "explore"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.generating = False
            st.rerun()

    # ── 说明卡片（横排，txt_box_bg 背景）──
    st.markdown(f"""
    <div class="cards-row">
      <div class="card-item card-rapid">
        <p class="card-title">🔥 意志铸剑者</p>
        <p class="card-text">
          当你已明晰 Mod 的核心法则与物品灵魂<br>
          无需徘徊于暗影之间<br>
          将你的疯狂构想直接锻造成可触及的现实
          <span class="card-en">For when your vision is clear. Forge it now.</span>
        </p>
      </div>
      <div class="card-item card-explore">
        <p class="card-title">👁️ 迷雾探路者</p>
        <p class="card-text">
          当灵感如迷雾般在你脑海中低语<br>
          混沌尚未凝聚成形<br>
          与暗影对话，在反复试探中让疯狂的蓝图逐渐清晰
          <span class="card-en">For when inspiration is foggy. Talk to the Shadow.</span>
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ========================
# 🔧 工具函数
# ========================
def safe_explore_llm(user_msg: str, history: list) -> str:
    """
    安全调用 explore_with_llm，
    自动检测函数接受 1 个还是 2 个参数。
    """
    import inspect
    try:
        params = inspect.signature(explore_with_llm).parameters
        if len(params) >= 2:
            raw = explore_with_llm(user_msg, history)
        else:
            raw = explore_with_llm(user_msg)
        if isinstance(raw, dict):
            return raw.get("text", str(raw))
        return str(raw)
    except Exception as exc:
        return f"（暗影沉默了：{exc}）"


def safe_design_llm(design: str, history: list) -> dict:
    import inspect
    try:
        params = inspect.signature(design_with_llm).parameters
        if len(params) >= 2:
            raw = design_with_llm(design, history)
        else:
            raw = design_with_llm(design)
        if isinstance(raw, dict):
            return raw
        return {"text": str(raw), "data": {}}
    except Exception as exc:
        return {"text": f"生成失败：{exc}", "data": {}}


def safe_optimize_prompt(design: str) -> str:
    try:
        raw = optimize_visual_prompt(design)
        if isinstance(raw, dict):
            return raw.get("optimized_prompt",
                   raw.get("fallback_prompt",
                   "don't starve together dark fantasy mod icon"))
        return str(raw)
    except Exception as exc:
        return "don't starve together dark fantasy mod icon"


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
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in mod.get("all_files", {}).items():
            zf.writestr(name,
                data.encode() if isinstance(data, str) else data)
        for d in ["sounds/", "images/", "animations/"]:
            zf.writestr(d, b"")
    buf.seek(0)
    return buf.getvalue()


def render_chat(messages: list):
    """渲染对话气泡"""
    for m in messages:
        if not isinstance(m, dict):
            continue
        if m["role"] == "user":
            st.markdown(
                f'<div class="chat-user">'
                f'<span class="chat-name" style="color:#E8820C;">⚔️ 求生者</span>'
                f'{m["content"]}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-ai">'
                f'<span class="chat-name" style="color:#55AA60;">🌑 暗影设计助手</span>'
                f'{m["content"]}</div>',
                unsafe_allow_html=True)

# ========================
# 🔄 生成 MOD 主流程
# ========================
def do_generate():
    st.markdown("""
    <div style="background:rgba(25,14,4,0.88);border:2px solid #7a3c10;
                border-radius:14px;padding:28px;text-align:center;
                margin:16px auto;max-width:660px;">
      <h2 style="font-family:Creepster,cursive;color:#FFD700;margin:0;font-size:2rem;">
        ⚙️ 世界正在扭曲……
      </h2>
      <p style="color:#aa9060;margin:10px 0 0 0;">
        The shadows are weaving your madness...
      </p>
    </div>""", unsafe_allow_html=True)

    bar = st.progress(0)

    with st.spinner("📝 Qwen 正在撰写 Mod 代码…"):
        bar.progress(15)
        result = safe_design_llm(st.session_state.final_design, st.session_state.messages)
    bar.progress(40)

    with st.spinner("🎨 优化图标描述词…"):
        img_prompt = safe_optimize_prompt(st.session_state.final_design)
    bar.progress(60)

    icon = {"ok": False, "err": "未执行"}
    with st.spinner("🖼️ 绘制 Mod 图标…"):
        icon = fetch_icon(img_prompt)
        if icon["ok"]:
            st.success("✅ 图标生成成功！")
            st.image(icon["url"], width=180, caption="MOD 图标预览")
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(icon["b64"])
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
        else:
            st.warning(f"⚠️ 图标生成失败：{icon['err']}")
    bar.progress(90)

    # 保存消息
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("text", "✅ Mod 已生成完毕！")
    })

    # 存档 Mod
    d = result.get("data", {})
    if d:
        st.session_state.generated_mods.append({
            "id":   len(st.session_state.generated_mods) + 1,
            "name": d.get("name", f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc": d.get("desc", ""),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "design":    st.session_state.final_design,
            "all_files": d.get("files", {}),
            "icon_ok":   icon["ok"],
        })

    bar.progress(100)
    st.session_state.generating = False
    st.session_state.mode = "done"
    st.rerun()

# ======================================================
# 💬 探索模式（多轮对话 → 确认 → 生成）
# ======================================================
if st.session_state.mode == "explore":

    st.markdown("""
    <div style="text-align:center;padding:14px 0 6px 0;">
      <h3 style="font-family:Creepster,cursive;color:#4CAF50;font-size:1.75rem;margin:0;">
        👁️ 迷雾探路者 · 探索设计模式
      </h3>
      <p style="color:#778866;font-size:0.88rem;margin-top:5px;">
        与暗影助手充分对话 → 设计确定后点击下方「MOD生成」按钮
      </p>
    </div>
    """, unsafe_allow_html=True)

    # 渲染历史对话
    render_chat(st.session_state.messages)

    # 用户输入
    user_inp = st.chat_input("描述你的想法，与暗影助手对话…")
    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("🌑 暗影低语中…"):
            reply = safe_explore_llm(user_inp, st.session_state.messages[:-1])
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # ── MOD 生成按钮（至少 1 轮对话后出现）──
    if len(st.session_state.messages) >= 2:
        # 图片装饰
        st.markdown(
            f'<div class="gen-btn-wrap">'
            f'<img class="gen-img" src="{IMG["generate"]}" alt="MOD生成">'
            f'</div>',
            unsafe_allow_html=True)
        # 真实可点击按钮
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🔨 确认生成 MOD", key="explore_gen", use_container_width=True):
                st.session_state.final_design = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.generating = True
                st.rerun()

    # 触发生成
    if st.session_state.generating:
        do_generate()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 返回主页", key="back_explore"):
        st.session_state.update(mode="home", messages=[], generating=False)
        st.rerun()

# ======================================================
# ⚡ 快速生成模式（多轮对话细化 → 确认 → 生成）
# ======================================================
elif st.session_state.mode == "rapid":

    st.markdown("""
    <div style="text-align:center;padding:14px 0 6px 0;">
      <h3 style="font-family:Creepster,cursive;color:#FFD700;font-size:1.75rem;margin:0;">
        🔥 意志铸剑者 · 快速生成模式
      </h3>
      <p style="color:#887744;font-size:0.88rem;margin-top:5px;">
        输入构想 → LLM 细化确认 → 点击「MOD生成」
      </p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages)

    user_inp = st.chat_input("输入你的 Mod 构想…")
    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("🌑 暗影正在解读…"):
            reply = safe_explore_llm(user_inp, st.session_state.messages[:-1])
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if len(st.session_state.messages) >= 2:
        st.markdown(
            f'<div class="gen-btn-wrap">'
            f'<img class="gen-img" src="{IMG["generate"]}" alt="MOD生成">'
            f'</div>',
            unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🔨 确认生成 MOD", key="rapid_gen", use_container_width=True):
                st.session_state.final_design = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.generating = True
                st.rerun()

    if st.session_state.generating:
        do_generate()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 返回主页", key="back_rapid"):
        st.session_state.update(mode="home", messages=[], generating=False)
        st.rerun()

# ======================================================
# ✅ 完成页
# ======================================================
elif st.session_state.mode == "done":

    st.markdown("""
    <div style="text-align:center;padding:30px 0 14px;">
      <h2 style="font-family:Creepster,cursive;color:#FFD700;font-size:2.4rem;margin:0;">
        ✨ MOD 铸造完成！
      </h2>
      <p style="color:#998866;margin-top:8px;">
        在侧边栏下载 ZIP，或继续对话优化。
      </p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages[-8:])

    ca, cb = st.columns(2)
    with ca:
        if st.button("🔄 继续优化", use_container_width=True, key="continue_explore"):
            st.session_state.mode = "explore"
            st.rerun()
    with cb:
        if st.button("🏠 返回主页", use_container_width=True, key="done_home"):
            st.session_state.update(mode="home", messages=[])
            st.rerun()

# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    if not st.session_state.generated_mods:
        st.caption("暂无 Mod 创作记录")
    else:
        for mod in reversed(st.session_state.generated_mods):
            with st.expander(f"📜 {mod['name']} · {mod['date']}"):
                st.caption(mod.get("desc", ""))
                z = make_zip(mod)
                st.download_button(
                    "💾 下载 ZIP",
                    data=z,
                    file_name=f"{mod['name'].replace(' ','_')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key=f"dl_{mod['id']}"
                )
                if st.button("🔄 重新优化", key=f"re_{mod['id']}", use_container_width=True):
                    st.session_state.mode = "explore"
                    st.session_state.final_design = mod["design"]
                    st.session_state.messages = [
                        {"role": "user", "content": mod["design"]}
                    ]
                    st.rerun()

    st.divider()
    st.caption(f"本次对话：{len(st.session_state.messages)} 条")
    st.divider()
    if st.button("🗑️ 清除全部", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
