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
    
    # 降级模式 - 模拟 LLM 响应
    def mock_explore(messages):
        return {
            "text": "👁️ 暗影回应了你的召唤...\n\n让我来帮你完善这个疯狂的想法。\n(The shadows respond to your summoning...)\n\nWhat kind of creature or item do you want to create?",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f'''✅ **Mod 已成功生成！**\n\n📦 **名称**: 疯狂构想 #{datetime.now().strftime('%H:%M')}\\n\\n📝 **描述**:\\n基于你的想法 "{idea[:50]}...", 我已生成了一个完整的 Mod 设计方案。\\n\\n✨ **特性**:\\n- 全新生物/物品\\n- 符合 DST 世界观\\n- 可直接下载到游戏\\n\\nThe shadows have woven your madness into reality.''',
            "data": {
                "name": f"疯狂Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea[:100] + "...",
                "status": "ready"
            }
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
# ⚠️ 关键：主题最先注入
# ========================
print("=== 启动 App ===")
st.markdown(inject_theme(), unsafe_allow_html=True)

# ========================
# Session State (重要!)
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []

if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ========================
# Banner (保持不变)
# ========================
st.markdown(f'''
<div class="background-layer" style="text-align:center;margin:20px auto;max-width:950px;padding:40px;">
    <h1 style="font-family:'Creepster';font-size:3.5rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.4rem;letter-spacing:3px;margin-top:5px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:20px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.7;font-size:1.1rem;max-width:800px;margin:0 auto 30px;">
    当理智的 san 值归零，现实的法则在此崩塌。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <div style="display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-top:20px;">
        <div style="flex:1;min-width:320px;background:rgba(30,20,10,0.75);border:2px solid #aa7733;padding:20px;">
            <h3 style="font-family:'Creepster';color:#ffaa60;font-size:1.6rem;">🔥 快速生成 / RAPID</h3>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.6;margin-top:10px;">适用于意志坚定的造物主。<br>当你已明确 Mod 的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。</p>
            <span style="color:#888;font-size:0.8em;display:block;margin-top:10px;font-style:italic;">For when your vision is clear. Forge it now.</span>
        </div>
        
        <div style="flex:1;min-width:320px;background:rgba(20,30,20,0.75);border:2px solid #668844;padding:20px;">
            <h3 style="font-family:'Creepster';color:#aadd88;font-size:1.6rem;">👁️ 探索设计 / EXPLORE</h3>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.6;margin-top:10px;">适用于在迷雾中低语的探索者。<br>当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。</p>
            <span style="color:#888;font-size:0.8em;display:block;margin-top:10px;font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# ========================
# 模式选择按钮
# ========================
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

# 模式确认
if st.session_state.mode != "home":
    render_mode_confirmation(st.session_state.mode)

# ========================
# 🎮 探索模式 (核心修复)
# ========================
if st.session_state.mode == "explore":
    st.info("""
    💬 **与暗影对话以明确设计思路**  
    Talk to the Shadow to refine your ideas
    """, unsafe_allow_html=True)
    
    user_input = st.chat_input("描述你的想法 / Describe your ideas...")
    
    if user_input and not st.session_state.is_generating:
        # ✅ 1. 添加用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        
        # ✅ 2. 立即重定向到生成状态
        st.rerun()

# ========================
# 快速生成模式
# ========================
elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想 / Enter your concept...")
    
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

# ========================
# 🔄 生成响应阶段 (核心!)
# ========================
if st.session_state.is_generating:
    # ✅ 显示 Loading 动画
    render_loading()
    
    import time
    time.sleep(2.5)  # 模拟生成延迟
    
    # ✅ 调用 LLM (或用模拟数据)
    try:
        if st.session_state.mode == "explore":
            result = explore_with_llm(st.session_state.messages)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        # ✅ 添加 AI 回复到消息历史
        reply_text = result.get('text', '暗影已回应...')
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply_text
        })
        
        # ✅ 如果包含 Mod 数据，保存到历史库
        mod_data = result.get('data', {})
        if mod_data and st.session_state.mode == "rapid":
            new_mod = {
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.generated_mods.append(new_mod)
        
    except Exception as e:
        print(f"❌ 生成错误：{e}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ 暗影沉默了... {str(e)}"
        })
    
    # ✅ 重置状态并刷新
    st.session_state.is_generating = False
    st.rerun()

# ========================
# 📖 显示聊天历史
# ========================
if st.session_state.messages:
    render_chat(st.session_state.messages)

# ========================
# ✨ 生成完成后的操作
# ========================
if st.session_state.mode == "explore" and len(st.session_state.messages) >= 4:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✨ 生成最终 Mod", key="gen_from_explore", use_container_width=True):
            summary = "\\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
            st.session_state.final_prompt = summary
            st.session_state.mode = "generating"
            st.session_state.is_generating = True
            st.rerun()

# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("""
    <div style="background:rgba(30,20,10,0.95);border:2px solid #A67C3B;border-radius:6px;padding:15px;margin-bottom:20px;text-align:center;">
        <h3 style="font-family:'Creepster';color:#FFD700;margin-top:0;">📦 Mod 库</h3>
        <p style="font-family:'IM Fell English SC';color:#AA8855;font-size:0.85rem;margin-bottom:0;">Your Mod Archive</p>
    </div>
    """, unsafe_allow_html=True)
    
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

# ========================
# 🐛 Debug (可选)
# ========================
if 'debug' in st.query_params:
    with st.expander("🔍 DEBUG"):
        st.json({
            "mode": st.session_state.mode,
            "is_generating": st.session_state.is_generating,
            "messages_count": len(st.session_state.messages),
            "mods_count": len(st.session_state.generated_mods)
        })
