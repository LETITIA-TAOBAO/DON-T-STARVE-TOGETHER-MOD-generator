import streamlit as st
import sys
import os
import base64
import traceback

# =========================
# 路径设置
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# =========================
# LLM导入（安全版）
# =========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception:
    st.error("LLM模块加载失败")
    st.error(traceback.format_exc())
    st.stop()

from ui.theme import inject_theme
from ui.components import render_banner, render_chat


# =========================
# 页面配置（必须最先）
# =========================
st.set_page_config(page_title="AI Mod Generator", layout="wide")


# =========================
# 背景图
# =========================
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

bg_base64 = get_base64_image(os.path.join(BASE_DIR, "封面图.png"))


# =========================
# Theme（安全注入）
# =========================
if bg_base64:
    st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)


# =========================
# Session State
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "final_input" not in st.session_state:
    st.session_state.final_input = None


# =========================
# Header
# =========================
st.markdown("""
<h1 style='text-align:center; color:#f5e6c8;'>
🌙 AI 饥荒 Mod 生成器
</h1>
""", unsafe_allow_html=True)

render_banner()

st.write("DEBUG: page loaded")  # 🔥调试点


# =========================
# 模式选择
# =========================
st.markdown("## 🎮 选择模式")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 快速生成", use_container_width=True):
        st.session_state.mode = "fast"
        st.session_state.messages = []

with col2:
    if st.button("🧠 探索设计", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []


# =========================
# HOME
# =========================
if st.session_state.mode == "home":
    st.info("请选择一个模式开始设计你的 Mod")


# =========================
# FAST MODE
# =========================
elif st.session_state.mode == "fast":

    user_input = st.text_area("描述你的Mod想法")

    if st.button("✨ 生成"):
        if user_input.strip():
            with st.spinner("AI正在构建世界..."):
                try:
                    result = design_with_llm(user_input)
                except Exception:
                    result = traceback.format_exc()

            st.markdown("## 🧠 设计方案")
            st.markdown(result)


# =========================
# EXPLORE MODE
# =========================
elif st.session_state.mode == "explore":

    user_input = st.chat_input("说说你的想法...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            reply = explore_with_llm(st.session_state.messages)
        except Exception:
            reply = traceback.format_exc()

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
            st.rerun()


# =========================
# GENERATE MODE
# =========================
elif st.session_state.mode == "generate":

    with st.spinner("AI正在生成最终设计..."):
        try:
            result = design_with_llm(st.session_state.final_input)
        except Exception:
            result = traceback.format_exc()

    st.markdown("## 🧠 最终设计")
    st.markdown(result)

    if st.button("🔁 返回首页"):
        st.session_state.mode = "home"
        st.rerun()


# =========================
# DEBUG SIDEBAR
# =========================
with st.sidebar:
    st.write("Mode:", st.session_state.mode)
    st.write("Messages:", len(st.session_state.messages))
