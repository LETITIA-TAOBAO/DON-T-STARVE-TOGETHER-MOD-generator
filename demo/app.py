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
    "mode":               "home",
    "messages":           [],
    "generated_mods":     [],
    "final_design":       "",
    "design_spec":        None,
    "visual_result":      None,
    "sound_result":       None,
    "preview_image_url":  None,
    "preview_image_b64":  None,
    "preview_approved":   False,
    "stage":              "chat",
    "generating":         False,
    "sound_audio_cache":  {},
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
    content:""; position:fixed; inset:0;
    background:rgba(8,4,0,0.45); z-index:0; pointer-events:none;
}}
.stAppViewContainer .stMainBlockContainer,
.block-container {{
    background:rgba(20,11,3,0.55) !important;
    backdrop-filter:blur(2px);
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
    background:rgba(15,8,2,0.82); border:2px solid #7B5820;
    border-top:3px solid #C8A84B; border-bottom:3px solid #C8A84B;
    padding:36px 44px 30px; border-radius:4px; text-align:center;
    margin:10px auto 28px; max-width:820px;
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
    font-family:'Cinzel',serif !important; color:#7B5820 !important;
    font-size:0.8rem; letter-spacing:4px; margin-top:5px;
}}
.banner-divider {{ border:none; border-top:1px solid #5a3a10; width:40%; margin:16px auto; }}
.banner-quote {{
    font-family:'IM Fell English SC',serif !important;
    font-size:0.98rem; line-height:1.9; color:#C8A86A !important; font-style:italic;
}}

.mode-cards {{ display:flex; gap:24px; justify-content:center; margin:0 auto 28px; max-width:880px; }}
.mode-card {{
    flex:1; max-width:420px; background:rgba(18,10,3,0.84);
    border:2px solid #5a3a10; border-radius:6px; padding:26px 22px 22px;
    text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.5); position:relative; overflow:hidden;
}}
.mode-card::before {{
    content:""; position:absolute; top:0;left:0;right:0; height:3px;
    background:linear-gradient(90deg,transparent,#C8A84B,transparent);
}}
.mode-card-icon  {{ font-size:2.2rem; margin-bottom:8px; display:block; }}
.mode-card-title {{
    font-family:'Cinzel Decorative',serif !important;
    font-size:1.1rem !important; color:#D4A843 !important; margin:0 0 4px !important;
}}
.mode-card-sub {{
    font-family:'Cinzel',serif !important; font-size:0.7rem !important;
    color:#7a5a28 !important; letter-spacing:3px; margin-bottom:12px !important; display:block;
}}
.mode-card-divider {{ border:none; border-top:1px solid #3a2008; margin:10px auto; width:60%; }}
.mode-card-desc {{ font-size:0.88rem !important; line-height:1.8 !important; color:#B89A62 !important; margin:0 !important; }}
.mode-card-en {{ font-style:italic !important; color:#5a4020 !important; font-size:0.76em !important; display:block !important; margin-top:10px !important; }}
.mode-card-hint {{
    display:inline-block; margin-top:16px; padding:5px 18px;
    border:1px solid #7B5820; border-radius:3px;
    font-size:0.8rem !important; color:#C8A84B !important;
    background:rgba(100,60,10,0.18); letter-spacing:1px;
}}

div[data-testid="stButton"]>button {{
    background:rgba(20,10,3,0.87) !important; border:2px solid #7a5020 !important;
    color:#D4A843 !important; font-family:'IM Fell English SC',serif !important;
    font-size:1rem !important; letter-spacing:1px !important;
    padding:10px 24px !important; border-radius:4px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.5) !important;
    text-shadow:0 0 8px rgba(200,160,60,0.35) !important;
}}
div[data-testid="stButton"]>button:hover {{
    background:rgba(50,25,5,0.96) !important; border-color:#C8A84B !important;
    color:#FFD700 !important; transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(0,0,0,0.6),0 0 15px rgba(200,168,75,0.2) !important;
}}
.primary-btn div[data-testid="stButton"]>button {{
    background:rgba(55,22,5,0.92) !important; border:2px solid #C8A84B !important;
    font-size:1.08rem !important; padding:13px 32px !important; letter-spacing:2px !important;
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
    font-family:'IM Fell English SC',serif !important; font-size:0.93rem !important;
    line-height:1.78 !important; color:#D4BC88 !important; white-space:pre-wrap;
}}

.preview-box {{
    background:rgba(12,6,1,0.90); border:2px solid #6B5018;
    border-radius:6px; padding:22px; margin:14px 0;
}}
.preview-box-title {{
    font-family:'Cinzel Decorative',serif !important; font-size:1.05rem !important;
    color:#D4A843 !important; text-align:center; margin-bottom:14px !important; letter-spacing:2px;
}}
.spec-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
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
.sound-desc {{ font-size:0.87rem !important; color:#C0D8C0 !important; display:block; margin-bottom:4px; }}
.sound-prompt {{ font-size:0.68rem !important; color:#3a5a3a !important; font-style:italic !important; }}

audio {{
    width:100%; height:34px; margin-top:6px;
    filter:sepia(0.4) saturate(0.7) brightness(0.9);
    border-radius:4px;
}}

.gen-box {{
    background:rgba(12,6,1,0.92); border:2px solid #7a4010;
    border-top:3px solid #C8A84B; border-radius:6px;
    padding:30px; text-align:center; margin:14px auto; max-width:600px;
}}

[data-testid="stChatInput"] {{ background:rgba(15,8,2,0.82) !important; border-top:1px solid rgba(139,100,32,0.35) !important; }}
[data-testid="stChatInput"] textarea {{
    background:rgba(20,11,3,0.93) !important; border:1px solid #4a3010 !important;
    color:#EDD9A3 !important; font-family:'IM Fell English SC',serif !important; border-radius:4px !important;
}}
[data-testid="stChatInput"] textarea:focus {{ border-color:#C8A84B !important; box-shadow:0 0 10px rgba(200,168,75,0.18) !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color:#5a4028 !important; font-style:italic !important; }}

.stProgress>div>div>div>div {{
    background:linear-gradient(90deg,#6B3A08,#C8A84B,#F0D070) !important; border-radius:4px !important;
}}
.st-expander {{ background:rgba(20,11,3,0.74) !important; border:1px solid #4a3010 !important; border-radius:4px !important; }}
hr {{ border:none !important; border-top:1px solid rgba(139,100,32,0.28) !important; margin:16px 0 !important; }}
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:rgba(10,5,0,0.3); }}
::-webkit-scrollbar-thumb {{ background:#5a3810; border-radius:3px; }}
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


def fetch_image(prompt: str, negative: str = "") -> dict:
    """调用 Pollinations.ai 生成饥荒风格图片"""
    try:
        full_negative = (
            "realistic, 3d render, photographic, bright saturated colors, "
            "anime, smooth shading, modern, clean lines, digital painting, "
            "gradient, text, watermark, logo, blurry, " + negative
        ).strip(", ")
        enc     = prompt.replace(" ", "+").replace("&", "%26")
        neg_enc = full_negative.replace(" ", "+").replace("&", "%26")
        url = (
            f"https://image.pollinations.ai/prompt/{enc}"
            f"?width=512&height=512&nologo=true"
            f"&negative={neg_enc}"
            f"&model=flux"
            f"&seed={int(datetime.now().timestamp())}"
        )
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 1000:
            return {"ok": True, "b64": base64.b64encode(r.content).decode(), "url": url}
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "err": str(e)}


def make_zip(mod: dict) -> bytes:
    install_txt = """══════════════════════════════════════
   饥荒联机版 MOD 安装指南
══════════════════════════════════════

【手动安装】
① 解压本 ZIP 文件
② 将解压后的文件夹复制到：
   Windows:
   C:/Users/你的用户名/Documents/Klei/
   DoNotStarveTogether/mods/

   Steam 路径:
   Steam/steamapps/common/
   Don't Starve Together/mods/

③ 启动游戏 → 主菜单 → 模组
   找到本 Mod → 点击启用

④ 创建或进入存档，Mod 即刻生效

⚠️ 注意：
  - api_version 必须为 10
  - 多人游戏所有玩家需安装
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
        "mode":              "home",
        "stage":             "chat",
        "messages":          [],
        "final_design":      "",
        "design_spec":       None,
        "visual_result":     None,
        "sound_result":      None,
        "preview_image_url": None,
        "preview_image_b64": None,
        "preview_approved":  False,
        "generating":        False,
        "sound_audio_cache": {},
    })


# ══════════════════════════════════════════════════════════════
# 🔊 音效合成 HTML 生成
# ══════════════════════════════════════════════════════════════

def _synth_audio_html(params: dict, element_id: str) -> str:
    """生成 Web Audio API 合成音效的 HTML/JS"""
    p = params
    vibrato_js = ""
    if p.get("vibrato"):
        vibrato_js = """
        const lfo = ctx.createOscillator();
        lfo.frequency.value = 6;
        const lfoGain = ctx.createGain();
        lfoGain.gain.value = 50;
        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);
        lfo.start(now);
        lfo.stop(now + dur);
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
        lfo2.start(now);
        lfo2.stop(now + dur);
        """

    safe_id     = element_id.replace("-", "_")
    stype       = p.get("type", "sound").upper()
    dur         = p.get("duration", 0.5)
    osc_type    = p.get("oscillator", "triangle")
    freq_start  = p.get("frequency_start", 300)
    freq_end    = max(p.get("frequency_end", 150), 20)
    gain_start  = p.get("gain_start", 0.5)
    gain_end    = max(p.get("gain_end", 0.01), 0.001)
    noise_mix   = p.get("noise_mix", 0.2)

    return f"""
    <div style="background:rgba(15,30,15,0.70);border:1px solid #2a4a2a;
                border-radius:4px;padding:8px 12px;margin:4px 0;
                display:flex;align-items:center;gap:10px;">
      <button id="play_{safe_id}" onclick="playSynth_{safe_id}()"
        style="background:rgba(30,60,30,0.80);border:1px solid #4A9A50;
               color:#88cc88;padding:6px 18px;border-radius:4px;
               cursor:pointer;font-family:'IM Fell English SC',serif;
               font-size:0.85rem;letter-spacing:1px;
               transition:all 0.2s;white-space:nowrap;">
        ▶ 试听 · {stype}
      </button>
      <span style="font-size:0.70rem;color:#3a6a3a;font-style:italic;">
        合成音效 · {dur:.1f}s
      </span>
    </div>
    <script>
    function playSynth_{safe_id}() {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const dur = {dur};
        const now = ctx.currentTime;

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
            noiseSrc.start(now);
            noiseSrc.stop(now + dur);
        }}

        {vibrato_js}
        {lfo_js}

        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + dur);

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

def render_sound_preview(sound: dict):
    """渲染可试听的音效方案"""
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

    # ── 各触发音效 ──
    for i, sfx in enumerate(sfx_list):
        trigger   = sfx.get("trigger", f"音效{i+1}")
        desc_cn   = sfx.get("description_cn", "")
        prompt_en = sfx.get("prompt_en", "")
        keywords  = sfx.get("search_keywords", "")
        duration  = sfx.get("duration", "short")
        cache_key = f"sfx_{i}"

        st.markdown(f"""
        <div class="sound-card">
          <span class="sound-trigger">▶ {trigger.upper()}</span>
          <span class="sound-desc">{desc_cn}</span>
          <span class="sound-prompt">{prompt_en}</span>
        </div>
        """, unsafe_allow_html=True)

        if cache_key in cache:
            entry = cache[cache_key]
            if entry.get("ok"):
                if entry.get("source") == "synth":
                    params = entry.get("synth_params", {})
                    html   = _synth_audio_html(params, f"sfx{i}")
                    st.components.v1.html(html, height=55)
                else:
                    fmt = entry.get("format", "wav")
                    st.audio(entry["audio_bytes"], format=f"audio/{fmt}")
                    st.download_button(
                        "⬇ 下载",
                        data=entry["audio_bytes"],
                        file_name=f"{trigger}_{i}.{fmt}",
                        mime=f"audio/{fmt}",
                        key=f"dl_sfx_{i}",
                        use_container_width=True,
                    )
                if st.button("🔄 重新生成",
                             key=f"regen_sfx_{i}", use_container_width=True):
                    del st.session_state.sound_audio_cache[cache_key]
                    st.rerun()
            else:
                st.markdown(
                    f'<span style="color:#9a5a4a;font-size:0.78rem;">'
                    f'✕ {entry.get("err","未知错误")}</span>',
                    unsafe_allow_html=True)
                if st.button("↺ 重试",
                             key=f"retry_sfx_{i}", use_container_width=True):
                    del st.session_state.sound_audio_cache[cache_key]
                    st.rerun()
        else:
            if st.button(f"🎵 生成试听",
                         key=f"gen_sfx_{i}", use_container_width=True):
                with st.spinner(f"✦ 召唤「{trigger}」音效……"):
                    result = generate_sound_effect(keywords, prompt_en, duration)
                    st.session_state.sound_audio_cache[cache_key] = result
                st.rerun()

    # ── 环境音 ──
    if ambient.get("needed"):
        amb_desc   = ambient.get("description_cn", "")
        amb_prompt = ambient.get("prompt_en", "")
        amb_kw     = ambient.get("search_keywords", "")
        amb_key    = "sfx_ambient"

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sound-card" style="border-color:#1a3a2a;">
          <span class="sound-trigger" style="color:#3a8a6a;">♪ AMBIENT</span>
          <span class="sound-desc">{amb_desc}</span>
          <span class="sound-prompt">{amb_prompt}</span>
        </div>
        """, unsafe_allow_html=True)

        if amb_key in cache:
            entry = cache[amb_key]
            if entry.get("ok"):
                if entry.get("source") == "synth":
                    params = entry.get("synth_params", {})
                    html   = _synth_audio_html(params, "ambient")
                    st.components.v1.html(html, height=55)
                else:
                    fmt = entry.get("format", "wav")
                    st.audio(entry["audio_bytes"], format=f"audio/{fmt}")
                if st.button("🔄 重新生成环境音",
                             key="regen_ambient", use_container_width=True):
                    del st.session_state.sound_audio_cache[amb_key]
                    st.rerun()
            else:
                st.markdown(
                    f'<span style="color:#9a5a4a;font-size:0.78rem;">'
                    f'✕ {entry.get("err","")}</span>',
                    unsafe_allow_html=True)
                if st.button("↺ 重试环境音",
                             key="retry_ambient", use_container_width=True):
                    del st.session_state.sound_audio_cache[amb_key]
                    st.rerun()
        else:
            if st.button("🎵 生成环境音试听",
                         key="gen_ambient", use_container_width=True):
                with st.spinner("✦ 编织环境音效……"):
                    result = generate_sound_effect(amb_kw, amb_prompt, "medium")
                    st.session_state.sound_audio_cache[amb_key] = result
                st.rerun()

    # ── 一键全部生成 ──
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
                    kw   = ambient.get("search_keywords", "")
                    prmt = ambient.get("prompt_en", "")
                    dur  = "medium"
                    name = "环境音"
                else:
                    n    = int(key.split("_")[1])
                    s    = sfx_list[n]
                    kw   = s.get("search_keywords", "")
                    prmt = s.get("prompt_en", "")
                    dur  = s.get("duration", "short")
                    name = s.get("trigger", "")
                with st.spinner(f"✦ 生成「{name}」({idx+1}/{len(uncached)})…"):
                    r = generate_sound_effect(kw, prmt, dur)
                    st.session_state.sound_audio_cache[key] = r
                prog.progress((idx + 1) / len(uncached))
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🎨 预览页
# ══════════════════════════════════════════════════════════════

def render_preview_stage():
    spec   = st.session_state.design_spec   or {}
    visual = st.session_state.visual_result  or {}
    sound  = st.session_state.sound_result   or {}
    obj    = spec.get("main_object", {})

    st.markdown("""
    <div class="mode-header">
      <h3 style="color:#C8A84B !important;">✦ 设计预览 · Design Preview</h3>
      <p>确认图像与音效无误后，令混沌永久凝固</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 规格卡 ──
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.markdown('<p class="preview-box-title">📋 MOD 设计规格</p>',
                unsafe_allow_html=True)
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

    stats      = spec.get("stats", {})
    stat_items = [(k.upper(), v) for k, v in stats.items() if v is not None]
    if stat_items:
        st.markdown(
            '<div class="spec-grid">'
            + "".join(
                f'<div class="spec-item"><span class="spec-label">{k}</span>'
                f'<span class="spec-value">{v}</span></div>'
                for k, v in stat_items)
            + '</div>', unsafe_allow_html=True)

    recipe = spec.get("recipe", [])
    if recipe:
        st.markdown(
            f'<div class="spec-item" style="margin-top:7px;">'
            f'<span class="spec-label">RECIPE</span>'
            f'<span class="spec-value">{" ＋ ".join(recipe)}</span></div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 图片 + 音效 并列 ──
    col_img, col_snd = st.columns([1, 1])

    with col_img:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown('<p class="preview-box-title">🎨 外观预览</p>',
                    unsafe_allow_html=True)
        img_url = st.session_state.preview_image_url
        if img_url:
            st.image(img_url, caption=obj.get("name_cn", "MOD 图标"),
                     use_container_width=True)
            used = visual.get("optimized_prompt", "")
            if used:
                st.markdown(
                    f'<p style="font-size:0.68rem;color:#4a3820;'
                    f'font-style:italic;text-align:center;margin-top:4px;">'
                    f'{used[:90]}…</p>', unsafe_allow_html=True)
            if st.button("🔄 重新生成图片",
                         key="regen_img", use_container_width=True):
                with st.spinner("✦ 召唤新的图腾形象……"):
                    prompt   = visual.get("optimized_prompt",
                               visual.get("fallback_prompt",
                               "Don't Starve Together style dark fantasy item"))
                    negative = visual.get("negative_prompt", "")
                    new_img  = fetch_image(prompt, negative)
                    if new_img["ok"]:
                        st.session_state.preview_image_url = new_img["url"]
                        st.session_state.preview_image_b64 = new_img["b64"]
                    else:
                        st.warning(f"生成失败：{new_img['err']}")
                st.rerun()
        else:
            st.markdown(
                '<p style="color:#4a3820;text-align:center;'
                'font-style:italic;padding:40px 0;">图腾尚未显现……</p>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_snd:
        render_sound_preview(sound)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 确认按钮 ──
    st.markdown("""
    <p style="text-align:center;font-size:0.82rem;color:#4a3820;
              font-style:italic;margin-bottom:10px;letter-spacing:1px;">
      ✦ 确认图像与音效无误后，令混沌永久凝固 ✦
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
        if st.button("✏ 继续调整设计",
                     key="back_to_chat", use_container_width=True):
            st.session_state.stage = "chat"
            st.rerun()
    with c2:
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

    # Step 1: 生成代码
    with st.spinner("✦ 暗影法典正在书写 Lua 代码……"):
        bar.progress(20)
        result = design_with_llm(
            st.session_state.final_design,
            st.session_state.messages
        )
    bar.progress(45)

    # Step 2: 附加图标
    with st.spinner("✦ 封印图腾形象……"):
        b64 = st.session_state.get("preview_image_b64")
        if b64:
            result.setdefault("data", {}).setdefault("files", {})
            result["data"]["files"]["modicon.tex"] = base64.b64decode(b64)
            result["data"]["files"]["modicon.xml"] = generate_atlas_xml()
            st.success("✦ 图腾已封印！")
        else:
            st.warning("图腾形象缺失，跳过。")
    bar.progress(65)

    # Step 3: 打包音效
    with st.spinner("✦ 封印音效……"):
        cache    = st.session_state.get("sound_audio_cache", {})
        sound    = st.session_state.get("sound_result", {}) or {}
        sfx_list = sound.get("sound_effects", [])
        files    = result.setdefault("data", {}).setdefault("files", {})

        packed = 0
        for i, sfx in enumerate(sfx_list):
            key = f"sfx_{i}"
            if key in cache and cache[key].get("ok"):
                entry = cache[key]
                if entry.get("source") == "synth":
                    # 合成音暂不打包（浏览器端合成无法导出wav）
                    continue
                trig = sfx.get("trigger", "sfx").replace(" ", "_")
                fmt  = entry.get("format", "wav")
                files[f"sounds/{trig}_{i}.{fmt}"] = entry["audio_bytes"]
                packed += 1

        if "sfx_ambient" in cache and cache["sfx_ambient"].get("ok"):
            entry = cache["sfx_ambient"]
            if entry.get("source") != "synth":
                fmt = entry.get("format", "wav")
                files[f"sounds/ambient.{fmt}"] = entry["audio_bytes"]
                packed += 1

        if packed:
            st.success(f"✦ 已封印 {packed} 个音效！")
        else:
            st.info("音效为合成预览，未打包到MOD中。可后续手动添加。")
    bar.progress(85)

    # Step 4: 归档
    with st.spinner("✦ 归入典藏……"):
        st.session_state.messages.append({
            "role":    "assistant",
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
# 💬 对话阶段
# ══════════════════════════════════════════════════════════════

def _enter_preview():
    """点击「预览并确认」后：总结设计 + 生成图片 + 生成音效"""
    with st.spinner("✦ 暗影正在整理设计蓝图……"):
        spec = summarize_design(st.session_state.messages)
        st.session_state.design_spec  = spec
        st.session_state.final_design = json.dumps(
            spec, ensure_ascii=False, indent=2)

    with st.spinner("✦ 召唤图腾形象（饥荒风格）……"):
        visual   = optimize_visual_prompt(spec)
        st.session_state.visual_result = visual
        prompt   = visual.get("optimized_prompt",
                   visual.get("fallback_prompt",
                   "Don't Starve Together official art style, dark fantasy item"))
        negative = visual.get("negative_prompt", "")
        img      = fetch_image(prompt, negative)
        st.session_state.preview_image_url = img["url"] if img["ok"] else None
        st.session_state.preview_image_b64 = img["b64"] if img["ok"] else None

    with st.spinner("✦ 编排音效方案……"):
        sound = generate_sound_prompts(spec)
        st.session_state.sound_result = sound

    # 清空旧的音效缓存
    st.session_state.sound_audio_cache = {}
    st.session_state.stage = "preview"
    st.rerun()


def render_chat_stage(mode: str):
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

    render_chat(st.session_state.messages)

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
            st.session_state.update({
                "mode": "rapid", "stage": "chat",
                "messages": [], "final_design": "",
                "design_spec": None, "sound_audio_cache": {},
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
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


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
                st.caption(f"{mod['date']}  ·  {mod['name']}")
                if mod.get("desc"):
                    st.caption(mod["desc"])
                if mod.get("image_url"):
                    st.image(mod["image_url"], width=110)
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
                    })
                    st.rerun()

    st.divider()
    st.caption(f"本次对话：{len(st.session_state.messages)} 条")
    st.caption(f"已生成 Mod：{len(st.session_state.generated_mods)} 个")
    st.divider()
    if st.button("🗑 清除全部记录", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
