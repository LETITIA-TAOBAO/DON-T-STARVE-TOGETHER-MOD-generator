import streamlit as st
import os
import base64
from datetime import datetime

# 安全导入 LLM
try:
    from qwen_client import design_with_llm
except Exception:
    def mock_design(idea):
        return {"text": "✅ Mod 已生成", "data": {"name": f"Mod_{datetime.now().strftime('%H%M')}", "desc": idea}}
    design_with_llm = mock_design

from theme import inject_theme
from components import (render_banner, render_chat, render_loading, 
                       render_mode_confirmation, render_mod_history, render_download_section)

# 页面配置
st.set_page_config(page_title="AI Mod Generator", layout="wide", initial_sidebar_state="expanded")

# 背景图处理
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "背景图.png")

def get_base64_image(path):
    try:
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

bg_base64 = get_base64_image(bg_path)

# ⚠️ 关键：主题最先注入
print("=== 启动 App ===")
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# Session State
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []

# Banner
render_banner()

# 模式选择
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("**🔥 快速生成**\nRAPID GENERATION", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\nDEEP EXPLORATION", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# 模式确认
if st.session_state.mode != "home":
    render_mode_confirmation(st.session_state.mode)

# 各模式逻辑
if st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的 Mod 构想...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.mode = "generating"
        st.rerun()

elif st.session_state.mode == "explore":
    st.info("💬 与暗影对话以明确设计思路")
    user_input = st.chat_input("描述你的想法...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = "👁️ 暗影回应了你的召唤..."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if len(st.session_state.messages) >= 4:
            if st.button("✨ 生成最终 Mod"):
                st.session_state.mode = "generating"
                st.rerun()

# 生成阶段
if st.session_state.mode == "generating":
    render_loading()
    import time
    time.sleep(2)
    
    try:
        result = design_with_llm(st.session_state.messages[-1]['content'])
        mod_data = result.get('data', {})
        if mod_data:
            st.session_state.generated_mods.append({
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', '新 Mod'),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        st.session_state.messages.append({"role": "assistant", "content": result.get('text', '完成')})
        st.session_state.mode = "generated"
        st.rerun()
    except Exception as e:
        st.error(f"生成失败：{e}")
        st.session_state.mode = "explore"
        st.rerun()

# 结果展示
if st.session_state.mode == "generated":
    if st.session_state.messages:
        render_chat(st.session_state.messages)
    if st.button("🔄 再次生成"):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

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
