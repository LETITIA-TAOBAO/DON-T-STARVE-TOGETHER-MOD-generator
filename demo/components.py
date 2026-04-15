import streamlit as st

def render_banner():
    st.markdown("""
    <div style="text-align:center;margin:20px auto;max-width:900px;">
        <h1 style="font-family:'Creepster';font-size:3rem;color:#ffaa60;">饥荒 MOD 生成器</h1>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;">DON'T STARVE TOGETHER MOD GENERATOR</p>
        <hr style="width:50%;border-color:#5a3a1a;">
        <p style="font-family:'Griffy';color:#d4c4a0;">
        当理智的 san 值归零，现实的法则在此崩塌。<br>
        <span style="color:#88aa66;">You are no longer a survivor, but a Creator.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_chat(messages):
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍♂️ 求生者' if role == 'user' else '👁️ 暗影'
            st.markdown(f'<div style="background:rgba(30,20,10,0.7);padding:15px;border-left:4px solid {color};margin:10px 0;"><b style="color:{color};">{name}</b><br>{content}</div>', unsafe_allow_html=True)

def render_loading():
    st.markdown("""
    <div style="text-align:center;padding:30px;">
        <h2 style="font-family:'Creepster';color:#FFD700;">世界正在扭曲...</h2>
        <p style="font-family:'Griffy';color:#aa8855;">REALITY IS WARPING...</p>
    </div>
    """, unsafe_allow_html=True)

def render_mode_confirmation(mode):
    config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    icon, color, text = config.get(mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f'<div style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.3);border:2px dashed {color};"><h3 style="color:{color};">{icon} {text}</h3></div>', unsafe_allow_html=True)

def render_mod_history(mods):
    if not mods:
        st.info("暂无 Mod")
        return
    st.markdown("#### 📜 Mod 记录")
    for mod in mods:
        st.markdown(f"- **{mod['name']}** ({mod['date']})")

def render_download_section(mod):
    if not mod:
        return
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 下载"):
            st.success(f"{mod['name']} 已开始下载")
    with col2:
        if st.button("🔄 重新生成"):
            st.info("重新生成中...")
