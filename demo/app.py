import streamlit as st
import json
import sys
import os

# =========================
# 🚨 关键修复：保证 Cloud / 本地都能找到模块
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# =========================
# 安全 import（避免 Cloud 崩）
# =========================
from llm.qwen_client import design_with_llm, explore_with_llm
from bridge.intent_builder import build_intent_from_design
from parser.recommender import recommend
from generator.image_generator import generate_boss_image
from generator.packer import build_full_mod
from core.agent_flow import explore_step, generate_step
from ui.theme import inject_theme
from ui.components import (
    render_banner,
    render_boss_card,
    render_mechanics,
    render_chat
)

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="AI Mod Generator",
    layout="wide"
)

# 注入主题（防止UI报错）
st.markdown(inject_theme(), unsafe_allow_html=True)

# =========================
# Session初始化
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# UI Header
# =========================
render_banner()

# =========================
# 模式选择
# =========================
st.markdown("## 🎮 选择模式")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 快速生成"):
        st.session_state.mode = "fast"

with col2:
    if st.button("🧠 探索设计"):
        st.session_state.mode = "explore"


# =========================
# 🧠 探索模式
# =========================
if st.session_state.mode == "explore":

    st.markdown("### 🧠 探索模式（对话构思）")

    user_input = st.chat_input("描述你的Boss想法...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            reply = explore_step(st.session_state.messages)
        except Exception as e:
            reply = f"⚠️ AI调用失败: {e}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    render_chat(st.session_state.messages)

    if st.button("🌙 进入生成阶段"):
        st.session_state.mode = "generate"


# =========================
# ⚙️ 生成模式（核心）
# =========================
if st.session_state.mode == "generate":

    st.markdown("## ⚙️ 正在生成你的Boss...")

    with st.spinner("AI正在构建世界..."):

        try:
            design, result = generate_step(st.session_state.messages)
        except Exception as e:
            st.error(f"生成失败: {e}")
            st.stop()

        # 图片（失败也不崩）
        try:
            image_url = generate_boss_image(design.get("entity", "boss"))
        except:
            image_url = None

    # =========================
    # 展示Boss
    # =========================
    render_boss_card(design, image_url)

    # =========================
    # 机制
    # =========================
    render_mechanics(design.get("mechanics", []))

    # =========================
    # 代码
    # =========================
    st.markdown("## 💻 Lua代码")

    code = result.get("code", "-- no code generated")
    st.code(code, language="lua")

    # =========================
    # 下载
    # =========================
    try:
        zip_data = build_full_mod(code)

        st.download_button(
            "📦 下载Mod",
            data=zip_data,
            file_name="dont_starve_mod.zip"
        )
    except Exception as e:
        st.error(f"打包失败: {e}")


# =========================
# Debug（Cloud安全模式）
# =========================
with st.sidebar:
    st.write("Mode:", st.session_state.mode)
    st.write("Messages:", len(st.session_state.messages))