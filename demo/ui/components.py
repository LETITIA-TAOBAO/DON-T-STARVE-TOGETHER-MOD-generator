# ui/components.py

import streamlit as st
from ui.theme import THEME


# =========================
# 🌙 顶部Banner
# =========================
def render_banner():
    st.markdown(f"""
    <div style="
        text-align:center;
        padding:30px;
        background: linear-gradient(180deg, #111, #000);
        border-radius:15px;
        border:1px solid {THEME['border']};
        margin-bottom:20px;
    ">
        <h1>🌙 AI 饥荒 Mod 生成器</h1>
        <p style="color:{THEME['sub_text']}">
            Design nightmares for Don't Starve
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🎮 模式卡片
# =========================
def render_mode_card(title, desc, icon):
    st.markdown(f"""
    <div class="card">
        <h3>{icon} {title}</h3>
        <p style="color:{THEME['sub_text']}">{desc}</p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🌙 Boss卡片（核心展示）
# =========================
def render_boss_card(design, image_url=None):
    st.markdown(f"""
    <div class="card">
        <h2>🌙 {design.get("entity", "Unknown Entity")}</h2>
        <p style="color:{THEME['sub_text']}">
            {design.get("concept", "")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    if image_url:
        st.image(image_url, width=250)


# =========================
# ⚔️ 机制列表
# =========================
def render_mechanics(mechanics):
    st.markdown("### ⚔️ Ability System")

    if not mechanics:
        st.write("No mechanics defined yet.")
        return

    for m in mechanics:
        st.markdown(f"""
        <div style="
            background:{THEME['panel']};
            padding:10px;
            border-radius:8px;
            margin:5px 0;
            border-left:3px solid {THEME['accent']};
        ">
            {m}
        </div>
        """, unsafe_allow_html=True)


# =========================
# 💬 对话气泡（探索模式）
# =========================
def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])