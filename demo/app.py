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
    "design_spec": None,
    "visual_result": None,
    "sound_result": None,
    "preview_image_url": None,
    "preview_image_b64": None,
    "preview_approved": False,
    "stage": "chat",           # chat / preview / generating / done
    "generating": False,
    "sound_audio_cache": {},   # 存储已生成的音效
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========================
# 📸 背景图路径
# ========================
BASE_URL = "https://raw.githubusercontent.com/LETITIA-TAOBAO/DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
BG_URL = BASE_URL + "background.jpg.png"

# ========================
# 🎨 CSS（饥荒风格 + 半透明背景）
# ========================
st.markdown(f"""
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
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(8, 4, 0, 0.48);
    z-index: -1;
}}
.block-container, .stMainBlockContainer {{
    background: rgba(20, 11, 3, 0.58) !important;
    backdrop-filter: blur(3px);
    border-left: 1px solid rgba(160, 110, 40, 0.15);
    border-right: 1px solid rgba(160, 110, 40, 0.15);
}}

/* 侧边栏半透明 */
section[data-testid="stSidebar"] {{
    background: rgba(15, 8, 2, 0.78) !important;
    border-right: 2px solid rgba(160, 100, 30, 0.45) !important;
    backdrop-filter: blur(4px);
}}
section[data-testid="stSidebar"] * {{ color: #C8A868 !important; }}
section[data-testid="stSidebar"] h1, h2, h3 {{ color: #D4A843 !important; }}

/* 字体 */
h1, h2, h3 {{
    font-family: 'Cinzel Decorative', serif !important;
    color: #D4A843 !important;
    text-shadow: 0 0 20px rgba(200,160,60,0.45), 2px 2px 4px rgba(0,0,0,0.8) !important;
}}
p, span, div, label, li {{
    font-family: 'IM Fell English SC', serif !important;
    color: #EDD9A3 !important;
}}

/* Banner */
.dst-banner {{
    background: rgba(15,8,2,0.82);
    border: 2px solid #7B5820;
    border-top: 3px solid #C8A84B;
    border-bottom: 3px solid #C8A84B;
    padding: 36px 44px 30px;
    border-radius: 4px;
    text-align: center;
    margin: 10px auto 28px auto;
    max-width: 820px;
    box-shadow: 0 0 60px rgba(0,0,0,0.7), inset 0 0 30px rgba(0,0,0,0.4);
}}
.banner-sub {{ font-family: 'Cinzel', serif !important; color: #7B5820 !important; font-size: 0.82rem; letter-spacing: 4px; }}
.banner-divider {{ border: none; border-top: 1px solid #5a3a10; width: 40%; margin: 16px auto; }}
.banner-quote {{ font-style: italic; color: #C8A86A !important; line-height: 1.9; }}

/* 模式卡片 */
.mode-cards {{ display: flex; gap: 24px; justify-content: center; margin: 0 auto 28px; max-width: 880px; }}
.mode-card {{
    flex: 1; max-width: 420px; background: rgba(18,10,3,0.84);
    border: 2px solid #5a3a10; border-radius: 6px; padding: 26px 22px;
    text-align: center; cursor: pointer; transition: all 0.3s;
}}
.mode-card:hover {{ border-color: #C8A84B; transform: translateY(-4px); }}
.mode-card-icon {{ font-size: 2.4rem; margin-bottom: 8px; }}
.mode-card-title {{ font-family: 'Cinzel Decorative', serif !important; font-size: 1.15rem !important; color: #D4A843 !important; }}
.mode-card-sub {{ font-size: 0.72rem; color: #7a5a28; letter-spacing: 3px; }}
.mode-card-desc {{ font-size: 0.88rem; line-height: 1.8; color: #B89A62; }}

/* 按钮 */
div[data-testid="stButton"] > button {{
    background: rgba(20,10,3,0.87) !important;
    border: 2px solid #7a5020 !important;
    color: #D4A843 !important;
    font-family: 'IM Fell English SC', serif !important;
    padding: 10px 24px !important;
    border-radius: 4px !important;
    transition: all 0.25s;
}}
div[data-testid="stButton"] > button:hover {{
    background: rgba(50,25,5,0.96) !important;
    border-color: #C8A84B !important;
    color: #FFD700 !important;
    transform: translateY(-2px);
}}

/* 主操作按钮 */
.primary-btn div[data-testid="stButton"] > button {{
    background: rgba(55,22,5,0.92) !important;
    border: 2px solid #C8A84B !important;
    font-size: 1.08rem !important;
    padding: 14px 32px !important;
}}
.primary-btn div[data-testid="stButton"] > button:hover {{
    box-shadow: 0 0 25px rgba(200,168,75,0.3);
}}

/* 聊天气泡 */
.chat-user, .chat-ai {{
    padding: 12px 16px; margin: 10px 0; border-radius: 0 6px 6px 0;
}}
.chat-user {{ background: rgba(25,14,4,0.9); border-left: 3px solid #C8820C; }}
.chat-ai   {{ background: rgba(8,20,10,0.9);  border-left: 3px solid #4A9A50; }}
.chat-name {{ font-family: 'Cinzel', serif !important; font-size: 0.78rem; letter-spacing: 2px; display: block; margin-bottom: 5px; }}

/* 预览框 */
.preview-box {{
    background: rgba(12,6,1,0.88);
    border: 2px solid #6B5018;
    border-radius: 6px;
    padding: 22px;
    margin: 14px 0;
}}
.preview-box-title {{
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 1.1rem !important;
    color: #D4A843 !important;
    text-align: center;
    margin-bottom: 16px;
}}

/* 音效卡片 */
.sound-card {{
    background: rgba(8,20,10,0.82);
    border: 1px solid #2a4a2a;
    border-radius: 5px;
    padding: 12px 16px;
    margin: 8px 0;
}}
.sound-trigger {{ font-family: 'Cinzel', serif !important; font-size: 0.72rem; color: #4A9A50; letter-spacing: 2px; }}
.sound-desc {{ font-size: 0.88rem; color: #C8D8C8; }}
.sound-prompt {{ font-size: 0.7rem; color: #3a5a3a; font-style: italic; }}

/* 音频控件 */
audio {{ width: 100%; margin-top: 6px; filter: sepia(0.3) saturate(0.8); }}

.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, #6B3A08, #C8A84B, #F0D070) !important;
}}
</style>
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

def fetch_image(prompt: str) -> dict:
    try:
        enc = prompt.replace(" ", "+").replace("&", "%26")
        url = (f"https://image.pollinations.ai/prompt/{enc}"
               f"?width=512&height=512&nologo=true&model=flux"
               f"&seed={int(datetime.now().timestamp())}")
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 1000:
            return {
                "ok": True,
                "b64": base64.b64encode(r.content).decode(),
                "url": url
            }
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def make_zip(mod: dict) -> bytes:
    buf = io.BytesIO()
    install_txt = """══════════════════════════════════════
   饥荒联机版 MOD 安装指南
══════════════════════════════════════

① 将文件夹复制到：
   Steam/steamapps/common/Don't Starve Together/mods/

② 启动游戏 → 模组 → 启用本 Mod

③ 创建或进入世界即可生效。

如有问题请查看 log.txt
══════════════════════════════════════
"""
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in mod.get("all_files", {}).items():
            if isinstance(content, str):
                zf.writestr(name, content.encode("utf-8"))
            elif isinstance(content, bytes):
                zf.writestr(name, content)
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
                f'<span class="chat-content">{m["content"]}</span></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-ai">'
                f'<span class="chat-name" style="color:#4A9A50;">✦ SHADOW ARCHITECT</span>'
                f'<span class="chat-content">{m["content"]}</span></div>',
                unsafe_allow_html=True)

def reset_to_home():
    st.session_state.update({
        "mode": "home",
        "stage": "chat",
        "messages": [],
        "final_design": "",
        "design_spec": None,
        "visual_result": None,
        "sound_result": None,
        "preview_image_url": None,
        "preview_image_b64": None,
        "preview_approved": False,
        "generating": False,
        "sound_audio_cache": {},
    })

# ========================
# 🔊 可试听音效组件
# ========================
def render_sound_preview(sound: dict):
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">🔊 音效方案（点击可试听）</p>', unsafe_allow_html=True)

    sfx_list = sound.get("sound_effects", [])
    cache = st.session_state.sound_audio_cache

    for i, sfx in enumerate(sfx_list):
        trigger = sfx.get("trigger", f"音效{i+1}")
        desc = sfx.get("description_cn", "")
        prompt = sfx.get("prompt_en", "")
        key = f"sfx_{i}"

        st.markdown(f"""
        <div class="sound-card">
          <span class="sound-trigger">▶ {trigger.upper()}</span>
          <span class="sound-desc">{desc}</span>
          <span class="sound-prompt">{prompt}</span>
        </div>
        """, unsafe_allow_html=True)

        if key in cache and cache[key].get("ok"):
            st.audio(cache[key]["audio_bytes"], format=f'audio/{cache[key].get("format","wav")}')
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 换一个", key=f"regen_{i}", use_container_width=True):
                    del cache[key]
                    st.rerun()
            with col2:
                st.download_button("⬇ 下载", 
                                   data=cache[key]["audio_bytes"],
                                   file_name=f"{trigger}.wav",
                                   mime="audio/wav",
                                   key=f"dl_{i}",
                                   use_container_width=True)
        else:
            if st.button(f"🎵 生成并试听", key=f"gen_{i}", use_container_width=True):
                with st.spinner("正在生成音效..."):
                    result = generate_sound_effect(prompt)
                    cache[key] = result
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ========================
# 🎨 预览页面
# ========================
def render_preview_stage():
    spec = st.session_state.design_spec or {}
    visual = st.session_state.visual_result or {}
    sound = st.session_state.sound_result or {}
    obj = spec.get("main_object", {})

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#C8A84B !important;">✦ 设计预览 · Design Preview</h3>
      <p>确认图像与音效后点击「铸造 MOD」</p>
    </div>
    """, unsafe_allow_html=True)

    # 设计规格
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">📋 MOD 设计规格</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <b>名称：</b> {spec.get("mod_name_cn","—")} ({spec.get("mod_name_en","—")})<br>
    <b>类型：</b> {spec.get("mod_type","—")}<br>
    <b>核心功能：</b> {spec.get("core_function","—")}<br>
    <b>主要对象：</b> {obj.get("name_cn","—")} ({obj.get("appearance","—")})
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown('<p class="preview-box-title">🎨 外观预览</p>', unsafe_allow_html=True)
        if st.session_state.preview_image_url:
            st.image(st.session_state.preview_image_url, use_container_width=True)
        else:
            st.info("图片生成中...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        render_sound_preview(sound)

    st.markdown("<hr>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 3, 2])
    with c2:
        if st.button("⚙ 确认并铸造 MOD", key="confirm_forge", use_container_width=True):
            st.session_state.stage = "generating"
            st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✏ 继续调整设计", key="back_to_chat"):
            st.session_state.stage = "chat"
            st.rerun()
    with col_b:
        if st.button("✕ 返回主页", key="abort"):
            reset_to_home()
            st.rerun()


# ========================
# 其他页面函数（简化版，保持逻辑）
# ========================

def render_home():
    st.markdown("""
    <div class="dst-banner">
      <h1>饥荒 MOD 生成器</h1>
      <p class="banner-sub">DON'T STARVE TOGETHER MOD GENERATOR</p>
      <hr class="banner-divider">
      <p class="banner-quote">
        当理智归零，现实崩塌。<br>
        <em>You are no longer a survivor, but a Creator.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ 快速生成", key="home_rapid", use_container_width=True):
            st.session_state.mode = "rapid"
            st.session_state.stage = "chat"
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("👁 探索设计", key="home_explore", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.stage = "chat"
            st.session_state.messages = []
            st.rerun()


def render_chat_stage(mode: str):
    is_explore = mode == "explore"
    title = "👁 迷雾探路者" if is_explore else "⚡ 意志铸剑者"
    color = "#4CAF50" if is_explore else "#D4A843"

    st.markdown(f"""
    <div class="mode-header">
      <h3 style="color:{color} !important;">{title}</h3>
      <p>与暗影对话 → 设计明确后点击「预览并确认」</p>
    </div>
    """, unsafe_allow_html=True)

    render_chat(st.session_state.messages)

    user_input = st.chat_input("描述你的想法...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("暗影正在回应..."):
            if is_explore:
                reply = explore_with_llm(st.session_state.messages)
            else:
                reply = rapid_with_llm(st.session_state.messages)
            text = reply.get("text", str(reply)) if isinstance(reply, dict) else str(reply)
            st.session_state.messages.append({"role": "assistant", "content": text})
        st.rerun()

    if len(st.session_state.messages) >= 2:
        if st.button("✦ 预览并确认设计", key="to_preview", use_container_width=True):
            with st.spinner("正在整理设计规格..."):
                spec = summarize_design(st.session_state.messages)
                st.session_state.design_spec = spec
                st.session_state.final_design = json.dumps(spec, ensure_ascii=False, indent=2)

                visual = optimize_visual_prompt(spec)
                st.session_state.visual_result = visual
                img = fetch_image(visual.get("optimized_prompt", visual.get("fallback_prompt", "")))
                if img["ok"]:
                    st.session_state.preview_image_url = img["url"]
                    st.session_state.preview_image_b64 = img["b64"]

                sound = generate_sound_prompts(spec)
                st.session_state.sound_result = sound

            st.session_state.stage = "preview"
            st.rerun()

    if st.button("← 返回主页"):
        reset_to_home()
        st.rerun()


def render_generating_stage():
    st.markdown("""
    <div style="text-align:center;padding:40px;background:rgba(12,6,1,0.9);border:2px solid #7a4010;border-radius:8px;">
      <h2 style="color:#D4A843;">世界正在扭曲……</h2>
      <p style="color:#aa9060;">暗影正在将你的意志铸造成现实……</p>
    </div>
    """, unsafe_allow_html=True)

    bar = st.progress(0)
    with st.spinner("生成 Mod 代码..."):
        bar.progress(30)
        result = design_with_llm(st.session_state.final_design, st.session_state.messages)
    bar.progress(60)

    with st.spinner("封印图腾与音效..."):
        bar.progress(85)
        if st.session_state.preview_image_b64:
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(st.session_state.preview_image_b64)
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()

    bar.progress(100)

    st.session_state.messages.append({"role": "assistant", "content": result.get("text", "MOD 已铸造完成")})
    st.session_state.generated_mods.append({
        "id": len(st.session_state.generated_mods) + 1,
        "name": result.get("data", {}).get("name", "CustomMod"),
        "desc": result.get("data", {}).get("desc", ""),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "design": st.session_state.final_design,
        "all_files": result.get("data", {}).get("files", {}),
        "image_url": st.session_state.preview_image_url,
    })

    st.session_state.stage = "done"
    st.rerun()


def render_done_stage():
    st.success("✨ MOD 铸造完成！")
    render_chat(st.session_state.messages[-6:])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("继续优化", use_container_width=True):
            st.session_state.stage = "chat"
            st.session_state.mode = "explore"
            st.rerun()
    with col2:
        if st.button("返回主页", use_container_width=True):
            reset_to_home()
            st.rerun()


# ========================
# 主路由
# ========================
if st.session_state.mode == "home":
    render_home()
elif st.session_state.mode in ["explore", "rapid"]:
    if st.session_state.stage == "chat":
        render_chat_stage(st.session_state.mode)
    elif st.session_state.stage == "preview":
        render_preview_stage()
    elif st.session_state.stage == "generating":
        render_generating_stage()
    elif st.session_state.stage == "done":
        render_done_stage()

# ========================
# 侧边栏
# ========================
with st.sidebar:
    st.markdown("### ✦ MOD 典藏库")
    if not st.session_state.generated_mods:
        st.write("暂无已生成 Mod")
    else:
        for mod in reversed(st.session_state.generated_mods):
            with st.expander(mod["name"]):
                st.caption(mod["date"])
                st.caption(mod.get("desc", ""))
                if mod.get("image_url"):
                    st.image(mod["image_url"], width=120)
                zip_data = make_zip(mod)
                st.download_button(
                    "下载 MOD",
                    data=zip_data,
                    file_name=f"{mod['name']}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    st.divider()
    st.caption(f"对话条数：{len(st.session_state.messages)}")
    st.caption(f"已生成 Mod：{len(st.session_state.generated_mods)} 个")
    if st.button("清除全部记录"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
