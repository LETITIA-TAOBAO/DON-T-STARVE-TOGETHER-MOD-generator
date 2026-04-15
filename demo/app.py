# app.py
import streamlit as st
import os
import base64
import time

# =========================
# 1. 页面配置
# =========================
st.set_page_config(page_title="DST Mod Generator", layout="wide")

# =========================
# 2. 实用函数 (修复背景图)
# =========================
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# 加载本地图片 "背景图.png"
bg_base64 = get_base64_image("背景图.png")

# =========================
# 3. 导入模块
# =========================
from theme import inject_theme
from components import render_banner, render_chat, render_loading

# =========================
# 4. 注入主题 (传入图片编码)
# =========================
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# =========================
# 5. Session State
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 6. UI 渲染
# =========================

# 渲染 Banner
# ⚠️ 重要：必须加上 unsafe_allow_html=True
st.markdown(render_banner(), unsafe_allow_html=True)

# 模式选择
col1, col2 = st.columns(2, gap="large")
with col1:
    if st.button("快速生成\nRAPID GENERATION", use_container_width=True):
        st.session_state.mode = "rapid"
        st.rerun()

with col2:
    if st.button("探索设计\nDEEP EXPLORATION", use_container_width=True):
        st.session_state.mode = "explore"
        st.rerun()

# --- 快速生成模式 ---
if st.session_state.mode == "rapid":
    st.markdown("### ⚡ 当前模式：快速生成 / RAPID GENERATION")
    user_input = st.text_area("描述你的 Mod 构想 / Describe your Mod Idea")
    if st.button("✨ 开始铸造 / FORGE MOD", use_container_width=True):
        with st.spinner(""):
            st.markdown(render_loading(), unsafe_allow_html=True)
            time.sleep(2) # 模拟生成
            st.success("Mod 已经铸造成型！/ Mod has been forged!")

# --- 探索设计模式 ---
elif st.session_state.mode == "explore":
    st.markdown("### 👁️ 当前模式：探索设计 / DEEP EXPLORATION")
    user_input = st.chat_input("与暗影对话... / Talk to the Shadow...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # 这里可以添加调用 LLM 的逻辑
        st.session_state.messages.append({"role": "assistant", "content": "暗影低语：这是一个疯狂的构想..."})
        st.rerun()
    render_chat(st.session_state.messages)

else:
    st.markdown("<div style='text-align:center; color:#888; margin-top:50px;'>请选择你的道路，求生者... / Please choose your path, Survivor...</div>", unsafe_allow_html=True)
