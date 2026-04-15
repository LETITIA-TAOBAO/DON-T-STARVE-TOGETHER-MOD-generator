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
    "explore_confirmed": False,   # 是否已点击"MOD生成"确认生成
    "generating": False,           # 是否正在生成中
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
# 🎨 全局 CSS
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
    min-height: 100vh;
}}
html, body, [class*="css"] {{ background-color: transparent !important; }}
.stApp::before {{
    content: "";
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    background: linear-gradient(rgba(20,15,10,0.65), rgba(15,10,5,0.82));
}}

/* ── 字体 ── */
h1,h2,h3 {{ font-family:'Creepster' !important; color:#FFD700 !important; }}
p,span,div,label {{ font-family:'IM Fell English SC' !important; color:#F5E6C8 !important; }}

/* ── Banner ── */
.banner-box {{
    background: rgba(30,20,10,0.78);
    border: 3px solid #A67C3B;
    padding: 40px;
    border-radius: 12px;
    text-align: center;
    margin: 30px auto;
    max-width: 900px;
    box-shadow: 0 0 40px rgba(0,0,0,0.8);
}}

/* ══════════════════════════════════════
   ⭐ 模式选择区：两个图片按钮并排
   ══════════════════════════════════════ */
.mode-select-wrapper {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 60px;
    margin: 40px auto 10px auto;
    max-width: 1100px;
}}

/* 每个按钮组（图片按钮 + 说明卡片纵向堆叠） */
.mode-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0px;
    flex: 1;
    max-width: 460px;
}}

/* 图片按钮容器（覆盖 Streamlit 原生按钮） */
.img-btn-wrap {{
    width: 100%;
    position: relative;
    cursor: pointer;
}}
.img-btn-wrap img {{
    width: 100%;
    max-width: 420px;
    height: auto;
    display: block;
    margin: 0 auto;
    transition: transform 0.25s ease, filter 0.25s ease;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.7));
}}
.img-btn-wrap img:hover {{
    transform: scale(1.06) translateY(-4px);
    filter: drop-shadow(0 12px 28px rgba(0,0,0,0.85)) brightness(1.15);
}}

/* ══════════════════════════════════════
   ⭐ 说明卡片：横排两个，用 txt_box_bg.png
   ══════════════════════════════════════ */
.cards-row {{
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 60px;
    margin: 0 auto 40px auto;
    max-width: 1100px;
    padding: 0 20px;
}}

