import streamlit as st
import sys
import os
import base64

# =========================
# 🚨 路径修复
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# =========================
# 🔥 导入模块
# =========================
from qwen_client import design_with_llm, explore_with_llm
from generator.image_generator import generate_boss_image
from generator.packer import build_full_mod

from ui.theme import inject_theme
from ui.components import (
    render_banner,
    render_chat
)

# =========================
# 🖼️ 读取封面图（关键）
# =========================
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

bg_base64 = get_base64_image(os.path.join(BASE_DIR, "封面图.png"))

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="AI Mod Generator",
    layout="wide"
)

# 注入主题（带背景）
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# =========================
# Session 初始化
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "final_input" not in st.session_state:
    st.session_state.final_input = None


# =========================
# 🎮 顶部标题（游戏感）
# =========================
st.markdown("""
<h1 style='text-align:center; font-size:48px;'>
🌙 AI 饥荒 Mod 生成器
</h1>
<p style='text-align:center; opacity:0.7;'>
在黑暗中创造属于你的世界
</p>
""", unsafe_allow_html=True)

render_banner()

# =========================
# 🎮 模式选择
# =========================
st.markdown("## 🎮 选择模式")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 快速生成（我已经想好了）"):
        st.session_state.mode = "fast"
        st.session_state.messages = []

with col2:
    if st.button("🧠 探索设计（一起构思）"):
        st.session_state.mode = "explore"
        st.session_state.messages = []


# =========================
# 🚀 快速生成模式
# =========================
if st.session_state.mode == "fast":

    st.markdown("### 🚀 快速生成")

    user_input = st.text_area("描述你的Mod想法（越具体越好）")

    if st.button("✨ 立即生成") and user_input:

        with st.spinner("AI正在构建世界..."):

            try:
                design_text = design_with_llm(user_input)
            except Exception as e:
                st.error(f"生成失败: {e}")
                st.stop()

        st.markdown("## 🧠 设计方案")
        st.markdown(design_text)

        # 图片（增强沉浸感）
        try:
            image_url = generate_boss_image("boss")
            if image_url:
                st.image(image_url)
        except:
            pass


# =========================
# 🧠 探索模式（多轮对话）
# =========================
if st.session_state.mode == "explore":

    st.markdown("### 🧠 探索模式（对话构思）")

    user_input = st.chat_input("说说你的想法，比如：一个夜晚变强的boss...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            reply = explore_with_llm(st.session_state.messages)
        except Exception as e:
            reply = f"AI有点卡住了：{e}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    # 渲染聊天
    render_chat(st.session_state.messages)

    # 👉 进入生成阶段
    if len(st.session_state.messages) >= 2:
        if st.button("🌙 我想好了，生成Mod"):

            summary = "\n".join([
                f"{m['role']}: {m['content']}"
                for m in st.session_state.messages
            ])

            st.session_state.final_input = summary
            st.session_state.mode = "generate"


# =========================
# ⚙️ 统一生成阶段
# =========================
if st.session_state.mode == "generate":

    st.markdown("## ⚙️ 正在生成你的Mod...")

    with st.spinner("AI正在把创意变成现实..."):

        try:
            design_text = design_with_llm(
                st.session_state.final_input
            )
        except Exception as e:
            st.error(f"生成失败: {e}")
            st.stop()

    st.markdown("## 🧠 最终设计方案")
    st.markdown(design_text)

    # 图片
    try:
        image_url = generate_boss_image("boss")
        if image_url:
            st.image(image_url)
    except:
        pass

    # 下载（占位）
    st.download_button(
        "📦 下载Mod（开发中）",
        data="暂未生成代码",
        file_name="mod.txt"
    )


# =========================
# 🧪 Debug 面板
# =========================
with st.sidebar:
    st.write("Mode:", st.session_state.mode)
    st.write("Messages:", len(st.session_state.messages))
