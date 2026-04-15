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
    print("使用降级模式（模拟回复）")
    
    def mock_explore(messages):
        return {
            "text": "👁️ 暗影在倾听...\n请告诉我更多关于你的想法。\n(Sounds echoing... Tell me more of your vision.)",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f"""
            ✅ Mod 已生成！
            
            名称：疯狂的构想 #{datetime.now().strftime("%H:%M")}
            
            描述：基于你的描述 '{idea[:50]}...'
            
            [点击下方按钮下载 .zip 文件]
            """,
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
try:
    from theme import inject_theme
    from components import (
        render_banner, 
        render_chat, 
        render_loading, 
        render_mode_confirmation,
        render_mod_history, 
        render_download_section
    )
except Exception as e:
    st.error(f"⚠️ 组件模块加载失败：{str(e)}")
    st.stop()

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
            print(f"ℹ️ 背景图未找到：{path}，使用默认网络图片")
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"❌ 背景图读取失败：{e}")
        return None

bg_base64 = get_base64_image(bg_path)

# ========================
# 注入主题
# ========================
if bg_base64:
    print(f"✅ 背景图加载成功 ({len(bg_base64)}字符)")
else:
    print("⚠️ 使用默认背景")

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
# 主界面渲染
# ========================
render_banner()

# 模式选择按钮
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
# 各模式处理逻辑
# ========================
if st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想 / Enter your complete concept...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.mode = "generating"
        st.rerun()

elif st.session_state.mode == "explore":
    st.markdown("""
    <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px dashed #A67C3B;">
        💬 与暗影进行多轮对话，逐步明确你的 Mod 设计思路。完成后点击右侧按钮生成最终方案。
        <br><span style="color:#888; font-size:0.9em;">Have a multi-turn dialogue to refine your design.</span>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.chat_input("描述你的想法 / Describe your ideas...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 模拟 AI 回复（实际替换为 API 调用）
        reply_text = "👁️ 暗影回应了你的召唤...\n让我们共同探索这个疯狂的世界。\n(The shadows respond... Let's explore this mad world together.)"
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()
    
    # 完成生成的按钮
    if len(st.session_state.messages) >= 2:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
                summary = "\\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
                st.session_state.final_prompt = summary
                st.session_state.mode = "generating"
                st.rerun()

# ========================
# 生成阶段
# ========================
if st.session_state.mode == "generating":
    render_loading()
    
    import time
    time.sleep(2)  # 模拟生成延迟
    
    # 调用真正的 LLM 函数
    try:
        if st.session_state.mode == "rapid":
            result = design_with_llm(st.session_state.messages[0]['content'])
        else:
            result = design_with_llm(st.session_state.get('final_prompt', ''))
    except Exception as e:
        result = {"text": f"❌ 生成失败：{str(e)}", "data": None}
    
    # 保存生成的 Mod
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
# 侧边栏：历史对话 & Mod 库
# ========================
with st.sidebar:
    st.markdown("""
    <div style="
        background: rgba(20, 15, 10, 0.9);
        border: 2px solid #A67C3B;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5);
    ">
        <h3 style="font-family:'Creepster'; color:#FFD700; margin-top:0;">📦 Mod 历史库</h3>
        <p style="font-family:'IM Fell English SC'; color:#D4C4A0; font-size:0.9rem;">Your Mod Archive</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_mod_history(st.session_state.generated_mods)
    
    st.divider()
    
    st.write(f"💬 本次对话：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        render_download_section(st.session_state.generated_mods[-1])
    
    st.divider()
    
    if st.button("🗑️ 清除全部记录", key="clear_all"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
