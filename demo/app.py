import streamlit as st
from theme import inject_theme
from components import render_banner, render_chat, render_loading

st.set_page_config(layout="wide")

st.markdown(inject_theme(), unsafe_allow_html=True)

# session
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# UI
render_banner()

col1, col2 = st.columns(2)

with col1:
    if st.button("快速生成\nRAPID"):
        st.session_state.mode = "rapid"

with col2:
    if st.button("探索设计\nEXPLORE"):
        st.session_state.mode = "explore"

# ===== 模式反馈（强化） =====
if st.session_state.mode == "rapid":
    st.markdown("### ⚡ 当前模式：快速生成 / RAPID GENERATION")

elif st.session_state.mode == "explore":
    st.markdown("### 👁️ 当前模式：探索设计 / DEEP EXPLORATION")

# ===== 输入 =====
user_input = st.chat_input("输入你的疯狂构想 / Enter your idea")

if user_input:
    st.session_state.messages.append(user_input)

    with st.spinner("世界正在变化..."):
        render_loading()

    st.session_state.messages.append("👁️ 暗影回应了你的召唤……")

render_chat(st.session_state.messages)
