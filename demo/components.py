import streamlit as st


def render_chat(messages):
    if not messages:
        return
    
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍️ 求生者' if role == 'user' else '👁️ 暗影'
            
            with st.container():
                st.markdown(f'**{name}**', unsafe_allow_html=True)
                st.markdown(content)
                st.markdown("---")


def render_loading():
    """加载动画"""
    st.markdown("""
    <div style="text-align:center;padding:30px;margin:20px 0;">
        <h2 style="font-family:'Creepster';color:#FFD700;font-size:2rem;text-shadow:0 0 15px rgba(255,215,0,0.7);">
            世界正在扭曲......<br>REALITY IS WARPING...
        </h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;">
            暗影正在编织你的疯狂...<br>The shadows are weaving your madness...
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_mode_confirmation(mode):
    """模式确认"""
    config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活!**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活!**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成!**")
    }
    
    icon, color, text = config.get(mode, ("❓", "#888", "**未知模式**"))
    
    st.markdown(f"""
    <div style="text-align:center;margin:20px 0;padding:15px;background:rgba(0,0,0,0.3);border:2px dashed {color};border-radius:6px;">
        <h3 style="font-family:'Creepster';color:{color};">{icon} {text}</h3>
    </div>
    """, unsafe_allow_html=True)


def render_mod_history(mods):
    if not mods:
        st.info("暂无 Mod 创作记录\nNo Mods Created Yet")
        return
    
    st.markdown("#### 📜 创作记录 / CREATIONS")
    
    for mod in mods:
        st.markdown(f"""
        <div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;border-radius:6px;padding:10px;margin-bottom:8px;">
            <strong style="font-family:'Creepster';color:#FFD700;">{mod['name']}</strong><br>
            <small style="color:#888;">{mod['date']}</small>
        </div>
        """, unsafe_allow_html=True)


def render_download_section(mod):
    if not mod:
        return
    
    st.markdown("### ⬇️ 下载你的 Mod")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 立即下载", use_container_width=True):
            st.success(f"✅ {mod['name']} 已开始下载!")
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            st.info("正在重新生成该 Mod...")


def render_banner():
    """主 Banner - 简化版避免 HTML 问题"""
    st.markdown("""
    <div style="text-align:center;margin:20px auto;max-width:900px;">
        <h1 style="font-family:'Creepster';font-size:3.5rem;color:#ffaa60;letter-spacing:4px;">饥荒 MOD 生成器</h1>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.3rem;">DON'T STARVE TOGETHER MOD GENERATOR</p>
        
        <hr style="width:50%;border-color:#5a3a1a;">
        
        <p style="font-family:'Griffy';color:#d4c4a0;line-height:1.6;">
        当理智的 san 值归零，现实的法则在此崩塌。<br>
        <span style="color:#88aa66;">You are no longer a survivor, but a Creator of Nightmares.</span><br>
        你不再是苟延残喘的求生者，而是编织噩梦的造物主。
        </p>
        
        <hr style="width:40%;border-color:#5a3a1a;">
        
        <div style="display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-top:20px;">
            <div style="flex:1;min-width:280px;background:rgba(30,20,10,0.7);border:2px solid #aa7733;padding:15px;">
                <h3 style="font-family:'Creepster';color:#ffaa60;">🔥 快速生成 / RAPID</h3>
                <p style="font-family:'Griffy';color:#d4c4a0;">适用于意志坚定的造物主</p>
            </div>
            <div style="flex:1;min-width:280px;background:rgba(20,30,20,0.7);border:2px solid #668844;padding:15px;">
                <h3 style="font-family:'Creepster';color:#aadd88;">👁️ 探索设计 / EXPLORE</h3>
                <p style="font-family:'Griffy';color:#d4c4a0;">适用于在迷雾中低语的探索者</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
