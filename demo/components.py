import streamlit as st


def render_chat(messages):
    """渲染聊天记录"""
    if not messages:
        return
    
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            
            st.markdown(f'''
            <div style="
                background: rgba(25,20,15,0.9);
                border-left: 4px solid {color};
                border: 1px solid rgba(166,124,59,0.3);
                padding: 15px;
                margin: 15px 0;
                border-radius: 0;
                color: #F5E6C8;
                font-family: 'IM Fell English SC', serif;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
            ">
                <b style="font-family:'Creepster';color:{color};font-size:1.2rem;">{name}</b><br>
                <span style="font-family:'IM Fell English SC';font-size:1.1rem;line-height:1.7;">{content}</span>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:rgba(25,20,15,0.9);padding:15px;margin:15px 0;border:1px solid rgba(166,124,59,0.3);color:#F5E6C8;'>{msg}</div>", unsafe_allow_html=True)


def render_loading():
    """渲染加载动画 - 饥荒风格"""
    st.markdown("""
    <div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 class="loading-text" style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        
        <!-- 旋转的荆棘图标 -->
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
        
        <style>
        @keyframes rotate {{ 
            from {{ transform: rotate(0deg); }} 
            to {{ transform: rotate(360deg); }} 
        }}
        @keyframes flicker {{ 
            0% {{ opacity: 0.7; text-shadow: 0 0 10px rgba(255,215,0,0.5); }} 
            50% {{ opacity: 1; text-shadow: 0 0 20px rgba(255,215,0,0.9); }} 
            100% {{ opacity: 0.8; text-shadow: 0 0 15px rgba(255,215,0,0.7); }} 
        }}
        .loading-text {{ animation: flicker 1.5s infinite alternate; }}
        </style>
    </div>
    """, unsafe_allow_html=True)


def render_mode_confirmation(mode):
    """模式确认动画"""
    config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    
    icon, color, text = config.get(mode, ("❓", "#888", "**未知模式**"))
    
    st.markdown(f'''
    <div class="mode-confirm" style="
        text-align:center;padding:15px;margin:20px 0;
        background:rgba(0,0,0,0.3);
        border:2px dashed {color};
        border-radius:0;
        animation: pulse 1.5s infinite;
    ">
        <h3 style="font-family:'Creepster';color:{color};font-size:2rem;">{icon} {text}</h3>
    </div>
    ''', unsafe_allow_html=True)


def render_mod_history(mods):
    """渲染 Mod 历史记录"""
    if not mods:
        st.markdown('''
        <div style="background:rgba(0,0,0,0.3);border:1px dashed #A67C3B;padding:20px;text-align:center;">
            <p style="font-family:'IM Fell English SC';color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
    
    for mod in mods:
        st.markdown(f'''
        <div style="background:rgba(30,20,10,0.7);border:1px solid #A67C3B;padding:12px;margin-bottom:10px;box-shadow:inset 0 0 10px rgba(0,0,0,0.5);">
            <strong style="font-family:'Creepster';color:#FFD700;">{mod['name']}</strong><br>
            <small style="color:#888;">{mod['date']}</small>
        </div>
        ''', unsafe_allow_html=True)


def render_download_section(mod):
    """渲染下载区域"""
    if not mod:
        return
    
    st.markdown("---")
    st.markdown(f'''
    <div style="background:rgba(30,20,10,0.8);border:2px solid #FFD700;padding:15px;box-shadow:0 0 20px rgba(255,215,0,0.2);">
        <h4 style="font-family:'Creepster';color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4>
        <p style="font-family:'IM Fell English SC';color:#aaa;font-size:0.9rem;margin-bottom:15px;">{mod.get('desc', '无描述')}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 立即下载", key=f"download_{mod['id']}", use_container_width=True):
            st.success(f"✅ {mod['name']} 已开始下载!")
    with col2:
        if st.button("🔄 重新生成", key=f"regen_{mod['id']}", use_container_width=True):
            st.info("正在重新生成该 Mod...")
