import streamlit as st
import sys
import os
import base64
import traceback
import time

# =========================
# 路径设置
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# =========================
# LLM导入
# =========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception:
    st.error("LLM模块加载失败 / MODULE LOAD FAILED")
    st.error(traceback.format_exc())
    st.stop()

from ui.theme import inject_theme
from ui.components import render_banner, render_chat, render_loading, render_mode_indicator

# =========================
# 页面配置
# =========================
st.set_page_config(page_title="AI Mod Generator", layout="wide")

# =========================
# 背景图处理
# =========================
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

bg_base64 = get_base64_image(os.path.join(BASE_DIR, "封面图.png"))

# =========================
# Theme注入
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
# 中央Banner（双语标题）
# =========================
render_banner()

# =========================
# 模式选择区域（双语按钮）
# =========================
st.markdown("""
<h2 style="margin-bottom: 5px;">选择模式</h2>
<p style="font-size: 0.9rem; color: rgba(200,180,140,0.6); margin-top: 0; letter-spacing: 2px; font-family: 'Griffy', cursive;">
    SELECT MODE
</p>
""", unsafe_allow_html=True)

# 模式指示器
if st.session_state.mode == "fast":
    render_mode_indicator("快速生成", "FAST GENERATION")
elif st.session_state.mode == "explore":
    render_mode_indicator("探索设计", "EXPLORE DESIGN")

col1, col2 = st.columns(2)

# 双语按钮：使用HTML实现中文+英文副标题
with col1:
    is_active = st.session_state.mode == "fast"
    btn_style = "primary" if is_active else "secondary"
    
    # 使用HTML按钮内容
    if st.button(
        "快速生成\nFAST GENERATION", 
        use_container_width=True, 
        type=btn_style,
        help="直接生成完整方案 / Generate complete design directly"
    ):
        st.session_state.mode = "fast"
        st.session_state.messages = []
        st.rerun()

with col2:
    is_active = st.session_state.mode == "explore"
    btn_style = "primary" if is_active else "secondary"
    
    if st.button(
        "探索设计\nEXPLORE DESIGN", 
        use_container_width=True, 
        type=btn_style,
        help="对话式逐步完善 / Iterative design through conversation"
    ):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# =========================
# HOME 模式（双语）
# =========================
if st.session_state.mode == "home":
    st.info("请选择一个模式开始设计你的 Mod\n\nPlease select a mode to start designing your Mod")

# =========================
# FAST MODE（双语）
# =========================
elif st.session_state.mode == "fast":
    st.markdown("""
    <h3 style="margin-bottom: 5px;">🚀 快速生成模式</h3>
    <p style="font-size: 0.9rem; color: rgba(200,180,140,0.6); margin-top: 0; letter-spacing: 1px;">
        FAST GENERATION MODE
    </p>
    """, unsafe_allow_html=True)
    
    st.caption("直接描述你的想法，AI将立即为你生成完整设计方案\nDescribe your idea, AI will generate complete design immediately")
    
    user_input = st.text_area(
        "描述你的Mod想法 / Describe Your Mod Idea", 
        placeholder="比如：一个能在月圆之夜变身的狼人角色，拥有独特的饥饿机制...\n\nExample: A werewolf character that transforms during full moon with unique hunger mechanics...",
        height=150
    )

    if st.button("开始生成\nSTART GENERATION", type="primary"):
        if user_input.strip():
            render_loading("正在生成世界...", "GENERATING WORLD...")
            
            try:
                result = design_with_llm(user_input)
                display_text = result["text"] if isinstance(result, dict) else result
                
                st.markdown("""
                <h3 style="margin-bottom: 5px;">📝 设计方案</h3>
                <p style="font-size: 0.9rem; color: rgba(200,180,140,0.6); margin-top: 0; letter-spacing: 1px;">
                    DESIGN PROPOSAL
                </p>
                """, unsafe_allow_html=True)
                
                st.markdown(display_text)
                st.success("✨ 生成完成！ / GENERATION COMPLETE!")
                
            except Exception as e:
                st.error("生成失败 / GENERATION FAILED")
                st.code(traceback.format_exc())
        else:
            st.warning("请输入你的想法后再生成哦！\nPlease enter your idea before generating!")

# =========================
# EXPLORE MODE（双语）
# =========================
elif st.session_state.mode == "explore":
    st.markdown("""
    <h3 style="margin-bottom: 5px;">🧠 探索设计模式</h3>
    <p style="font-size: 0.9rem; color: rgba(200,180,140,0.6); margin-top: 0; letter-spacing: 1px;">
        EXPLORE DESIGN MODE
    </p>
    """, unsafe_allow_html=True)
    
    st.caption("与AI对话，逐步完善你的Mod设计\nChat with AI to gradually refine your mod design")
    
    render_chat(st.session_state.messages)
    
    user_input = st.chat_input("说说你的想法... / Share your thoughts...")
    
    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with st.spinner(""):
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                render_loading("暗影正在凝聚...", "SHADOWS GATHERING...")
            
            time.sleep(0.5)
            
            try:
                reply_obj = explore_with_llm(st.session_state.messages)
                reply_text = reply_obj["text"] if isinstance(reply_obj, dict) else reply_obj
            except Exception:
                reply_text = "❌ 对话失败 / CHAT FAILED: " + 
