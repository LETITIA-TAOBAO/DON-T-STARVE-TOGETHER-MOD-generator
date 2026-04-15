# app.py
import streamlit as st
import sys
import os
import time

# =========================
# 1. 页面配置 (必须最先执行)
# =========================
st.set_page_config(
    page_title="DST Mod Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# 2. 导入与容错处理 (防止白屏)
# =========================
# 尝试导入真实的 LLM 客户端，如果失败则使用模拟数据，确保 UI 不崩溃
try:
    from qwen_client import design_with_llm, explore_with_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    # 模拟函数，用于测试 UI
    def design_with_llm(prompt):
        time.sleep(2)
        return {"text": f"【模拟生成】基于你的构想：'{prompt}'，已生成 Mod 代码结构..."}
    
    def explore_with_llm(messages):
        time.sleep(2)
        return {"text": "【模拟回应】暗影低语道：这个想法很有趣，但我们需要更多的细节来定义它的 san 值影响..."}

# 导入自定义模块
from theme import inject_theme
from components import render_banner, render_chat, render_loading

# =========================
# 3. 注入主题
# =========================
st.markdown(inject_theme(), unsafe_allow_html=True)

# =========================
# 4. Session State 初始化
# =========================
if "mode" not in st.session_state:
    st.session_state.mode = None  # None, 'rapid', 'explore'

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 5. 主界面渲染
# =========================

# 渲染顶部 Banner (包含介绍和模式说明)
render_banner()

# 模式选择按钮区域
col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button("快速生成\nRAPID GENERATION", use_container_width=True, key="btn_rapid"):
        st.session_state.mode = "rapid"
        st.session_state.messages = [] # 切换模式清空消息
        st.rerun()

with col2:
    if st.button("探索设计\nDEEP EXPLORATION", use_container_width=True, key="btn_explore"):
        st.session_state.mode = "explore"
        st.session_state.messages = [] # 切换模式清空消息
        st.rerun()

# =========================
# 6. 模式反馈与功能区域
# =========================

# --- 快速生成模式 ---
if st.session_state.mode == "rapid":
    st.markdown("### ⚡ 当前模式：快速生成 / RAPID GENERATION")
    st.markdown("<div style='height:2px; background:#aa7733; margin:10px 0 30px 0;'></div>", unsafe_allow_html=True)
    
    user_input = st.text_area(
        "描述你的 Mod 构想 / Describe your Mod Idea",
        placeholder="例如：我想做一个会爆炸的切斯特... / e.g., I want an explosive Chester...",
        height=150
    )
    
    if st.button("✨ 开始铸造 / FORGE MOD", use_container_width=True):
        if user_input.strip():
            with st.container():
                render_loading()
                # 调用 LLM (真实或模拟)
                result = design_with_llm(user_input)
                display_text = result["text"] if isinstance(result, dict) else result
                
                st.markdown(f"""
                <div style="
                    background: rgba(0,0,0,0.6);
                    border: 1px solid #5a3a1a;
                    padding: 20px;
                    border-radius: 8px;
                    font-family: 'Griffy';
                    color: #aadd88;
                    margin-top: 20px;
                ">
                <h3 style="color:#ffaa60; text-align:left;">📜 生成结果 / RESULT</h3>
                {display_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 请输入你的疯狂构想！ / Enter your madness!")

# --- 探索设计模式 ---
elif st.session_state.mode == "explore":
    st.markdown("### 👁️ 当前模式：探索设计 / DEEP EXPLORATION")
    st.markdown("<div style='height:2px; background:#668844; margin:10px 0 30px 0;'></div>", unsafe_allow_html=True)
    
    # 聊天输入
    user_input = st.chat_input("与暗影对话... / Talk to the Shadow...")
    
    if user_input:
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 显示加载动画
        with st.spinner(""):
            render_loading()
            # 调用 LLM
            reply_obj = explore_with_llm(st.session_state.messages)
            reply_text = reply_obj["text"] if isinstance(reply_obj, dict) else reply_obj
            
        # 添加 AI 消息
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()
    
    # 渲染聊天记录
    render_chat(st.session_state.messages)

# --- 未选择模式 ---
else:
    st.markdown("""
    <div style="text-align:center; margin-top:50px; opacity:0.7;">
        <p style="font-family:'Griffy'; font-size:1.5rem;">
        选择你的道路，求生者...<br>
        <span style="font-size:1rem; color:#888;">Choose your path, Survivor...</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 7. 调试侧边栏 (可选，方便重置)
# =========================
with st.sidebar:
    st.markdown("### 🛠️ 调试 / DEBUG")
    if st.button("🗑️ 重置状态 / Reset"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    st.write(f"Mode: {st.session_state.mode}")
    st.write(f"LLM Status: {'Connected' if LLM_AVAILABLE else 'Mock Mode'}")
