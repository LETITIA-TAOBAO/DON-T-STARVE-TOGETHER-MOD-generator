import streamlit as st
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
html, body, [class*="css"] {{
    background-color: transparent !important;
}}
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

/* ══════════════════════════
   图片按钮 - 彻底去除白底
   ══════════════════════════ */

/* 隐藏所有原生 Streamlit 按钮的视觉部分 */
.stButton > button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
    padding: 0 !important;
}}
.stButton > button:hover,
.stButton > button:focus,
.stButton > button:active {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
}}

/* 模式按钮容器 */
.mode-btn-img {{
    width: 100%;
    max-width: 400px;
    display: block;
    margin: 0 auto;
    cursor: pointer;
    transition: transform 0.25s ease, filter 0.25s ease;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.7));
    /* 关键：保留PNG透明度 */
    mix-blend-mode: normal;
}}
.mode-btn-img:hover {{
    transform: scale(1.06) translateY(-4px);
    filter: drop-shadow(0 12px 28px rgba(0,0,0,0.85)) brightness(1.15);
}}

/* ══════════════════════════
   说明卡片 - txt_box_bg背景
   ══════════════════════════ */
.cards-row {{
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 40px;
    margin: 20px auto 40px auto;
    max-width: 1000px;
    padding: 0 20px;
}}
.card-item {{
    flex: 1;
    max-width: 460px;
    background-image: url("{IMAGES['card_bg']}");
    background-size: 100% 100%;
    background-repeat: no-repeat;
    background-position: center;
    padding: 50px 40px 40px 40px;
    text-align: center;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.card-title {{
    font-family: Creepster !important;
    font-size: 1.6rem !important;
    margin-bottom: 14px !important;
}}
.card-rapid .card-title  {{ color: #ffaa60 !important; }}
.card-explore .card-title {{ color: #aadd88 !important; }}
.card-text {{
    font-family: "IM Fell English SC" !important;
    font-size: 0.95rem !important;
    line-height: 1.8 !important;
    color: #d4c4a0 !important;
    margin: 0;
}}
.card-en {{
    color: #998877 !important;
    font-size: 0.82em !important;
    font-style: italic !important;
    display: block !important;
    margin-top: 12px !important;
}}

/* ══════════════════════════
   MOD生成按钮 - 去除白底
   ══════════════════════════ */
.gen-btn-img {{
    display: block;
    max-width: 450px;
    width: 70%;
    margin: 20px auto 5px auto;
    cursor: pointer;
    transition: transform 0.25s, filter 0.25s;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.7));
}}
.gen-btn-img:hover {{
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
.chat-msg-assistant {{
    background: rgba(18,28,18,0.88);
    border-left: 4px solid #66BB6A;
    padding: 14px 18px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
}}
.chat-name {{
    font-family: Creepster !important;
    font-size: 1.05rem;
    display: block;
    margin-bottom: 6px;
}}

/* ── 侧边栏 ── */
section[data-testid="stSidebar"] {{
    background: rgba(25,15,8,0.98) !important;
    border-right: 4px solid #8B4513 !important;
}}
section[data-testid="stSidebar"] * {{
    color: #F5E6C8 !important;
}}

/* ── 聊天输入框 ── */
[data-testid="stChatInput"] textarea {{
    background-color: rgba(40,30,20,0.92) !important;
    border: 3px solid #8B4513 !important;
    color: #F5E6C8 !important;
    font-family: 'IM Fell English SC' !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #FFA726 !important;
    outline: none !important;
}}

/* ── 进度条颜色 ── */
.stProgress > div > div > div > div {{
    background-color: #FFD700 !important;
}}

/* ── 返回按钮样式（保留可见）── */
.back-btn > button {{
    background: rgba(60,40,20,0.8) !important;
    border: 2px solid #8B4513 !important;
    color: #F5E6C8 !important;
    font-family: 'IM Fell English SC' !important;
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
# ⭐ 主页
# ========================
if st.session_state.mode == "home":

    # 两列图片按钮
    col1, col2 = st.columns(2)

    with col1:
        # 先显示图片
        st.markdown(
            f'<img class="mode-btn-img" src="{IMAGES["btn_rapid"]}" alt="快速生成">',
            unsafe_allow_html=True
        )
        # 透明按钮覆盖
        if st.button("　　　　　　　　　　　　", key="btn_rapid_click", use_container_width=True):
            st.session_state.mode = "rapid"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.rerun()

    with col2:
        st.markdown(
            f'<img class="mode-btn-img" src="{IMAGES["btn_explore"]}" alt="探索设计">',
            unsafe_allow_html=True
        )
        if st.button("　　　　　　　　　　　　", key="btn_explore_click", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.session_state.final_design = ""
            st.rerun()

    # 横排说明卡片（txt_box_bg.png作为背景）
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
def generate_atlas_xml():
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
  <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''

def call_explore_llm(user_msg: str, history: list) -> str:
    """安全调用 explore_with_llm，自动适配参数数量"""
    import inspect
    try:
        sig = inspect.signature(explore_with_llm)
        param_count = len(sig.parameters)
        if param_count >= 2:
            result = explore_with_llm(user_msg, history)
        else:
            result = explore_with_llm(user_msg)
        if isinstance(result, dict):
            return result.get("text", str(result))
        return str(result)
    except Exception as e:
        return f"（暗影沉默了：{e}）"

def generate_icon_with_pollinations(prompt: str) -> dict:
    try:
        if not prompt or len(prompt) < 5:
            return {"success": False, "error": "Prompt 太短"}
        encoded = prompt.replace(" ", "+").replace("&", "%26")
        url = (f"https://image.pollinations.ai/prompt/{encoded}"
               f"?width=512&height=512&nologo=true&seed={int(datetime.now().timestamp())}")
        resp = requests.get(url, timeout=50)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return {
                "success": True,
                "base64": base64.b64encode(resp.content).decode(),
                "url": url
            }
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

def render_messages(messages: list):
    """渲染对话消息列表"""
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="chat-msg">'
                f'<span class="chat-name" style="color:#FF8C00;">⚔️ 求生者</span>'
                f'{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-msg-assistant">'
                f'<span class="chat-name" style="color:#66BB6A;">🌑 暗影设计助手</span>'
                f'{content}</div>',
                unsafe_allow_html=True
            )

# ========================
# 🔄 MOD 生成主流程
# ========================
def do_generate_mod():
    st.markdown("""
    <div style="background:rgba(30,20,10,0.85);border:2px solid #8B4513;
                border-radius:12px;padding:30px;text-align:center;margin:20px auto;max-width:700px;">
      <h2 style="font-family:Creepster;font-size:2rem;color:#FFD700;margin:0;">
        ⚙️ 世界正在扭曲……
      </h2>
      <p style="color:#aa9977;margin-top:10px;">The shadows are weaving your madness...</p>
    </div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)

    with st.spinner("📝 Qwen 正在生成 Mod 代码…"):
        progress_bar.progress(20)
        try:
            result = design_with_llm(st.session_state.final_design, st.session_state.messages)
        except Exception as e:
            result = {"text": f"生成失败：{e}", "data": {}}

    with st.spinner("🎨 正在优化图标提示词…"):
        progress_bar.progress(50)
        try:
            visual_result = optimize_visual_prompt(st.session_state.final_design)
            image_prompt = visual_result.get("optimized_prompt",
                           visual_result.get("fallback_prompt", "don't starve together mod icon"))
        except Exception as e:
            image_prompt = "don't starve together mod icon dark fantasy"

    icon_result = {"success": False, "error": "未执行"}
    with st.spinner("🖼️ Pollinations.ai 正在绘制图标…"):
        progress_bar.progress(75)
        icon_result = generate_icon_with_pollinations(image_prompt)
        if icon_result["success"]:
            st.success("✅ 图标生成成功！")
            st.image(icon_result["url"], caption="生成的图标预览", width=200)
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(icon_result["base64"])
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
        else:
            st.warning(f"⚠️ 图标生成失败：{icon_result['error']}")

    progress_bar.progress(100)
    st.success("✅ MOD 文件生成完成！")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("text", "Mod 已生成完毕。")
    })

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

    st.session_state.generating = False
    st.session_state.mode = "done"
    st.rerun()

# ========================
# 💬 探索模式（多轮对话）
# ========================
if st.session_state.mode == "explore":

    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px 0;">
      <h3 style="font-family:Creepster;color:#4CAF50;font-size:1.8rem;margin:0;">
        👁️ 迷雾探路者 · 探索设计模式
      </h3>
      <p style="color:#888;font-size:0.9rem;margin-top:6px;">
        与暗影助手充分对话，确认设计后点击「MOD生成」按钮
      </p>
    </div>
    """, unsafe_allow_html=True)

    # 渲染对话
    render_messages(st.session_state.messages)

    # 输入框
    user_input = st.chat_input("描述你的想法，与暗影助手对话…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🌑 暗影低语中…"):
            reply_text = call_explore_llm(user_input, st.session_state.messages[:-1])
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

    # MOD生成按钮（至少一轮对话后显示）
    if len(st.session_state.messages) >= 2:
        st.markdown(
            f'<img class="gen-btn-img" src="{IMAGES["btn_generate"]}" alt="MOD生成">',
            unsafe_allow_html=True
        )
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            if st.button("🔨 确认生成 MOD", key="explore_gen_btn", use_container_width=True):
                summary = "\n".join(
                    f"{'用户' if m['role']=='user' else '助手'}: {m['content']}"
                    for m in st.session_state.messages
                )
                st.session_state.final_design = summary
                st.session_state.generating = True
                st.rerun()

    if st.session_state.generating:
        do_generate_mod()

    # 返回按钮
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        if st.button("← 返回主页", key="back_from_explore"):
            st.session_state.mode = "home"
            st.session_state.messages = []
            st.session_state.generating = False
            st.rerun()

# ========================
# ⚡ 快速生成模式
# ========================
elif st.session_state.mode == "rapid":

    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px 0;">
      <h3 style="font-family:Creepster;color:#FFD700;font-size:1.8rem;margin:0;">
        🔥 意志铸剑者 · 快速生成模式
      </h3>
      <p style="color:#888;font-size:0.9rem;margin-top:6px;">
        输入你完整的 Mod 构想，LLM 将帮你细化方案，确认后点击「MOD生成」
      </p>
    </div>
    """, unsafe_allow_html=True)

    render_messages(st.session_state.messages)

    user_input = st.chat_input("输入你的完整 Mod 构想…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🌑 暗影正在解读你的构想…"):
            reply_text = call_explore_llm(user_input, st.session_state.messages[:-1])
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

    if len(st.session_state.messages) >= 2:
        st.markdown(
            f'<img class="gen-btn-img" src="{IMAGES["btn_generate"]}" alt="MOD生成">',
            unsafe_allow_html=True
        )
        col_l, col_c, col_r = st.columns([1, 2, 1])
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
        st.session_state.generating = False
        st.rerun()

# ========================
# ✅ 生成完成页
# ========================
elif st.session_state.mode == "done":
    st.markdown("""
    <div style="text-align:center;padding:30px 0 16px 0;">
      <h2 style="font-family:Creepster;color:#FFD700;font-size:2.5rem;margin:0;">
        ✨ MOD 铸造完成！
      </h2>
      <p style="color:#aaa;margin-top:8px;">前往侧边栏下载你的 Mod，或继续优化。</p>
    </div>
    """, unsafe_allow_html=True)

    render_messages(st.session_state.messages[-6:])

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
