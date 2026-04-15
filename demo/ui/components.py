import streamlit as st


# 🌙 顶部Banner
def render_banner():
    st.markdown("""
    <div style="
        margin: 40px auto;
        padding: 40px;
        width: 70%;

        background: rgba(20,18,15,0.6);
        backdrop-filter: blur(12px);

        border-radius: 20px;
        border: 1px solid rgba(255,220,150,0.15);

        box-shadow: 
            0 0 40px rgba(0,0,0,0.6),
            inset 0 0 20px rgba(255,200,120,0.05);

        text-align:center;
    ">
        <h2 style="color:#f5e6c8;">🌙 AI 饥荒 Mod 生成器</h2>
        <p style="opacity:0.7;">Design nightmares for Don't Starve</p>
    </div>
    """, unsafe_allow_html=True)


# 💬 聊天
def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
