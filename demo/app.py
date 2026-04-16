import streamlit as st
import io
import json
import re
import zipfile
import requests
import base64
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# ⚠️ LLM 导入
# ══════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════
# 🔧 Session State
# ══════════════════════════════════════════════════════════════
for key, val in {
    "mode": "home",
    "messages": [],
    "generated_mods": [],
    "final_design": "",
    "design_spec": None,
    "visual_result": None,
    "sound_result": None,
    "preview_images": [],
    "preview_approved": False,
    "stage": "chat",
    "generating": False,
    "sound_audio_cache": {},
    "show_producer_msg": False,
    "show_install_guide": False,
    "num_images": 1,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════════════════════
# 📸 背景图
# ══════════════════════════════════════════════════════════════
BASE_URL = (
    "https://raw.githubusercontent.com/LETITIA-TAOBAO/"
    "DON-T-STARVE-TOGETHER-MOD-generator/main/demo/assets/"
)
BG_URL = BASE_URL + "background.jpg.png"

# ══════════════════════════════════════════════════════════════
# 🎨 CSS
# ══════════════════════════════════════════════════════════════
_creator_tag_css = ""
if st.session_state.mode == "home":
    _creator_tag_css = """
    .creator-tag {
        position: fixed; bottom: 20px; right: 24px; z-index: 9999;
        text-align: right; pointer-events: auto;
        background: rgba(15,8,2,0.88);
        border: 2px solid rgba(139,100,32,0.5); border-radius: 6px;
        padding: 14px 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.7);
        opacity: 0.85; transition: all 0.3s ease;
    }
    .creator-tag:hover {
        opacity: 1.0; border-color: rgba(200,168,75,0.75);
        box-shadow: 0 6px 24px rgba(0,0,0,0.8), 0 0 20px rgba(200,168,75,0.2);
    }
    .creator-tag p {
        font-family: 'Cinzel', serif !important; font-size: 0.75rem !important;
        color: #C8A868 !important; letter-spacing: 2px !important;
        margin: 4px 0 !important; line-height: 1.7 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.9) !important;
    }
    .creator-tag .creator-name {
        font-weight: 600 !important; color: #D4A843 !important;
        font-size: 0.82rem !important;
    }
    .creator-tag .creator-divider {
        border: none; border-top: 1px solid rgba(139,100,32,0.4);
        margin: 8px 0; width: 100%;
    }
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC:ital@0;1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');

.stApp {{
    background-image: url("{BG_URL}");
    background-size: cover; background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content:""; position:fixed; inset:0;
    background:rgba(8,4,0,0.45); z-index:0; pointer-events:none;
}}
.stAppViewContainer .stMainBlockContainer, .block-container {{
    background:rgba(20,11,3,0.55) !important; backdrop-filter:blur(2px);
}}
html,[class*="css"] {{ background-color:transparent !important; }}

section[data-testid="stSidebar"] {{
    background:rgba(15,8,2,0.72) !important;
    border-right:2px solid rgba(160,100,30,0.35) !important;
    backdrop-filter:blur(4px);
}}
section[data-testid="stSidebar"]>div {{ background:transparent !important; }}
section[data-testid="stSidebar"] * {{ color:#C8A868 !important; }}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{ color:#D4A843 !important; }}

h1,h2,h3 {{
    font-family:'Cinzel Decorative',serif !important; color:#D4A843 !important;
    text-shadow:0 0 20px rgba(200,160,60,0.4),2px 2px 4px rgba(0,0,0,0.8) !important;
    letter-spacing:2px !important;
}}
p,span,div,label,li {{
    font-family:'IM Fell English SC',serif !important; color:#EDD9A3 !important;
}}

.dst-banner {{
    background:rgba(15,8,2,0.82); border:2px solid #7B5820;
    border-top:3px solid #C8A84B; border-bottom:3px solid #C8A84B;
    padding:36px 44px 30px; border-radius:4px;
    text-align:center; margin:10px auto 28px; max-width:820px;
    box-shadow:0 0 60px rgba(0,0,0,0.7),inset 0 0 30px rgba(0,0,0,0.4);
    position:relative;
}}
.dst-banner::before,.dst-banner::after {{
    content:"✦"; position:absolute; top:12px; color:#7B5820; font-size:1.2rem;
}}
.dst-banner::before {{ left:18px; }}
.dst-banner::after  {{ right:18px; }}
.banner-sub {{
    font-family:'Cinzel',serif !important; color:#7B5820 !important;
    font-size:0.8rem; letter-spacing:4px; margin-top:5px;
}}
.banner-divider {{
    border:none; border-top:1px solid #5a3a10; width:40%; margin:16px auto;
}}
.banner-quote {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.98rem; line-height:1.9; color:#C8A86A !important;
    font-style:italic;
}}

.mode-cards {{
    display:flex; gap:24px; justify-content:center;
    margin:0 auto 28px; max-width:880px;
}}
.mode-card {{
    flex:1; max-width:420px; background:rgba(18,10,3,0.84);
    border:2px solid #5a3a10; border-radius:6px;
    padding:26px 22px 22px; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.5); position:relative; overflow:hidden;
}}
.mode-card::before {{
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,transparent,#C8A84B,transparent);
}}
.mode-card-icon  {{ font-size:2.2rem; margin-bottom:8px; display:block; }}
.mode-card-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.1rem !important; color:#D4A843 !important; margin:0 0 4px !important;
}}
.mode-card-sub {{
    font-family:'Cinzel',serif !important; font-size:0.7rem !important;
    color:#7a5a28 !important; letter-spacing:3px; margin-bottom:12px !important;
    display:block;
}}
.mode-card-divider {{
    border:none; border-top:1px solid #3a2008; margin:10px auto; width:60%;
}}
.mode-card-desc {{
    font-size:0.88rem !important; line-height:1.8 !important;
    color:#B89A62 !important; margin:0 !important;
}}
.mode-card-en {{
    font-style:italic !important; color:#5a4020 !important;
    font-size:0.76em !important; display:block !important; margin-top:10px !important;
}}
.mode-card-hint {{
    display:inline-block; margin-top:16px; padding:5px 18px;
    border:1px solid #7B5820; border-radius:3px;
    font-size:0.8rem !important; color:#C8A84B !important;
    background:rgba(100,60,10,0.18); letter-spacing:1px;
}}

div[data-testid="stButton"]>button {{
    background:rgba(20,10,3,0.87) !important;
    border:2px solid #7a5020 !important; color:#D4A843 !important;
    font-family:'IM Fell English SC',serif !important;
    font-size:1rem !important; letter-spacing:1px !important;
    padding:10px 24px !important; border-radius:4px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.5) !important;
    text-shadow:0 0 8px rgba(200,160,60,0.35) !important;
}}
div[data-testid="stButton"]>button:hover {{
    background:rgba(50,25,5,0.96) !important;
    border-color:#C8A84B !important; color:#FFD700 !important;
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(0,0,0,0.6),0 0 15px rgba(200,168,75,0.2) !important;
}}
.primary-btn div[data-testid="stButton"]>button {{
    background:rgba(55,22,5,0.92) !important;
    border:2px solid #C8A84B !important;
    font-size:1.08rem !important; padding:13px 32px !important;
    letter-spacing:2px !important;
}}
.primary-btn div[data-testid="stButton"]>button:hover {{
    background:rgba(85,35,8,0.97) !important;
    box-shadow:0 0 30px rgba(200,168,75,0.28),0 6px 20px rgba(0,0,0,0.6) !important;
}}
.danger-btn div[data-testid="stButton"]>button {{
    border-color:#6B2020 !important; color:#BB5555 !important;
}}
.danger-btn div[data-testid="stButton"]>button:hover {{
    border-color:#CC3333 !important; color:#FF7777 !important;
    background:rgba(50,8,8,0.92) !important;
}}

.mode-header {{
    background:rgba(12,6,1,0.80); border:1px solid #4a3010;
    border-top:3px solid #9B7830; border-radius:4px;
    padding:20px 28px 16px; text-align:center; margin-bottom:18px;
}}
.mode-header h3 {{ font-size:1.55rem !important; margin:0 0 5px !important; }}
.mode-header p  {{ font-size:0.86rem !important; color:#7a6040 !important; margin:0 !important; }}

.chat-user {{
    background:rgba(25,14,4,0.90); border-left:3px solid #C8820C;
    border-bottom:1px solid rgba(200,130,12,0.18);
    padding:12px 16px; margin:10px 0; border-radius:0 6px 6px 0;
}}
.chat-ai {{
    background:rgba(8,20,10,0.90); border-left:3px solid #4A9A50;
    border-bottom:1px solid rgba(74,154,80,0.18);
    padding:12px 16px; margin:10px 0; border-radius:0 6px 6px 0;
}}
.chat-name {{
    font-family:'Cinzel',serif !important; font-size:0.78rem !important;
    letter-spacing:2px !important; display:block; margin-bottom:5px;
}}
.chat-content {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.93rem !important; line-height:1.78 !important;
    color:#D4BC88 !important; white-space:pre-wrap;
}}

.preview-box {{
    background:rgba(12,6,1,0.90); border:2px solid #6B5018;
    border-radius:6px; padding:22px; margin:14px 0;
}}
.preview-box-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.05rem !important; color:#D4A843 !important;
    text-align:center; margin-bottom:14px !important; letter-spacing:2px;
}}

/* ── 贴图限制说明栏 ── */
.img-limit-notice {{
    background: rgba(30,18,5,0.85);
    border: 1px solid #5a3a10;
    border-left: 3px solid #C8A84B;
    border-radius: 4px;
    padding: 10px 16px;
    margin: 8px 0 14px 0;
    font-size: 0.80rem !important;
    color: #A88A58 !important;
    line-height: 1.7 !important;
}}
.img-limit-notice strong {{
    color: #D4A843 !important;
    font-size: 0.82rem !important;
}}
.img-limit-notice .limit-icon {{
    font-size: 0.90rem;
    margin-right: 4px;
}}

.spec-grid {{
    display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0;
}}
.spec-item {{
    background:rgba(25,14,4,0.72); border:1px solid #3a2510;
    border-radius:4px; padding:9px 13px;
}}
.spec-label {{
    font-family:'Cinzel',serif !important; font-size:0.68rem !important;
    color:#7a5a28 !important; letter-spacing:2px; display:block; margin-bottom:3px;
}}
.spec-value {{ font-size:0.86rem !important; color:#D4BC88 !important; }}

.sound-card {{
    background:rgba(8,20,10,0.82); border:1px solid #2a4a2a;
    border-radius:5px; padding:11px 14px; margin:7px 0;
    transition:border-color 0.2s;
}}
.sound-card:hover {{ border-color:#4A9A50; }}
.sound-trigger {{
    font-family:'Cinzel',serif !important; font-size:0.70rem !important;
    color:#4A9A50 !important; letter-spacing:2px; display:block; margin-bottom:3px;
}}
.sound-desc {{
    font-size:0.87rem !important; color:#C0D8C0 !important;
    display:block; margin-bottom:4px;
}}

.img-card {{
    background:rgba(8,4,0,0.82); border:1px solid #4a3010;
    border-radius:6px; padding:8px; text-align:center;
}}
.img-card-label {{
    font-family:'Cinzel',serif !important; font-size:0.72rem !important;
    color:#7a5a28 !important; letter-spacing:2px; display:block; margin-top:6px;
}}

audio {{
    width:100%; height:34px; margin-top:6px;
    filter:sepia(0.4) saturate(0.7) brightness(0.9); border-radius:4px;
}}

.gen-box {{
    background:rgba(12,6,1,0.92); border:2px solid #7a4010;
    border-top:3px solid #C8A84B; border-radius:6px;
    padding:30px; text-align:center; margin:14px auto; max-width:600px;
}}

[data-testid="stChatInput"] {{
    background:rgba(15,8,2,0.82) !important;
    border-top:1px solid rgba(139,100,32,0.35) !important;
}}
[data-testid="stChatInput"] textarea {{
    background:rgba(20,11,3,0.93) !important;
    border:1px solid #4a3010 !important; color:#EDD9A3 !important;
    font-family:'IM Fell English SC',serif !important; border-radius:4px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color:#C8A84B !important;
    box-shadow:0 0 10px rgba(200,168,75,0.18) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color:#5a4028 !important; font-style:italic !important;
}}

.stProgress>div>div>div>div {{
    background:linear-gradient(90deg,#6B3A08,#C8A84B,#F0D070) !important;
    border-radius:4px !important;
}}
.st-expander {{
    background:rgba(20,11,3,0.74) !important;
    border:1px solid #4a3010 !important; border-radius:4px !important;
}}
.st-expander [data-testid="stMarkdownContainer"] p {{
    margin: 4px 0 !important; line-height: 1.5 !important;
}}
hr {{
    border:none !important;
    border-top:1px solid rgba(139,100,32,0.28) !important;
    margin:16px 0 !important;
}}
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:rgba(10,5,0,0.3); }}
::-webkit-scrollbar-thumb {{ background:#5a3810; border-radius:3px; }}

{_creator_tag_css}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🔧 工具函数
# ══════════════════════════════════════════════════════════════

# ── 贴图上限常量（统一管理，方便日后修改）──────────────────
MAX_IMAGES = 4

def generate_atlas_xml() -> str:
    return '''<?xml version="1.0" encoding="utf-8"?>
<TextureAtlas imagePath="modicon.tex">
  <SubTexture name="default" x="0" y="0" width="512" height="512"/>
</TextureAtlas>
'''


def _clean_for_url(text: str, max_chars: int = 300) -> str:
    """
    清理文本用于 URL：
    1. 移除所有中文字符
    2. 只保留英文字母、数字、空格、逗号、连字符
    3. 按字符数截断（不按词数，更精确控制长度）
    4. 清理多余空格
    """
    # 移除中文
    text = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df]+', '', text)
    # 只保留安全字符
    text = re.sub(r'[^\w\s,\-\.]', ' ', text)
    # 合并多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 按字符数截断（在词边界截断）
    if len(text) > max_chars:
        text = text[:max_chars]
        # 在最后一个空格处截断，避免截断单词中间
        last_space = text.rfind(' ')
        if last_space > max_chars // 2:
            text = text[:last_space]
    return text.strip()


def _build_safe_image_url(prompt: str, seed: int) -> str:
    """
    构建安全的图片 URL：
    - prompt 严格限制在 250 字符以内（编码前）
    - negative prompt 固定使用极短版本
    - 使用 requests.Request 来正确编码，避免手动拼接出错
    """
    # 固定短版 negative prompt（约 80 字符）
    FIXED_NEG = (
        "realistic photo 3d render anime bright colors "
        "text watermark blurry modern"
    )

    # 清理并严格截断 prompt
    clean = _clean_for_url(prompt, max_chars=250)
    if len(clean) < 8:
        clean = (
            "Don't Starve Together dark gothic item "
            "hand-drawn sketch muted parchment style"
        )

    # 手动构建 URL（pollinations 的路径参数需要特殊处理）
    # 只对空格和逗号编码，保留其他 ASCII 字符
    enc_prompt = clean.replace(" ", "+").replace(",", "%2C")
    enc_neg    = FIXED_NEG.replace(" ", "+")

    url = (
        f"https://image.pollinations.ai/prompt/{enc_prompt}"
        f"?width=512&height=512"
        f"&nologo=true"
        f"&negative={enc_neg}"
        f"&model=flux"
        f"&seed={seed % 99999}"
    )
    return url


def fetch_image(prompt: str, negative: str = "") -> dict:
    """
    健壮版图片获取：
    - 严格控制 URL 总长度 ≤ 1500 字符
    - 最多重试 2 次（换种子）
    - 详细错误信息
    """
    seed = int(datetime.now().timestamp()) % 99999

    for attempt in range(2):
        try:
            url = _build_safe_image_url(prompt, seed + attempt * 1000)

            # 安全检查：URL 总长不超过 1500
            if len(url) > 1500:
                # 进一步截短 prompt
                short_prompt = _clean_for_url(prompt, max_chars=150)
                url = _build_safe_image_url(short_prompt, seed + attempt * 1000)

            print(f"[DEBUG] 图片请求 URL 长度={len(url)}, attempt={attempt+1}")
            print(f"[DEBUG] URL: {url[:120]}...")

            r = requests.get(url, timeout=90)

            if r.status_code == 200 and len(r.content) > 1000:
                return {
                    "ok":  True,
                    "b64": base64.b64encode(r.content).decode(),
                    "url": url,
                }
            elif r.status_code == 200:
                # 返回了内容但太小（可能是错误图）
                print(f"[DEBUG] 响应内容太小: {len(r.content)} bytes")
                continue
            else:
                print(f"[DEBUG] HTTP错误: {r.status_code}")
                if attempt == 0:
                    continue  # 重试

        except requests.Timeout:
            if attempt == 0:
                print("[DEBUG] 超时，重试中……")
                continue
            return {"ok": False, "err": "图片生成超时（>90s），请点击重生成重试"}
        except Exception as e:
            print(f"[DEBUG] 异常: {e}")
            if attempt == 0:
                continue
            return {"ok": False, "err": f"生成错误：{str(e)[:60]}"}

    return {"ok": False, "err": "两次尝试均失败，请点击「重生成」重试"}


def make_zip(mod: dict) -> bytes:
    install_txt = """══════════════════════════════════════
饥荒联机版 MOD 安装指南
══════════════════════════════════════
① 解压本 ZIP 文件
② 将文件夹复制到：
   Windows: C:/Users/用户名/Documents/Klei/DoNotStarveTogether/mods/
   Steam:   Steam/steamapps/common/Don't Starve Together/mods/
③ 游戏主菜单 → 模组 → 找到 MOD → 启用
④ api_version 必须为 10，多人游戏所有玩家需安装

【贴图说明】
• modicon.tex / modicon.xml → MOD 主图标（第1张贴图）
• images/ 目录 → 其余变体贴图（第2-4张）
• 本工具最多支持生成 4 张贴图（1张主图标 + 3张变体）
• 如需更多贴图，可在 images/ 目录手动添加

══════════════════════════════════════
CREATED BY DST MOD GENERATOR · PRODUCER · LETITIA
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
    st.session_state.update({
        "mode": "home", "stage": "chat",
        "messages": [], "final_design": "",
        "design_spec": None, "visual_result": None,
        "sound_result": None, "preview_images": [],
        "preview_approved": False, "generating": False,
        "sound_audio_cache": {}, "show_producer_msg": False,
        "num_images": 1,
    })


def _get_image_prompt_for_idx(idx: int) -> str:
    """
    获取第 idx 张图对应的 prompt。
    优先从 all_prompts 读取，并强制截断到安全长度。
    """
    visual      = st.session_state.visual_result or {}
    all_prompts = visual.get("all_prompts", [])
    if idx < len(all_prompts):
        raw = all_prompts[idx].get("prompt", "")
    else:
        # 降级：用基础 prompt 加变体词
        base = visual.get("optimized_prompt", "")
        raw  = f"{base} variant {idx + 1}" if base else ""

    # 无论来源，都做清理截断，确保安全
    cleaned = _clean_for_url(raw, max_chars=220)
    if not cleaned or len(cleaned) < 8:
        cleaned = (
            "Don't Starve Together dark gothic item "
            "hand-drawn sketch muted parchment style"
        )
    return cleaned


def _get_image_label_for_idx(idx: int, default: str) -> str:
    """获取第 idx 张图的标签"""
    visual      = st.session_state.visual_result or {}
    all_prompts = visual.get("all_prompts", [])
    if idx < len(all_prompts):
        return all_prompts[idx].get("label", default)
    return f"{default} #{idx + 1}"


def _get_negative_prompt() -> str:
    """返回极短的固定 negative prompt（不从 visual_result 读取，避免过长）"""
    return (
        "realistic photo 3d render anime bright colors "
        "text watermark blurry modern"
    )

# ══════════════════════════════════════════════════════════════
# 🔊 音效合成 HTML
# ══════════════════════════════════════════════════════════════

def synth_audio_html(params: dict, element_id: str) -> str:
    if not params:
        return ""
    p          = params
    safe_id    = re.sub(r'\W', '', element_id)
    stype      = str(p.get("type", "sound")).upper()[:20]
    dur        = float(p.get("duration", 0.5))
    osc_type   = p.get("oscillator", "triangle")
    freq_start = float(p.get("frequency_start", 300))
    freq_end   = max(float(p.get("frequency_end", 150)), 20.0)
    gain_start = float(p.get("gain_start", 0.5))
    gain_end   = max(float(p.get("gain_end", 0.01)), 0.001)
    noise_mix  = float(p.get("noise_mix", 0.2))

    vibrato_js = ""
    if p.get("vibrato"):
        vibrato_js = """
        const lfo = ctx.createOscillator();
        lfo.frequency.value = 6;
        const lfoGain = ctx.createGain();
        lfoGain.gain.value = 50;
        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);
        lfo.start(now); lfo.stop(now + dur);
        """

    lfo_js = ""
    if p.get("lfo"):
        lfo_js = """
        const lfo2 = ctx.createOscillator();
        lfo2.frequency.value = 0.5;
        const lfo2Gain = ctx.createGain();
        lfo2Gain.gain.value = 30;
        lfo2.connect(lfo2Gain);
        lfo2Gain.connect(osc.frequency);
        lfo2.start(now); lfo2.stop(now + dur);
        """

    return f"""
<div style="background:rgba(15,30,15,0.70);border:1px solid #2a4a2a;
            border-radius:4px;padding:8px 12px;margin:4px 0;
            display:flex;align-items:center;gap:10px;">
  <button id="play_{safe_id}" onclick="playSynth_{safe_id}()"
    style="background:rgba(30,60,30,0.80);border:1px solid #4A9A50;
           color:#88cc88;padding:6px 18px;border-radius:4px;cursor:pointer;
           font-family:'IM Fell English SC',serif;font-size:0.85rem;
           letter-spacing:1px;transition:all 0.2s;white-space:nowrap;">
    ▶ 试听 · {stype}
  </button>
  <span style="font-size:0.70rem;color:#3a6a3a;font-style:italic;">
    合成音效 · {dur:.1f}s
  </span>
</div>
<script>
function playSynth_{safe_id}() {{
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const dur = {dur}; const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.type = '{osc_type}';
    osc.frequency.setValueAtTime({freq_start}, now);
    osc.frequency.exponentialRampToValueAtTime({freq_end}, now + dur);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime({gain_start}, now);
    gain.gain.exponentialRampToValueAtTime({gain_end}, now + dur);
    osc.connect(gain);
    if ({noise_mix} > 0.05) {{
        const bufSize = Math.ceil(ctx.sampleRate * dur);
        const noiseBuf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
        const data = noiseBuf.getChannelData(0);
        for (let i = 0; i < data.length; i++) {{
            data[i] = (Math.random() * 2 - 1) * {noise_mix};
        }}
        const noiseSrc = ctx.createBufferSource();
        noiseSrc.buffer = noiseBuf;
        const noiseGain = ctx.createGain();
        noiseGain.gain.setValueAtTime({noise_mix}, now);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + dur);
        noiseSrc.connect(noiseGain);
        noiseGain.connect(ctx.destination);
        noiseSrc.start(now); noiseSrc.stop(now + dur);
    }}
    {vibrato_js}
    {lfo_js}
    gain.connect(ctx.destination);
    osc.start(now); osc.stop(now + dur);
    const btn = document.getElementById('play_{safe_id}');
    btn.style.background = 'rgba(60,120,60,0.90)';
    btn.style.color = '#aaffaa';
    btn.textContent = '♫ 播放中…';
    setTimeout(() => {{
        btn.style.background = 'rgba(30,60,30,0.80)';
        btn.style.color = '#88cc88';
        btn.textContent = '▶ 试听 · {stype}';
    }}, dur * 1000 + 200);
}}
</script>
"""

# ══════════════════════════════════════════════════════════════
# 🔊 音效试听组件
# ══════════════════════════════════════════════════════════════

def _get_or_generate_sfx(cache_key: str, sfx_data: dict,
                          trigger_type: str = "pickup",
                          duration: str = "short") -> dict:
    cache = st.session_state.sound_audio_cache
    if cache_key in cache:
        return cache[cache_key]
    if sfx_data.get("synth_params"):
        result = {
            "ok":           True,
            "source":       "synth",
            "synth_params": sfx_data["synth_params"],
            "format":       "synth",
        }
    else:
        result = generate_sound_effect(
            search_keywords = sfx_data.get("trigger", ""),
            prompt_en       = sfx_data.get("description_cn", ""),
            faction         = sfx_data.get("faction", "neutral"),
            trigger_type    = trigger_type,
            duration        = duration,
        )
    return result


def render_sound_preview(sound: dict):
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">🔊 音效方案</p>',
                unsafe_allow_html=True)

    sfx_list = sound.get("sound_effects", [])
    ambient  = sound.get("ambient_sound", {})

    if not sfx_list and not ambient.get("needed"):
        st.markdown(
            '<p style="color:#3a5030;font-style:italic;text-align:center;'
            'padding:20px 0;">音效方案尚未凝聚……</p>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cache = st.session_state.sound_audio_cache

    faction_colors = {
        "shadow":  "#9a6aaa",
        "lunar":   "#6aaaca",
        "nature":  "#4A9A50",
        "neutral": "#8a8a6a",
    }

    for i, sfx in enumerate(sfx_list):
        trigger      = sfx.get("trigger", f"音效{i+1}")
        desc_cn      = sfx.get("description_cn", "")
        faction      = sfx.get("faction", "neutral")
        trigger_type = sfx.get("trigger_type", "pickup")
        cache_key    = f"sfx_{i}"
        color        = faction_colors.get(faction, "#4A9A50")

        st.markdown(f"""
        <div class="sound-card">
          <span class="sound-trigger" style="color:{color};">
            ▶ {trigger.upper()} · {faction.upper()}
          </span>
          <span class="sound-desc">{desc_cn}</span>
        </div>
        """, unsafe_allow_html=True)

        if cache_key in cache:
            entry = cache[cache_key]
            if entry.get("ok") and entry.get("source") == "synth":
                html = synth_audio_html(entry.get("synth_params", {}),
                                        f"sfx{i}")
                if html:
                    st.components.v1.html(html, height=55)
                if st.button("🔄 重新生成", key=f"regen_sfx_{i}",
                             use_container_width=True):
                    del st.session_state.sound_audio_cache[cache_key]
                    st.rerun()
            else:
                st.markdown(
                    f'<span style="color:#9a5a4a;font-size:0.78rem;">'
                    f'✕ {entry.get("err","未知错误")}</span>',
                    unsafe_allow_html=True)
                if st.button("↺ 重试", key=f"retry_sfx_{i}",
                             use_container_width=True):
                    del st.session_state.sound_audio_cache[cache_key]
                    st.rerun()
        else:
            if st.button("🎵 生成试听", key=f"gen_sfx_{i}",
                         use_container_width=True):
                with st.spinner(f"✦ 召唤「{trigger}」音效……"):
                    result = _get_or_generate_sfx(
                        cache_key, sfx, trigger_type)
                    st.session_state.sound_audio_cache[cache_key] = result
                st.rerun()

    if ambient.get("needed"):
        amb_desc = ambient.get("description_cn", "")
        amb_key  = "sfx_ambient"

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sound-card" style="border-color:#1a3a2a;">
          <span class="sound-trigger" style="color:#3a8a6a;">♪ AMBIENT</span>
          <span class="sound-desc">{amb_desc}</span>
        </div>
        """, unsafe_allow_html=True)

        if amb_key in cache:
            entry = cache[amb_key]
            if entry.get("ok"):
                html = synth_audio_html(
                    entry.get("synth_params", {}), "ambient")
                if html:
                    st.components.v1.html(html, height=55)
                if st.button("🔄 重新生成环境音", key="regen_ambient",
                             use_container_width=True):
                    del st.session_state.sound_audio_cache[amb_key]
                    st.rerun()
            else:
                st.markdown(
                    f'<span style="color:#9a5a4a;font-size:0.78rem;">'
                    f'✕ {entry.get("err","")}</span>',
                    unsafe_allow_html=True)
                if st.button("↺ 重试环境音", key="retry_ambient",
                             use_container_width=True):
                    del st.session_state.sound_audio_cache[amb_key]
                    st.rerun()
        else:
            if st.button("🎵 生成环境音试听", key="gen_ambient",
                         use_container_width=True):
                with st.spinner("✦ 编织环境音效……"):
                    result = _get_or_generate_sfx(
                        amb_key, ambient, "ambient", "medium")
                    st.session_state.sound_audio_cache[amb_key] = result
                st.rerun()

    all_keys = [f"sfx_{i}" for i in range(len(sfx_list))]
    if ambient.get("needed"):
        all_keys.append("sfx_ambient")
    uncached = [k for k in all_keys if k not in cache]

    if uncached:
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button(f"⚡ 一键生成全部音效（{len(uncached)} 个）",
                     key="gen_all_sfx", use_container_width=True):
            prog = st.progress(0)
            for idx, key in enumerate(uncached):
                if key == "sfx_ambient":
                    sfx_data = ambient
                    name     = "环境音"
                    t_type   = "ambient"
                    dur      = "medium"
                else:
                    n        = int(key.split("_")[1])
                    sfx_data = sfx_list[n]
                    name     = sfx_data.get("trigger", "")
                    t_type   = sfx_data.get("trigger_type", "pickup")
                    dur      = "short"

                with st.spinner(f"✦ 生成「{name}」({idx+1}/{len(uncached)})…"):
                    r = _get_or_generate_sfx(key, sfx_data, t_type, dur)
                    st.session_state.sound_audio_cache[key] = r
                prog.progress((idx + 1) / len(uncached))
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🎨 多图预览组件
# ══════════════════════════════════════════════════════════════

def _render_image_limit_notice(num_images: int):
    """渲染贴图数量限制说明"""
    st.markdown(f"""
    <div class="img-limit-notice">
      <span class="limit-icon">📌</span>
      <strong>贴图生成说明</strong><br>
      · 本工具最多支持生成 <strong>{MAX_IMAGES} 张</strong>游戏贴图
      （1 张主图标 + 最多 3 张变体）<br>
      · 当前已选择生成 <strong>{num_images} 张</strong>，
        第 1 张将自动用作 MOD 图标（modicon），
        其余存入 <code>images/</code> 目录<br>
      · 如需超过 {MAX_IMAGES} 张贴图，请下载 MOD 包后在
        <code>images/</code> 目录手动添加<br>
      · 图片由 <em>Pollinations AI</em> 生成，网络波动可能导致失败，
        可点击「🔄 重生成」单独重试
    </div>
    """, unsafe_allow_html=True)


def render_image_gallery(visual: dict, spec: dict):
    """渲染多图预览区"""
    images  = st.session_state.preview_images
    n       = len(images)
    obj     = spec.get("main_object", {})
    name_cn = obj.get("name_cn", "MOD 图标")

    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">🎨 外观预览</p>',
                unsafe_allow_html=True)

    if not images:
        st.markdown(
            '<p style="color:#4a3820;text-align:center;'
            'font-style:italic;padding:40px 0;">图腾尚未显现……</p>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 贴图限制说明
    _render_image_limit_notice(n)

    # 每行最多 2 列（避免过窄）
    cols_per_row = min(n, 2)
    rows = [images[i:i + cols_per_row]
            for i in range(0, n, cols_per_row)]

    for row_imgs in rows:
        cols = st.columns(len(row_imgs))
        for col, img_data in zip(cols, row_imgs):
            global_idx = images.index(img_data)
            is_icon    = (global_idx == 0)
            with col:
                st.markdown('<div class="img-card">', unsafe_allow_html=True)

                # 图标标识
                if is_icon:
                    st.markdown(
                        '<span style="display:block;text-align:center;'
                        'font-size:0.65rem;color:#C8A84B;letter-spacing:2px;'
                        'margin-bottom:4px;">★ MOD ICON</span>',
                        unsafe_allow_html=True)

                if img_data.get("url"):
                    st.image(img_data["url"], use_container_width=True)
                    label = img_data.get("label", name_cn)
                    st.markdown(
                        f'<span class="img-card-label">#{global_idx+1} {label}</span>',
                        unsafe_allow_html=True)
                    if img_data.get("err"):
                        st.markdown(
                            f'<span style="color:#9a5a4a;font-size:0.70rem;">'
                            f'⚠ {img_data["err"]}</span>',
                            unsafe_allow_html=True)
                else:
                    err_msg = img_data.get("err", "生成失败")
                    st.markdown(
                        f'<p style="color:#6a3820;text-align:center;'
                        f'font-style:italic;padding:20px 0;font-size:0.8rem;">'
                        f'#{global_idx+1} 生成失败<br>'
                        f'<span style="font-size:0.70rem;color:#4a2818;">'
                        f'{err_msg}</span></p>',
                        unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if st.button(f"🔄 重生成 #{global_idx+1}",
                             key=f"regen_img_{global_idx}",
                             use_container_width=True):
                    lbl = img_data.get("label", name_cn)
                    with st.spinner(f"✦ 重新召唤「{lbl}」……"):
                        prompt  = _get_image_prompt_for_idx(global_idx)
                        new_img = fetch_image(prompt)
                        if new_img["ok"]:
                            st.session_state.preview_images[global_idx] = {
                                "url":   new_img["url"],
                                "b64":   new_img["b64"],
                                "label": lbl,
                                "err":   "",
                            }
                        else:
                            st.session_state.preview_images[global_idx]["err"] = (
                                new_img["err"])
                            st.warning(f"生成失败：{new_img['err']}")
                    st.rerun()

    # 提示词预览（折叠）
    all_prompts = visual.get("all_prompts", [])
    if all_prompts:
        with st.expander("🔍 查看绘图 Prompt（调试用）", expanded=False):
            for i, ap in enumerate(all_prompts[:n]):
                raw_p   = ap.get("prompt", "")
                clean_p = _clean_for_url(raw_p, max_chars=220)
                st.markdown(
                    f'<p style="font-size:0.68rem;color:#4a3820;'
                    f'font-style:italic;margin:2px 0;">'
                    f'<strong style="color:#7a5a28;">#{i+1} {ap.get("label","")}</strong>'
                    f'（{len(clean_p)}字符）: {clean_p[:100]}…</p>',
                    unsafe_allow_html=True)

    # 一键重生成全部
    if st.button("🔄 重新生成全部图片",
                 key="regen_all_imgs", use_container_width=True):
        with st.spinner(f"✦ 重新召唤全部 {n} 张图腾……"):
            new_images = []
            for idx in range(n):
                prompt = _get_image_prompt_for_idx(idx)
                label  = (images[idx].get("label", name_cn)
                          if idx < len(images) else name_cn)
                img = fetch_image(prompt)
                new_images.append({
                    "url":   img["url"] if img["ok"] else None,
                    "b64":   img["b64"] if img["ok"] else None,
                    "label": label,
                    "err":   img.get("err", "") if not img["ok"] else "",
                })
            st.session_state.preview_images = new_images

        failed = [i + 1 for i, im in enumerate(new_images)
                  if not im.get("url")]
        if failed:
            st.warning(f"⚠️ 第 {failed} 张生成失败，可点击「🔄 重生成」单独重试")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🎨 预览页
# ══════════════════════════════════════════════════════════════

def render_preview_stage():
    spec   = st.session_state.design_spec or {}
    visual = st.session_state.visual_result or {}
    sound  = st.session_state.sound_result or {}
    obj    = spec.get("main_object", {})

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#C8A84B !important;">✦ 设计预览 · Design Preview</h3>
      <p>确认图像与音效无误后，令混沌永久凝固</p>
    </div>
    """, unsafe_allow_html=True)

    # ── MOD 规格卡 ──────────────────────────────────────
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">📋 MOD 设计规格</p>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="spec-grid">
      <div class="spec-item">
        <span class="spec-label">MOD NAME</span>
        <span class="spec-value">
          {spec.get("mod_name_cn","—")} · {spec.get("mod_name_en","—")}
        </span>
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
        <span class="spec-label">
          OBJECTS · {obj.get("name_cn","")}
          {" + " + str(len(spec.get("sub_objects",[]))) + " 个变体"
           if spec.get("sub_objects") else ""}
        </span>
        <span class="spec-value">{obj.get("appearance","—")}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    subs = spec.get("sub_objects", [])
    if subs:
        sub_html = "".join(
            f'<div class="spec-item">'
            f'<span class="spec-label">{s.get("name_cn","")}</span>'
            f'<span class="spec-value">{s.get("appearance","")[:60]}</span>'
            f'</div>'
            for s in subs
        )
        st.markdown(f'<div class="spec-grid">{sub_html}</div>',
                    unsafe_allow_html=True)

    stats      = spec.get("stats", {})
    stat_items = [(k.upper(), v) for k, v in stats.items() if v is not None]
    if stat_items:
        st.markdown(
            '<div class="spec-grid">'
            + "".join(
                f'<div class="spec-item">'
                f'<span class="spec-label">{k}</span>'
                f'<span class="spec-value">{v}</span></div>'
                for k, v in stat_items)
            + '</div>', unsafe_allow_html=True)

    recipe = spec.get("recipe", [])
    if recipe:
        st.markdown(
            f'<div class="spec-item" style="margin-top:7px;">'
            f'<span class="spec-label">RECIPE</span>'
            f'<span class="spec-value">{" ＋ ".join(recipe)}</span>'
            f'</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 贴图数量选择（图片未生成时显示）──────────────────
    if not st.session_state.preview_images:
        all_prompts     = visual.get("all_prompts", [])
        suggested_count = max(1, min(len(all_prompts), MAX_IMAGES)) if all_prompts else 1
        sub_count       = len(spec.get("sub_objects", []))

        st.markdown("""
        <p style="text-align:center;font-size:0.92rem;color:#C8A84B;
                  margin-bottom:4px;letter-spacing:1px;font-weight:600;">
          ✦ 选择需要生成的贴图数量
        </p>
        """, unsafe_allow_html=True)

        # 贴图限制说明（选择前展示）
        st.markdown(f"""
        <div class="img-limit-notice">
          <span class="limit-icon">📌</span>
          <strong>贴图生成限制说明</strong><br>
          · 本工具最多支持生成 <strong>{MAX_IMAGES} 张</strong>游戏贴图<br>
          · <strong>第 1 张</strong>自动作为 MOD 图标（modicon.tex），
            显示在游戏模组列表中<br>
          · <strong>第 2–{MAX_IMAGES} 张</strong>作为变体贴图，
            存入 MOD 包的 <code>images/</code> 目录<br>
          · 如需超过 {MAX_IMAGES} 张贴图，下载 MOD 包后可手动在
            <code>images/</code> 目录中添加<br>
          · 图片生成由 <em>Pollinations AI</em> 提供，网络波动可能导致个别张失败，
            可单独点击「🔄 重生成」重试
        </div>
        """, unsafe_allow_html=True)

        col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
        with col_n2:
            # 推荐数量提示
            if suggested_count > 1 or sub_count > 0:
                actual_suggest = max(suggested_count,
                                     min(sub_count + 1, MAX_IMAGES))
                st.markdown(
                    f'<p style="text-align:center;font-size:0.78rem;'
                    f'color:#7a5a28;margin-bottom:4px;">'
                    f'✦ 检测到 {max(sub_count, suggested_count - 1)} 种变体对象，'
                    f'推荐生成 <strong style="color:#C8A84B;">'
                    f'{actual_suggest}</strong> 张</p>',
                    unsafe_allow_html=True)
            else:
                actual_suggest = 1

            num = st.select_slider(
                "贴图数量",
                options=list(range(1, MAX_IMAGES + 1)),
                value=min(actual_suggest, MAX_IMAGES),
                key="num_images_slider",
                label_visibility="collapsed",
            )
            st.session_state.num_images = num

            # 动态说明
            slot_desc = "（仅主图标）" if num == 1 else f"（1 张主图标 + {num-1} 张变体）"
            st.markdown(
                f'<p style="text-align:center;font-size:0.80rem;'
                f'color:#9a7a48;margin-top:4px;">'
                f'将生成 <strong style="color:#D4A843;">{num}</strong> 张贴图 '
                f'{slot_desc}</p>',
                unsafe_allow_html=True)

        col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
        with col_g2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("✦ 生成贴图预览",
                         key="gen_imgs_btn", use_container_width=True):
                new_images = []
                prog = st.progress(0)
                failed_list = []

                for idx in range(num):
                    label  = _get_image_label_for_idx(idx, obj.get("name_cn", "MOD图标"))
                    prompt = _get_image_prompt_for_idx(idx)
                    if not prompt:
                        prompt = (
                            "Don't Starve Together dark gothic item "
                            "hand-drawn sketch muted parchment style"
                        )

                    with st.spinner(
                            f"✦ 生成第 {idx+1}/{num} 张「{label}」……"):
                        img = fetch_image(prompt)
                        entry = {
                            "url":   img["url"] if img["ok"] else None,
                            "b64":   img["b64"] if img["ok"] else None,
                            "label": label,
                            "err":   img.get("err", "") if not img["ok"] else "",
                        }
                        new_images.append(entry)
                        if not img["ok"]:
                            failed_list.append(idx + 1)

                    prog.progress((idx + 1) / num)

                st.session_state.preview_images = new_images

                if failed_list:
                    st.warning(
                        f"⚠️ 第 {failed_list} 张生成失败，"
                        f"可在预览区点击「🔄 重生成」单独重试")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

    # ── 图片 + 音效并排 ─────────────────────────────────
    col_img, col_snd = st.columns([1, 1])
    with col_img:
        render_image_gallery(visual, spec)
    with col_snd:
        render_sound_preview(sound)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 操作按钮 ────────────────────────────────────────
    st.markdown("""
    <p style="text-align:center;font-size:0.82rem;color:#4a3820;
              font-style:italic;margin-bottom:10px;letter-spacing:1px;">
      ✦ 确认图像与音效无误后，令混沌永久凝固 ✦
    </p>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("⚙ 确认并铸造 MOD · Forge",
                     key="confirm_forge", use_container_width=True):
            st.session_state.preview_approved = True
            st.session_state.stage = "generating"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("✏ 继续调整设计",
                     key="back_to_chat", use_container_width=True):
            st.session_state.stage = "chat"
            st.rerun()
    with col_b2:
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("✕ 放弃，返回主页",
                     key="abort_preview", use_container_width=True):
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

    with st.spinner("✦ 暗影法典正在书写 Lua 代码……"):
        bar.progress(20)
        result = design_with_llm(
            st.session_state.final_design,
            st.session_state.messages
        )
    bar.progress(45)

    with st.spinner("✦ 封印永恒形象……"):
        images = st.session_state.get("preview_images", [])
        files  = result.setdefault("data", {}).setdefault("files", {})

        sealed = 0
        if images:
            first = images[0]
            if first.get("b64"):
                files["modicon.tex"] = base64.b64decode(first["b64"])
                files["modicon.xml"] = generate_atlas_xml()
                sealed += 1

            for idx, img_data in enumerate(images[1:], start=2):
                if img_data.get("b64"):
                    label = img_data.get("label", f"variant_{idx}")
                    safe  = re.sub(r'[^\w]', '_', label)
                    files[f"images/{safe}.png"] = base64.b64decode(
                        img_data["b64"])
                    sealed += 1

            st.success(f"✦ {sealed} 张图像已封印！")
        else:
            st.warning("永恒形象缺失，跳过。")
    bar.progress(65)

    with st.spinner("✦ 封印音效……"):
        cache    = st.session_state.get("sound_audio_cache", {})
        sound    = st.session_state.get("sound_result", {}) or {}
        sfx_list = sound.get("sound_effects", [])
        packed   = 0

        for i, sfx in enumerate(sfx_list):
            key   = f"sfx_{i}"
            entry = cache.get(key, {})
            if entry.get("ok") and entry.get("source") != "synth":
                trig = sfx.get("trigger", "sfx").replace(" ", "_")
                fmt  = entry.get("format", "wav")
                files[f"sounds/{trig}_{i}.{fmt}"] = entry["audio_bytes"]
                packed += 1

        if "sfx_ambient" in cache:
            entry = cache["sfx_ambient"]
            if entry.get("ok") and entry.get("source") != "synth":
                fmt = entry.get("format", "wav")
                files[f"sounds/ambient.{fmt}"] = entry["audio_bytes"]
                packed += 1

        if packed:
            st.success(f"✦ 已封印 {packed} 个音效文件！")
        else:
            st.info("音效为合成预览，未打包（合成音效在游戏内由代码实现）。")
    bar.progress(85)

    with st.spinner("✦ 归入典藏……"):
        st.session_state.messages.append({
            "role":    "assistant",
            "content": result.get("text", "✦ Mod 铸造完毕。")
        })
        d = result.get("data", {})
        if d:
            first_url = (st.session_state.preview_images[0].get("url")
                         if st.session_state.preview_images else None)
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
                "image_url": first_url,
                "all_images": [
                    img.get("url") for img in st.session_state.preview_images
                    if img.get("url")
                ],
            })
    bar.progress(100)

    st.session_state.stage      = "done"
    st.session_state.generating = False
    st.rerun()

# ══════════════════════════════════════════════════════════════
# 💬 对话阶段
# ══════════════════════════════════════════════════════════════

def _enter_preview():
    with st.spinner("✦ 永恒大陆的使者正在整理设计蓝图……"):
        spec = summarize_design(st.session_state.messages)
        st.session_state.design_spec  = spec
        st.session_state.final_design = json.dumps(
            spec, ensure_ascii=False, indent=2)

    with st.spinner("✦ 准备视觉方案……"):
        visual = optimize_visual_prompt(spec)
        st.session_state.visual_result = visual

        all_prompts = visual.get("all_prompts", [])
        print(f"[DEBUG] 生成 {len(all_prompts)} 条图片 prompt：")
        for i, ap in enumerate(all_prompts):
            raw   = ap.get("prompt", "")
            clean = _clean_for_url(raw, max_chars=220)
            print(f"  #{i+1} [{ap.get('label','')}] 原始={len(raw)}字符 "
                  f"清理后={len(clean)}字符: {clean[:80]}")

    with st.spinner("✦ 编排音效方案……"):
        sound = generate_sound_prompts(spec)
        st.session_state.sound_result = sound

        sfx_list = sound.get("sound_effects", [])
        print(f"[DEBUG] 生成 {len(sfx_list)} 条音效：")
        for sfx in sfx_list:
            print(f"  [{sfx.get('faction','')}] {sfx.get('trigger','')}："
                  f"{sfx.get('description_cn','')}")

    st.session_state.preview_images    = []
    st.session_state.sound_audio_cache = {}
    st.session_state.num_images        = 1
    st.session_state.stage             = "preview"
    st.rerun()


def render_chat_stage(mode: str):
    is_explore = (mode == "explore")

    if is_explore:
        st.markdown("""
        <div class="mode-header">
          <h3 style="color:#4CAF50 !important;">👁 迷雾探路者 · Shadow Explore</h3>
          <p>与永恒大陆的使者充分对话，明确设计后点击「预览并确认」</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="mode-header">
          <h3 style="color:#D4A843 !important;">⚡ 意志铸剑者 · Rapid Forge</h3>
          <p>输入你的构想，永恒大陆的使者将细化设计，确认后点击「预览并确认」</p>
        </div>
        """, unsafe_allow_html=True)

    render_chat(st.session_state.messages)

    placeholder = ("低语你的构想，永恒大陆的使者将倾听……"
                   if is_explore else "将你的意志化为文字……")
    user_inp = st.chat_input(placeholder)

    if user_inp:
        st.session_state.messages.append({"role": "user", "content": user_inp})
        with st.spinner("✦ 永恒大陆的使者正在回应……"):
            try:
                if is_explore:
                    r = explore_with_llm(st.session_state.messages)
                else:
                    r = rapid_with_llm(st.session_state.messages)
                reply = (r.get("text", str(r))
                         if isinstance(r, dict) else str(r))
            except Exception as exc:
                reply = f"（永恒大陆沉默了：{exc}）"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if len(st.session_state.messages) >= 2:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align:center;font-size:0.82rem;color:#5a4020;
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

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 归返主页 · Return", key=f"back_{mode}"):
        reset_to_home()
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
# 📖 弹窗：创作者想说
# ══════════════════════════════════════════════════════════════

@st.dialog("✦ 创作者想说 ✦", width="large")
def show_producer_message():
    st.markdown("""
    <div style="font-family:'IM Fell English SC',serif;font-size:1rem;
                line-height:2;color:#D4BC88;text-align:justify;">
      <p style="margin-bottom:18px;">
        这个 <strong>MOD 生成器</strong>诞生于对《饥荒联机版》的热爱，
        以及对<strong>创造自由</strong>的向往。
      </p>
      <p style="margin-bottom:18px;">
        核心使命：<strong style="color:#FFD700;">让每一位想在游戏世界中自由创造、
        但不会编写代码的玩家，都能实现真正的"创造模式"</strong>。
      </p>
      <p style="margin-bottom:10px;">
        <strong style="color:#C8A84B;">现已支持：</strong>
      </p>
      <ul style="margin-left:28px;margin-bottom:20px;line-height:2;">
        <li>多对象MOD设计（如四种花各有独立设计）</li>
        <li>每个对象独立贴图生成（1–4张，各对应真实内容）</li>
        <li>阵营感知音效（影系/月亮系/自然系各有特色）</li>
        <li>完整Lua代码框架一键生成</li>
        <li>打包ZIP直接安装</li>
      </ul>
      <p style="margin-bottom:10px;">
        <strong style="color:#C8A84B;">贴图生成说明：</strong>
      </p>
      <ul style="margin-left:28px;margin-bottom:20px;line-height:2;">
        <li>最多支持生成 <strong>4 张</strong>贴图（当前工具上限）</li>
        <li>第 1 张自动作为 MOD 图标，其余存入 images/ 目录</li>
        <li>如 AI 生成失败，可点击「🔄 重生成」单独重试</li>
        <li>如需更多贴图，下载 MOD 包后手动在 images/ 目录添加</li>
      </ul>
      <p style="text-align:center;margin-top:28px;color:#D4A843;
                font-style:italic;font-size:1.1rem;letter-spacing:2px;">
        ✦ 愿你的创造力在永恒大陆中永不熄灭 ✦
      </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("关闭", use_container_width=True, key="close_producer"):
        st.session_state.show_producer_msg = False
        st.rerun()

# ══════════════════════════════════════════════════════════════
# 📖 弹窗：MOD 安装教程
# ══════════════════════════════════════════════════════════════

@st.dialog("📖 MOD 安装 & 使用教程", width="large")
def show_install_guide():
    st.markdown("### 一、下载 MOD")
    st.write("在左侧「MOD 典藏库」中点击「⬇ 下载 MOD 包」，获得 .zip 压缩包。")
    st.markdown("### 二、安装步骤")
    st.write("1. **解压**下载的 ZIP 文件")
    st.write("2. 将文件夹复制到 MOD 目录：")
    st.code("C:/Users/用户名/Documents/Klei/DoNotStarveTogether/mods/",
            language="")
    st.caption("👆 Windows 路径")
    st.code("Steam/steamapps/common/Don't Starve Together/mods/", language="")
    st.caption("👆 Steam 路径")
    st.write("3. 游戏主菜单 → **「模组」** → 找到 MOD → **「启用」**")
    st.write("4. 创建存档，MOD 即刻生效 ✨")
    st.markdown("### 三、注意事项")
    st.warning("⚠️ `api_version` 必须为 **10**")
    st.warning("⚠️ 多人游戏时所有玩家需安装")
    st.markdown("### 四、贴图说明")
    st.info(f"📌 本工具最多生成 **{MAX_IMAGES} 张**贴图（1 张主图标 + 最多 3 张变体）")
    st.write("• 第一张贴图自动作为 `modicon`（MOD图标）")
    st.write(f"• 第 2–{MAX_IMAGES} 张存放在 `images/` 目录，可在代码中按名称引用")
    st.write(f"• 如需超过 {MAX_IMAGES} 张，下载后在 `images/` 目录手动添加即可")
    st.markdown("### 五、音效说明")
    st.write("• 音效为 Web Audio 合成预览，正式发布时建议替换为 .wav 文件")
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#D4A843;font-style:italic;'>"
        "✦ 祝你在永恒大陆玩得愉快 ✦</p>",
        unsafe_allow_html=True)
    if st.button("关闭", use_container_width=True, key="close_install"):
        st.session_state.show_install_guide = False
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
          当你已明晰 Mod 的核心法则<br>
          将你的疯狂构想直接锻造成现实
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
          当灵感如迷雾般在脑海低语<br>
          与暗影对话，让蓝图逐渐清晰
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
            st.session_state.update({
                "mode": "rapid", "stage": "chat",
                "messages": [], "final_design": "",
                "design_spec": None, "sound_audio_cache": {},
                "preview_images": [], "num_images": 1,
                "show_producer_msg": False,
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("👁 探索设计 · Shadow Explore",
                     key="k_explore", use_container_width=True):
            st.session_state.update({
                "mode": "explore", "stage": "chat",
                "messages": [], "final_design": "",
                "design_spec": None, "sound_audio_cache": {},
                "preview_images": [], "num_images": 1,
                "show_producer_msg": False,
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="creator-tag">
      <p class="creator-name">✦ PRODUCER · LETITIA ✦</p>
      <hr class="creator-divider">
      <p>1135462669@qq.com</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button("💭 创作者想说 · FROM PRODUCER",
                     use_container_width=True, key="btn_producer_msg"):
            st.session_state.show_producer_msg = True
            st.rerun()

    if st.session_state.show_producer_msg:
        show_producer_message()

# ══════════════════════════════════════════════════════════════
# 🚦 路由
# ══════════════════════════════════════════════════════════════

mode  = st.session_state.mode
stage = st.session_state.stage

if mode == "home":
    render_home()
elif mode in ("explore", "rapid"):
    if   stage == "chat":       render_chat_stage(mode)
    elif stage == "preview":    render_preview_stage()
    elif stage == "generating": render_generating_stage()
    elif stage == "done":       render_done_stage()

# ══════════════════════════════════════════════════════════════
# 📦 侧边栏
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ✦ MOD 典藏库")
    st.caption("— Mod Archive —")

    if not st.session_state.generated_mods:
        st.markdown("""
        <p style="color:#4a3018;font-style:italic;font-size:0.82rem;
                  text-align:center;margin-top:14px;">
          典藏库空空如也……<br>
          <em>The archive awaits your creations...</em>
        </p>
        """, unsafe_allow_html=True)
    else:
        for mod in reversed(st.session_state.generated_mods):
            label = f"📜 {mod.get('name_cn') or mod['name']}"
            with st.expander(label):
                st.markdown(f"**{mod['date']}**  ·  `{mod['name']}`")
                if mod.get("desc"):
                    desc_text = mod["desc"][:100] + ("..." if len(mod["desc"]) > 100 else "")
                    st.caption(desc_text)

                all_imgs = mod.get("all_images", [])
                if all_imgs:
                    thumb_cols = st.columns(min(len(all_imgs), 3))
                    for tc, img_url in zip(thumb_cols, all_imgs[:3]):
                        with tc:
                            st.image(img_url, use_container_width=True)
                elif mod.get("image_url"):
                    st.image(mod["image_url"], width=110)

                # 贴图数量提示
                img_count = len(all_imgs)
                if img_count > 0:
                    st.caption(
                        f"📌 包含 {img_count} 张贴图"
                        f"{'（已达上限）' if img_count >= MAX_IMAGES else ''}")

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
                    st.session_state.update({
                        "mode": "explore", "stage": "chat",
                        "final_design": mod["design"],
                        "messages": [{"role": "user",
                                      "content": mod.get("design", "")}],
                        "sound_audio_cache": {},
                        "preview_images": [], "num_images": 1,
                        "show_producer_msg": False,
                    })
                    st.rerun()

    st.divider()
    if st.button("📖 MOD 安装教程",
                 use_container_width=True, key="btn_install_guide"):
        st.session_state.show_install_guide = True
        st.rerun()

    st.divider()
    st.caption(f"本次对话：{len(st.session_state.messages)} 条")
    st.caption(f"已生成 Mod：{len(st.session_state.generated_mods)} 个")
    st.divider()
    if st.button("🗑 清除全部记录", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ══ 安装教程弹窗（全局）══
if st.session_state.show_install_guide:
    show_install_guide()
