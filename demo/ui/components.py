# ui/components.py

import streamlit as st


# =========================
# 🌙 顶部Banner（科雷风升级版）
# =========================
def render_banner():
    st.markdown("""
    <div style="
        text-align:center;
        padding:30px;
        background: rgba(20,18,15,0.85);
        border-radius:16px;
        margin-bottom:20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.6);
    ">
        <h1 style="
            margin-bottom:10px;
        ">
            🌙 AI 饥荒 Mod 生成器
        </h1>
        <p style="
            opacity:0.7;
            font-size:14px;
        ">
            Design nightmares for Don't Starve
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🎮 模式卡片（可选用）
# =========================
def render_mode_card(title, desc, icon):
    st.markdown(f"""
    <div style="
        background: rgba(40,30,20,0.8);
        padding:20px;
        border-radius:12px;
        margin:10px 0;
        transition: all 0.2s ease-in-out;
    ">
        <h3>{icon} {title}</h3>
        <p style="opacity:0.7">{desc}</p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🌙 Boss卡片（适配新文本流）
# =========================
def render_boss_card(design_text, image_url=None):
    st.markdown("""
    <div style="
        background: rgba(25,20,15,0.85);
        padding:20px;
        border-radius:16px;
        margin-top:20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    ">
    """, unsafe_allow_html=True)

    # 👉 现在直接展示文本（不再依赖JSON）
    st.markdown(design_text)

    st.markdown("</div>", unsafe_allow_html=True)

    if image_url:
        st.image(image_url, width=300)


# =========================
# ⚔️ 机制（可选保留）
# =========================
def render_mechanics(mechanics):
    st.markdown("### ⚔️ Ability System")

    if not mechanics:
        st.write("（机制将在设计完成后出现）")
        return

    for m in mechanics:
        st.markdown(f"""
        <div style="
            background: rgba(60,50,35,0.7);
            padding:10px;
            border-radius:8px;
            margin:6px 0;
            border-left:3px solid rgba(255,200,120,0.5);
        ">
            {m}
        </div>
        """, unsafe_allow_html=True)


# =========================
# 💬 聊天UI（升级版）
# =========================
def render_chat(messages):

    for msg in messages:

        role = msg["role"]
        content = msg["content"]

        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"""
                <div style="
                    background: rgba(80,60,40,0.7);
                    padding:10px;
                    border-radius:10px;
                ">
                    {content}
                </div>
                """, unsafe_allow_html=True)

        else:
            with st.chat_message("assistant"):
                st.markdown(f"""
                <div style="
                    background: rgba(40,35,25,0.8);
                    padding:12px;
                    border-radius:10px;
                    border:1px solid rgba(255,220,150,0.2);
                ">
                    {content}
                </div>
                """, unsafe_allow_html=True)
