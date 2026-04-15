import streamlit as st


def render_banner():
    """渲染顶部 Banner"""
    banner_html = '''<div style="text-align:center;margin:20px auto;max-width:950px;padding:40px;">
        <h1 style="font-family:'Creepster';font-size:3.5rem;color:#ffaa60;letter-spacing:5px;">饥荒 MOD 生成器</h1>
        <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.4rem;letter-spacing:3px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
        
        <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:20px auto;opacity:0.7;">
        
        <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.7;font-size:1.1rem;">
        当理智归零，现实崩塌。<br>
        <span style="color:#88aa66;">You are no longer a survivor, but a Creator of Nightmares.</span><br>
        你不再是求生者，而是编织噩梦的造物主。<br>
        <span style="color:#88aa66;">Weave your madness into the Constant.</span>
        </p>
    </div>'''
    st.markdown(banner_html, unsafe_allow_html=True)


def render_chat(messages):
    """渲染聊天记录"""
    if not messages:
        return
    
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍♂️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            
            chat_html = f'<div style="background:rgba(25,20,15,0.9);border-left:4px solid {color};padding:15px;margin:15px 0;"><b style="color:{color};font-family:Creepster;">{name}</b><br>{content}</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:rgba(25,20,15,0.9);padding:15px;margin:15px 0;">{msg}</div>', unsafe_allow_html=True)


def render_loading():
    """渲染加载动画"""
    loading_html = '''<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;animation:flicker 1.5s infinite alternate;">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
        <style>@keyframes flicker{0%{opacity:0.7}50%{opacity:1}100%{opacity:0.8}}@keyframes rotate{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}</style>
    </div>'''
    st.markdown(loading_html, unsafe_allow_html=True)


def render_mode_confirmation(mode):
    """模式确认"""
    config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    
    icon, color, text = config.get(mode, ("❓", "#888", "**未知模式**"))
    
    confirm_html = f'<div style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.3);border:2px dashed {color};animation:pulse 1.5s infinite;"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>'
    st.markdown(confirm_html, unsafe_allow_html=True)


def render_mod_history(mods):
    """Mod 历史记录"""
    if not mods:
        st.markdown('<div style="background:rgba(0,0,0,0.3);border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;">暂无 Mod</p></div>', unsafe_allow_html=True)
        return
    
    st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录</h4>", unsafe_allow_html=True)
    
    for mod in mods:
        mod_html = f'<div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="font-family:Creepster;color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>'
        st.markdown(mod_html, unsafe_allow_html=True)


def render_download_section(mod):
    """下载区域"""
    if not mod:
        return
    
    st.markdown("---")
    download_html = '<div style="background:rgba(30,20,10,0.8);border:2px solid #FFD700;padding:15px;"><h4 style="color:#FFD700;font-family:Creepster;">⬇️ 下载 Mod</h4></div>'
    st.markdown(download_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 下载", key=f"download_{mod['id']}"):
            st.success(f"{mod['name']} 已开始下载")
    with col2:
        if st.button("🔄 重新生成", key=f"regen_{mod['id']}"):
            st.info("重新生成中...")


__all__ = [
    'render_banner',
    'render_chat',
    'render_loading',
    'render_mode_confirmation',
    'render_mod_history',
    'render_download_section'
]
