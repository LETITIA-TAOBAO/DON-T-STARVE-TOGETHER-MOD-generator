import streamlit as st
import os
from datetime import datetime
import time

# LLM导入
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"⚠️ LLM模块加载失败，使用降级模式")
    
    def mock_explore(messages):
        return {"text": f"👁️ 暗影回应了你的召唤...\n关于 '{messages[-1]['content'][:30]}...' 的想法很有趣！", "data": None}
    
    def mock_design(idea):
        return {"text": f"✅ Mod已生成！\n名称：Mod_{datetime.now().strftime('%H%M')}", "data": {"name": f"Mod_{datetime.now().strftime('%Y%m%d_%H%M')}", "desc": idea}}
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore

from theme import inject_theme
from components import render_banner, render_chat, render_loading, render_mode_confirmation, render_mod_history, render_download_section

st.set_page_config(page_title="AI 饥荒 Mod 生成器", layout="wide", initial_sidebar_state="expanded")

# ⚠️ 关键：主题最先注入
print("=== 启动 App ===")
st.markdown(inject_theme(), unsafe_allow_html=True)

# Session State
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Banner
render_banner()

# 模式选择
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("**🔥 快速生成**\\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

if st.session_state.mode != "home":
    render_mode_confirmation(st.session_state.mode)

# 聊天处理
if st.session_state.mode == "explore":
    st.info("💬 **与暗影对话以明确设计思路**")
    user_input = st.chat_input("描述你的想法...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

# 生成阶段
if st.session_state.is_generating:
    render_loading()
    time.sleep(2.5)
    
    try:
        if st.session_state.mode == "explore":
            result = explore_with_llm(st.session_state.messages)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        st.session_state.messages.append({"role": "assistant", "content": result.get('text', '暗影已回应...')})
        
        mod_data = result.get('data', {})
        if mod_data and st.session_state.mode == "rapid":
            st.session_state.generated_mods.append({
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', '新 Mod'),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ 生成失败：{str(e)}"})
    
    st.session_state.is_generating = False
    st.rerun()

# 显示聊天
if st.session_state.messages:
    render_chat(st.session_state.messages)

# 侧边栏
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    render_mod_history(st.session_state.generated_mods)
    st.divider()
    st.write(f"💬 对话：{len(st.session_state.messages)} 条")
    if st.session_state.generated_mods:
        render_download_section(st.session_state.generated_mods[-1])
    st.divider()
    if st.button("🗑️ 清除记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
