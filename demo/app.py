import streamlit as st
import os
import base64
from datetime import datetime

# ========================
# ✅ 导入模块
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception:
    def mock_explore(messages):
        return {"text": "👁️ 暗影在倾听...", "data": None}
    
    def mock_design(idea):
        return {
            "text": f"✅ Mod 已生成！\n名称：Mod #{datetime.now().strftime('%H:%M')}",
            "data": {"name": f"Mod_{datetime.now().strftime('%Y%m%d_%H%M')}", "desc": idea}
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore

from theme import inject_theme
from components import (render_banner, render_chat, render_loading, 
                       render_mode_confirmation, render_mod_history, render_download_section)

# ========================
# 页面配置
# ========================
st.set_page_config(
    page_title="AI 饥荒 Mod 生成器",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# 背景图处理
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "背景图.png")

def get_base64_image(path):
    try:
        if not os.path.exists(path):
            print("ℹ️ 未找到背景图，使用网络图片")
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"❌ 背景图读取失败：{e}")
        return None

bg_base64 = get_base64_image(bg_path)

# ========================
# ⚠️ 关键：主题必须在最前面注入
# ========================
print("✅ 注入主题样式")
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# ========================
# Session State
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []

if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

# ========================
# 主界面
# ========================
render_banner()

# 模式选择
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("**🔥 快速生成**\\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# 模式确认
if st.session_state.mode != "home":
    render_mode_confirmation(st.session_state.mode)

# ========================
# 模式逻辑
# ========================
if st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.show_loading = True
        st.rerun()

elif st.session_state.mode == "explore":
    st.info("💬 与暗影对话以明确设计思路\nTalk to the Shadow to refine your ideas")
    
    user_input = st.chat_input("描述你的想法...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 模拟 AI 回复
        reply = "👁️ 暗影回应了你的召唤...\nThe shadows respond to your summoning..."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        if len(st.session_state.messages) >= 4:
            if st.button("✨ 生成最终 Mod"):
                summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
                st.session_state.final_prompt = summary
                st.session_state.mode = "generating"
                st.rerun()

# ========================
# 生成阶段
# ========================
if st.session_state.mode == "generating":
    render_loading()
    
    import time
    time.sleep(2)
    
    try:
        result = design_with_llm(st.session_state.messages[0]['content'])
    except Exception as e:
        result = {"text": f"❌ 生成失败：{str(e)}", "data": None}
    
    mod_data = result.get('data', {})
    if mod_data:
        new_mod = {
            "id": len(st.session_state.generated_mods) + 1,
            "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc": mod_data.get('desc', ''),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.generated_mods.append(new_mod)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get('text', '生成完成')
    })
    st.session_state.mode = "generated"
    st.rerun()

# ========================
# 结果展示
# ========================
if st.session_state.mode == "generated":
    if st.session_state.messages:
        render_chat(st.session_state.messages)
    
    if st.button("🔄 再次生成"):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# ========================
# 侧边栏
# ========================
with st.sidebar:
    st.markdown("<h3 style='text-align:center;color:#FFD700;'>📦 Mod 库</h3>", unsafe_allow_html=True)
    
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
