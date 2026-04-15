import streamlit as st
import base64
import os
from theme import inject_theme
from components import render_banner, render_chat, render_loading

st.set_page_config(layout="wide")

# ===== 背景图读取 =====
def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_base64 = get_base64("背景图.png")

st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# ===== session =====
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== UI =====
render_banner()

col1, col2 = st.columns(2)

# ===== 按钮（带状态高亮）=====
with col1:
    if st.button("快速生成\nRAPID"):
        st.session_state.mode = "rapid"

with col2:
    if st.button("探索设计\nEXPLORE"):
        st.session_state.mode = "explore"

# ===== 模式反馈（强化+动画）=====
if st.session_state.mode == "rapid":
    st.markdown("""
    <div class="mode-box active">
    ⚡ 快速生成模式已激活<br>
    <span>RAPID GENERATION MODE ENGAGED</span>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.mode == "explore":
    st.markdown("""
    <div class="mode-box explore">
    👁️ 探索设计模式已激活<br>
    <span>DEEP EXPLORATION MODE ENGAGED</span>
    </div>
    """, unsafe_allow_html=True)

# ===== 输入 =====
user_input = st.chat_input("输入你的疯狂构想 / Enter your idea")

if user_input:
    st.session_state.messages.append(user_input)

    with st.spinner(""):
        render_loading()

    st.session_state.messages.append("👁️ 暗影回应了你的召唤……")

render_chat(st.session_state.messages)
