import streamlit as st
import os
import base64
from datetime import datetime

# ========================
# ✅ 安全导入 LLM 模块
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"⚠️ LLM 模块加载失败：{str(e)}")
    
    def mock_explore(messages):
        return {
            "text": "👁️ 暗影在倾听...\n请告诉我更多关于你的想法。",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f"✅ Mod 已生成！\n\n名称：Mod #{datetime.now().strftime('%H:%M')}",
            "data": {
                "name": f"疯狂Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea
            }
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore

# ========================
# ✅ 导入 UI 组件
# ========================
from theme import inject_theme
from components import render_banner, render_chat, render_loading, render_mode_confirmation, render_mod_history, render_download_section

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
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

bg_base64 = get_base64_image(bg_path)

# ========================
# 注入主题（必须放在最前面）
# ========================
st.markdown(inject_theme(bg_base64), unsafe_allow_html=True)

# ========================
# Session State 初始化
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
# ⚠️ 关键修复：直接写 Banner HTML（不要调用函数）
# ========================
st.markdown("""
<div style="
    background: rgba(20, 15, 10, 0.8);
    border: 3px solid #A67C3B;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    max-width: 950px;
    margin: 20px auto;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
">
    <h1 style="font-family:'Creepster'; font-size:3.8rem; color:#ffaa60; letter-spacing:5px;">饥荒 MOD 生成器</h1>
    <p style="font-family:'Griffy'; color:#aa8855; font-size:1.4rem; letter-spacing:3px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    <hr style="border:0; border-top:2px solid #5a3a1a; width:50%; margin:20px auto;">
    
    <p style="font-family:'Griffy'; font-size:1.1rem; line-height:1.7; color:#d4c4a0; max-width:800px; margin:0 auto 30px;">
    当理智的 san 值归零，现实的法则在此崩塌。<br>
    <span style="color:#88aa66;">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
    <span style="color:#88aa66;">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="border:0; border-top:2px solid #5a3a1a; width:40%; margin:25px auto;">
    
    <div style="display:flex; gap:20px; flex-wrap:wrap; justify-content:center;">
        <div style="flex:1; min-width:320px; background:rgba(30,20,10,0.7); border:2px solid #aa7733; padding:20px; border-radius:6px;">
            <div style="font-family:'Creepster'; color:#ffaa60; font-size:1.7rem;">🔥 快速生成 / RAPID</div>
            <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.95rem; margin-top:10px;">适用于意志坚定的造物主。</p>
        </div>
        
        <div style="flex:1; min-width:320px; background:rgba(20,30,20,0.7); border:2px solid #668844; padding:20px; border-radius:6px;">
            <div style="font-family:'Creepster'; color:#aadd88; font-size:1.7rem;">👁️ 探索设计 / EXPLORE</div>
            <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.95rem; margin-top:10px;">适用于在迷雾中低语的探索者。</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========================
# 模式选择按钮
# ========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("🔥 快速生成\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("👁️ 探索设计\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.rerun()

# 模式确认
if st.session_state.mode != "home":
    render_mode_confirmation(st.session_state.mode)

# ========================
# 各模式处理逻辑
# ========================
if st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.mode = "generating"
        st.rerun()

elif st.session_state.mode == "explore":
    user_input = st.chat_input("描述你的想法...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply_text = "👁️ 暗影回应了你的召唤..."
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()
    
    if len(st.session_state.messages) >= 2:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
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
        if st.session_state.mode == "rapid":
            result = design_with_llm(st.session_state.messages[0]['content'])
        else:
            result = design_with_llm(st.session_state.get('final_prompt', ''))
    except Exception as e:
        result = {"text": f"❌ 生成失败：{str(e)}", "data": None}
    
    mod_data = result.get('data', {})
    if mod_data:
        new_mod = {
            "id": len(st.session_state.generated_mods) + 1,
            "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
            "desc": mod_data.get('desc', '基于你的构想'),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": result.get('text', '')
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
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 再次生成", key="regen_btn", use_container_width=True):
            st.session_state.mode = "explore"
            st.session_state.messages = []
            st.rerun()
    
    st.divider()

# ========================
# 侧边栏
# ========================
with st.sidebar:
    st.markdown("<h3 style='font-family:Creepster; color:#FFD700; text-align:center;'>📦 Mod 库</h3>", unsafe_allow_html=True)
    
    render_mod_history(st.session_state.generated_mods)
    
    st.markdown("---")
    
    st.write(f"💬 对话记录：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        render_download_section(st.session_state.generated_mods[-1])
    
    st.markdown("---")
    
    if st.button("🗑️ 清除全部记录", key="clear_all"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