.card-item {{
    flex: 1;
    max-width: 460px;
    min-height: 200px;
    background-image: url("{IMAGES['card_bg']}");
    background-size: 100% 100%;
    background-repeat: no-repeat;
    background-position: center;
    padding: 40px 36px 36px 36px;
    border-radius: 10px;
    text-align: center;
    transition: transform 0.3s ease;
}}
.card-item:hover {{
    transform: translateY(-4px);
}}
.card-title {{
    font-family: Creepster !important;
    font-size: 1.5rem !important;
    margin-bottom: 12px !important;
    text-shadow: 0 0 8px rgba(255,215,0,0.4);
}}
.card-rapid .card-title  {{ color: #ffaa60 !important; }}
.card-explore .card-title {{ color: #aadd88 !important; }}
.card-text {{
    font-family: "IM Fell English SC" !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
    color: #d4c4a0 !important;
}}
.card-en {{
    color: #998877 !important;
    font-size: 0.82em !important;
    font-style: italic !important;
    display: block !important;
    margin-top: 10px !important;
}}

/* ── 隐藏原生 Streamlit 按钮（用图片覆盖点击） ── */
.stButton > button {{
    opacity: 0 !important;
    position: absolute !important;
    width: 100% !important;
    height: 100% !important;
    top: 0 !important; left: 0 !important;
    cursor: pointer !important;
    z-index: 10 !important;
}}

/* MOD生成大按钮区 */
.gen-btn-wrap {{
    display: flex;
    justify-content: center;
    margin: 30px auto;
}}
.gen-btn-wrap img {{
    max-width: 480px;
    width: 80%;
    height: auto;
    cursor: pointer;
    transition: transform 0.25s, filter 0.25s;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.7));
}}
.gen-btn-wrap img:hover {{
    transform: scale(1.06) translateY(-4px);
    filter: brightness(1.2) drop-shadow(0 10px 24px rgba(0,0,0,0.85));
}}

/* ── 聊天消息 ── */
.chat-msg {{
    background: rgba(30,20,10,0.88);
    border-left: 4px solid #FF8C00;
    padding: 14px 18px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
}}
.chat-msg.assistant {{
    background: rgba(18,28,18,0.88);
    border-left-color: #66BB6A;
}}
.chat-name {{ font-family: Creepster !important; font-size: 1.05rem; }}

/* ── 侧边栏 ── */
section[data-testid="stSidebar"] {{
    background: rgba(25,15,8,0.98) !important;
    border-right: 4px solid #8B4513 !important;
}}
section[data-testid="stSidebar"] * {{ color: #F5E6C8 !important; }}

/* ── 聊天输入 ── */
[data-testid="stChatInput"] textarea {{
    background-color: rgba(40,30,20,0.92) !important;
    border: 3px solid #8B4513 !important;
    color: #F5E6C8 !important;
    font-family: 'IM Fell English SC' !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #FFA726 !important;
}}

/* 进度区 */
.gen-progress {{
    background: rgba(30,20,10,0.85);
    border: 2px solid #8B4513;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    margin: 30px auto;
    max-width: 700px;
}}

::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-thumb {{ background: #8B4513; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# ========================
# 🏴 Banner
# ========================
st.markdown("""
<div class="banner-box">
  <h1 style="font-size:3.2rem;margin:0;text-shadow:0 0 25px rgba(255,215,0,0.55);">饥荒 MOD 生成器</h1>
  <p style="font-family:Griffy;color:#aa8855;font-size:1.3rem;letter-spacing:3px;margin-top:8px;">
    DON'T STARVE TOGETHER MOD GENERATOR
  </p>
  <hr style="width:45%;border:none;border-top:2px solid #8B4513;margin:18px auto;">
  <p style="line-height:1.8;font-size:1.05rem;max-width:780px;margin:0 auto;">
    当理智归零，现实崩塌。<br>
    <span style="color:#FFA726;text-shadow:0 0 10px rgba(255,167,38,0.5);">
      You are no longer a survivor, but a Creator.
    </span>
  </p>
</div>
""", unsafe_allow_html=True)

# ========================
# ⭐ 主页：两个模式按钮（图片）+ 横排说明卡片
# ========================
if st.session_state.mode == "home":

    # —— 图片按钮行（用 st.columns 保证点击有效）——
    st.markdown('<div style="max-width:1100px;margin:40px auto 0 auto;">', unsafe_allow_html=True)
    col1, col_gap, col2 = st.columns([5, 1, 5])

    with col1:
        # 显示图片
        st.markdown(f"""
        <div class="img-btn-wrap">
          <img src="{IMAGES['btn_rapid']}" alt="快速生成">
        </div>
        """, unsafe_allow_html=True)
        # 透明原生按钮叠在图片上
        st.markdown('<div style="position:relative;height:0px;top:-80px;">', unsafe_allow_html=True)
        if st.button("快速生成", key="btn_rapid_click", use_container_width=True):
            st.session_state.mode = "rapid"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.explore_confirmed = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="img-btn-wrap">
          <img src="{IMAGES['btn_explore']}" alt="探索设计">
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="position:relative;height:0px;top:-80px;">', unsafe_allow_html=True)
        if st.button("探索设计", key="btn_explore_click", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.session_state.explore_confirmed = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # —— 横排说明卡片 ——
    st.markdown(f"""
    <div class="cards-row" style="margin-top:10px;">
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
def generate_atlas_xml():
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
  <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''

def generate_icon_with_pollinations(prompt: str) -> dict:
    try:
        if not prompt or len(prompt) < 5:
            return {"success": False, "error": "Prompt 太短"}
        encoded = prompt.replace(" ", "+").replace("&", "%26")
        url = (f"https://image.pollinations.ai/prompt/{encoded}"
               f"?width=512&height=512&nologo=true&seed={int(datetime.now().timestamp())}")
        resp = requests.get(url, timeout=50)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return {"success": True,
                    "base64": base64.b64encode(resp.content).decode(),
                    "url": url}
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}

def create_mod_zip(mod_data: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in mod_data.get("all_files", {}).items():
            if isinstance(content, str):
                zf.writestr(name, content.encode("utf-8"))
            elif isinstance(content, bytes):
                zf.writestr(name, content)
        for d in ["sounds/", "images/", "animations/"]:
            zf.writestr(d, "")
    buf.seek(0)
    return buf.getvalue()

# ========================
# 🔄 实际生成 MOD 的逻辑（只在确认后调用）
# ========================
def do_generate_mod():
    """执行 MOD 生成全流程，结果写入 session_state"""
    st.markdown("""
    <div class="gen-progress">
      <h2 style="font-family:Creepster;font-size:2.2rem;color:#FFD700;">世界正在扭曲……</h2>
      <p>The shadows are weaving your madness...</p>
    </div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)

    # Step 1: 生成代码
    with st.spinner("📝 Qwen 正在生成 Mod 代码…"):
        progress_bar.progress(20)
        result = design_with_llm(st.session_state.final_design, st.session_state.messages)

    # Step 2: 优化图标 prompt
    with st.spinner("🎨 正在优化图标提示词…"):
        progress_bar.progress(50)
        visual_result = optimize_visual_prompt(st.session_state.final_design)
        image_prompt = visual_result.get("optimized_prompt",
                       visual_result.get("fallback_prompt", "don't starve together mod icon"))

    # Step 3: 生成图标
    icon_result = {"success": False, "error": "未执行"}
    with st.spinner("🖼️ Pollinations.ai 正在绘制图标…"):
        progress_bar.progress(75)
        icon_result = generate_icon_with_pollinations(image_prompt)
        if icon_result["success"]:
            st.success("✅ 图标生成成功！")
            st.image(icon_result["url"], caption="生成的图标预览", width=200)
            if "files" not in result.get("data", {}):
                result.setdefault("data", {})["files"] = {}
            result["data"]["files"]["modicon.tex"] = base64.b64decode(icon_result["base64"])
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
        else:
            st.warning(f"⚠️ 图标生成失败：{icon_result['error']}")

    progress_bar.progress(100)

    # 保存 assistant 回复
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("text", "Mod 已生成完毕。")
    })

    # 记录 mod
    mod_data = result.get("data", {})
    if mod_data:
        st.session_state.generated_mods.append({
            "id": len(st.session_state.generated_mods) + 1,
            "name": mod_data.get("name", f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc": mod_data.get("desc", ""),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "design": st.session_state.final_design,
            "all_files": mod_data.get("files", {}),
            "icon_generated": icon_result["success"],
        })

    # 重置生成标志，回到 explore/rapid 界面展示结果
    st.session_state.generating = False
    st.session_state.explore_confirmed = False
    st.session_state.mode = "done"
    st.rerun()

# ========================
# 💬 探索模式（多轮对话）
# ========================
if st.session_state.mode == "explore":

    st.markdown("""
    <div style="text-align:center;padding:12px 0 4px 0;">
      <h3 style="font-family:Creepster;color:#4CAF50;font-size:1.8rem;">
        👁️ 迷雾探路者 · 探索设计模式
      </h3>
      <p style="color:#aaa;font-size:0.95rem;">
        与暗影助手充分对话，确认设计后点击「MOD生成」按钮
      </p>
    </div>
    """, unsafe_allow_html=True)

    # —— 展示历史对话 ——
    for msg in st.session_state.messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        css_cls = "chat-msg" if role == "user" else "chat-msg assistant"
        color    = "#FF8C00"  if role == "user" else "#66BB6A"
        name     = "求生者"   if role == "user" else "暗影设计助手"
        st.markdown(
            f'<div class="{css_cls}">'
            f'<span class="chat-name" style="color:{color};">{name}</span><br>{content}'
            f'</div>',
            unsafe_allow_html=True
        )

    # —— 用户输入框 ——
    user_input = st.chat_input("描述你的想法，与暗影助手对话…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # 调用 LLM 探索对话
        with st.spinner("暗影低语中…"):
            try:
                reply = explore_with_llm(user_input, st.session_state.messages[:-1])
                reply_text = reply.get("text", reply) if isinstance(reply, dict) else str(reply)
            except Exception as exc:
                reply_text = f"（暗影沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

    # —— MOD生成 按钮（只有对话至少一轮才显示）——
    if len(st.session_state.messages) >= 2:
        st.markdown('<div class="gen-btn-wrap">', unsafe_allow_html=True)
        st.markdown(f'<img src="{IMAGES["btn_generate"]}" alt="MOD生成" id="gen-img">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 真实可点击的 Streamlit 按钮（样式透明，叠在图片下方）
        col_l, col_c, col_r = st.columns([2, 3, 2])
        with col_c:
            if st.button("🔨 确认生成 MOD", key="explore_gen_btn", use_container_width=True):
                # 汇总对话作为 final_design
                summary = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.final_design = summary
                st.session_state.generating = True
                st.rerun()

    # —— 如果已触发生成 ——
    if st.session_state.generating:
        do_generate_mod()

    # —— 返回主页 ——
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 返回主页", key="back_from_explore"):
        st.session_state.mode = "home"
        st.session_state.messages = []
        st.rerun()

# ========================
# ⚡ 快速生成模式（单次输入 → 明确设计 → 点按钮生成）
# ========================
elif st.session_state.mode == "rapid":

    st.markdown("""
    <div style="text-align:center;padding:12px 0 4px 0;">
      <h3 style="font-family:Creepster;color:#FFD700;font-size:1.8rem;">
        🔥 意志铸剑者 · 快速生成模式
      </h3>
      <p style="color:#aaa;font-size:0.95rem;">
        输入你完整的 Mod 构想，LLM 将帮你细化方案。确认后点击「MOD生成」。
      </p>
    </div>
    """, unsafe_allow_html=True)

    # —— 展示历史对话 ——
    for msg in st.session_state.messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        css_cls = "chat-msg" if role == "user" else "chat-msg assistant"
        color    = "#FF8C00"  if role == "user" else "#66BB6A"
        name     = "求生者"   if role == "user" else "暗影设计助手"
        st.markdown(
            f'<div class="{css_cls}">'
            f'<span class="chat-name" style="color:{color};">{name}</span><br>{content}'
            f'</div>',
            unsafe_allow_html=True
        )

    # —— 输入框 ——
    user_input = st.chat_input("输入你的完整 Mod 构想…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # 快速模式同样调用一轮 LLM 帮助细化/确认设计
        with st.spinner("暗影正在解读你的构想…"):
            try:
                reply = explore_with_llm(user_input, st.session_state.messages[:-1])
                reply_text = reply.get("text", reply) if isinstance(reply, dict) else str(reply)
            except Exception as exc:
                reply_text = f"（暗影沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

    # —— MOD生成 按钮 ——
    if len(st.session_state.messages) >= 2:
        st.markdown('<div class="gen-btn-wrap">', unsafe_allow_html=True)
        st.markdown(f'<img src="{IMAGES["btn_generate"]}" alt="MOD生成">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([2, 3, 2])
        with col_c:
            if st.button("🔨 确认生成 MOD", key="rapid_gen_btn", use_container_width=True):
                summary = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.final_design = summary
                st.session_state.generating = True
                st.rerun()

    if st.session_state.generating:
        do_generate_mod()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 返回主页", key="back_from_rapid"):
        st.session_state.mode = "home"
        st.session_state.messages = []
        st.rerun()

# ========================
# ✅ 生成完成展示页
# ========================
elif st.session_state.mode == "done":
    st.markdown("""
    <div style="text-align:center;padding:30px 0 10px 0;">
      <h2 style="font-family:Creepster;color:#FFD700;font-size:2.5rem;">
        ✨ MOD 铸造完成！
      </h2>
      <p style="color:#aaa;">前往侧边栏下载你的 Mod，或继续对话优化。</p>
    </div>
    """, unsafe_allow_html=True)

    # 展示最后一轮对话
    for msg in st.session_state.messages[-6:]:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        css_cls = "chat-msg" if role == "user" else "chat-msg assistant"
        color    = "#FF8C00"  if role == "user" else "#66BB6A"
        name     = "求生者"   if role == "user" else "暗影设计助手"
        st.markdown(
            f'<div class="{css_cls}">'
            f'<span class="chat-name" style="color:{color};">{name}</span><br>{content}'
            f'</div>',
            unsafe_allow_html=True
        )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 继续优化（探索模式）", use_container_width=True):
            st.session_state.mode = "explore"
            st.rerun()
    with col_b:
        if st.button("🏠 返回主页", use_container_width=True):
            st.session_state.mode = "home"
            st.session_state.messages = []
            st.rerun()

# ========================
# 📦 侧边栏：Mod 库
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
                    file_name=f"{mod['name'].replace(' ','_')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key=f"dl_{mod['id']}"
                )
            with col_re:
                if st.button("🔄", key=f"regen_{mod['id']}", use_container_width=True):
                    st.session_state.mode = "explore"
                    st.session_state.final_design = mod.get("design", "")
                    st.session_state.messages = [{"role": "user", "content": mod.get("design", "")}]
                    st.rerun()

    st.divider()
    st.write(f"对话：{len(st.session_state.messages)} 条")
    st.divider()
    if st.button("🗑️ 清除全部记录"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
