import streamlit as st
import sys
import os
import base64
import traceback

try:
    from llm.qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    st.error(traceback.format_exc())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from llm.qwen_client import design_with_llm, explore_with_llm
from ui.theme import inject_theme
from ui.components import render_banner, render_chat


# 🖼️ 背景读取
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

bg_base64 = get_base64_image(os.path.join(BASE_DIR, "封面图.png"))

st.set_page_config(page_title="AI Mod Generator", layout="wide")

# 注入主题
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)


# Session
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "final_input" not in st.session_state:
    st.session_state.final_input = None


# 🌙 标题（修复清晰度）
st.markdown("""
<h1 style='
    text-align:center;
    font-size:48px;
    color:#f5e6c8;
    text-shadow: 0 2px 6px rgba(0,0,0,0.8);
'>
🌙 AI 饥荒 Mod 生成器
</h1>

<p style='text-align:center; color:#c8b48a;'>
在黑暗中创造属于你的世界
</p>
""", unsafe_allow_html=True)


render_banner()


# 🎮 模式选择
st.markdown("## 🎮 选择模式")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 快速生成"):
        st.session_state.mode = "fast"
        st.session_state.messages = []

with col2:
    if st.button("🧠 探索设计"):
        st.session_state.mode = "explore"
        st.session_state.messages = []


# 🚀 快速模式
if st.session_state.mode == "fast":

    user_input = st.text_area("描述你的Mod想法")

    if st.button("✨ 生成") and user_input:

        with st.spinner("AI正在构建世界..."):
            result = design_with_llm(user_input)

        st.markdown("## 🧠 设计方案")
        st.markdown(result)


# 🧠 探索模式
if st.session_state.mode == "explore":

    user_input = st.chat_input("说说你的想法...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        reply = explore_with_llm(st.session_state.messages)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    render_chat(st.session_state.messages)

    if len(st.session_state.messages) >= 2:
        if st.button("🌙 开始生成"):

            summary = "\n".join([
                f"{m['role']}: {m['content']}"
                for m in st.session_state.messages
            ])

            st.session_state.final_input = summary
            st.session_state.mode = "generate"


# ⚙️ 生成
if st.session_state.mode == "generate":

    with st.spinner("AI正在生成最终设计..."):
        result = design_with_llm(st.session_state.final_input)

    st.markdown("## 🧠 最终设计")
    st.markdown(result)


# Debug
with st.sidebar:
    st.write("Mode:", st.session_state.mode)
