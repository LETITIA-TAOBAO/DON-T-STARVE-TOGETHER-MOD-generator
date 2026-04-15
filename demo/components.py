import streamlit as st


def render_banner():
    """渲染顶部 Banner - 包含完整说明"""
    banner = '''<div style="text-align:center;margin:20px auto;max-width:950px;padding:50px;">
        <h1 style="font-family:'Creepster';font-size:3.8rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
        <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.5rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
        
        <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
        
        <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.8;font-size:1.15rem;max-width:850px;margin:0 auto 35px;position:relative;z-index:2;">
        当理智的san值归零，现实的法则在此崩塌。<br>
        <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
        你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
        在永恒领域的边缘，用代码重塑你的疯狂。<br>
        <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">Weave your madness into the Constant.</span>
        </p>
        
        <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:30px auto;opacity:0.7;">
        
        <!-- 模式说明卡片 -->
        <div style="display:flex;gap:25px;flex-wrap:wrap;justify-content:center;margin-top:30px;">
            <div class="info-card" style="flex:1;min-width:300px;background:rgba(30,20,10,0.75);border:2px solid #aa7733;padding:25px;position:relative;">
                <div style="font-family:'Creepster';color:#ffaa60;font-size:1.7rem;text-align:center;margin-bottom:15px;">🔥 快速生成 / RAPID</div>
                <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">
                适用于意志坚定的造物主。<br>
                当你已明确Mod的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。<br>
                <span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when your vision is clear. Forge it now.</span>
                </p>
            </div>
            
            <div class="info-card" style="flex:1;min-width:300px;background:rgba(20,30,20,0.75);border:2px solid #668844;padding:25px;position:relative;">
                <div style="font-family:'Creepster';color:#aadd88;font-size:1.7rem;text-align:center;margin-bottom:15px;">👁️ 探索设计 / EXPLORE</div>
                <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">
                适用于在迷雾中低语的探索者。<br>
                当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。<br>
                <span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span>
                </p>
            </div>
        </div>
    </div>'''
    st.markdown(banner, unsafe_allow_html=True)


def render_chat(messages):
    if not messages:
        return
    
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍♂️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            
            chat_box = f'<div class="chat-box" style="border-left-color:{color} !important;"><b style="font-family:Creepster;color:{color};font-size:1.2rem;">{name}</b><br><span style="font-size:1.1rem;line-height:1.7;">{content}</span></div>'
            st.markdown(chat_box, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box">{msg}</div>', unsafe_allow_html=True)


def render_loading():
    st.markdown('''<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 class="loading-text" style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
    </div>''', unsafe_allow_html=True)


def render_mode_confirmation(mode):
    config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    icon, color, text = config.get(mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f'<div class="mode-confirm" style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.3);border:2px dashed {color};"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>', unsafe_allow_html=True)


def render_mod_history(mods):
    if not mods:
        st.markdown('<div style="background:rgba(0,0,0,0.3);border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p></div>', unsafe_allow_html=True)
        return
    
    st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
    for mod in mods:
        st.markdown(f'<div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="font-family:Creepster;color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>', unsafe_allow_html=True)


def render_download_section(mod):
    if not mod:
        return
    st.markdown("---")
    st.markdown(f'<div style="background:rgba(30,20,10,0.8);border:2px solid #FFD700;padding:15px;"><h4 style="font-family:Creepster;color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4><p style="color:#aaa;font-size:0.9rem;margin-bottom:15px;">{mod.get("desc", "")}</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 下载", key=f"download_{mod['id']}", use_container_width=True):
            st.success(f"{mod['name']} 已开始下载!")
    with col2:
        if st.button("🔄 重新生成", key=f"regen_{mod['id']}", use_container_width=True):
            st.info("正在重新生成该 Mod...")


__all__ = ['render_banner', 'render_chat', 'render_loading', 'render_mode_confirmation', 'render_mod_history', 'render_download_section']
