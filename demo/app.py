import streamlit as st
from theme import inject_theme
from components import render_banner, render_chat, render_loading

st.set_page_config(layout="wide")

st.markdown(inject_theme(), unsafe_allow_html=True)

# ===== session =====
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== UI =====
render_banner()

col1, col2 = st.columns(2)

with col1:
    if st.button("快速生成\nRAPID GENERATION"):
        st.session_state.mode = "rapid"

with col2:
    if st.button("探索设计\nDEEP EXPLORATION"):
        st.session_state.mode = "explore"

# ===== 模式动态反馈 =====
if st.session_state.mode == "rapid":
    st.markdown("""
    <div class="mode-box">
    ⚡ 当前模式：快速生成<br>
    <span>RAPID GENERATION MODE ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.mode == "explore":
    st.markdown("""
    <div class="mode-box green">
    👁️ 当前模式：探索设计<br>
    <span>EXPLORATION MODE ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

# ===== 输入 =====
user_input = st.chat_input("输入你的疯狂构想 / Enter your forbidden idea")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.spinner(""):
        render_loading()

    st.session_state.messages.append({
        "role": "assistant",
        "content": "👁️ 暗影低语：你的世界正在成形…… / The shadows whisper: your world takes form..."
    })

render_chat(st.session_state.messages)
