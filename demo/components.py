import streamlit as st


def render_banner():
    """渲染顶部 Banner"""
    st.markdown("""
    <div style="
        background: rgba(20, 15, 10, 0.75);
        border: 3px solid #A67C3B;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        max-width: 950px;
        margin: 20px auto;
        box-shadow: 0 0 50px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(0, 0, 0, 0.6);
        position: relative;
    ">
        <h1 style="
            font-family: 'Creepster', cursive;
            font-size: 3.8rem;
            margin: 0;
            color: #ffaa60;
            text-shadow: 0 0 25px rgba(255, 170, 96, 0.8);
            letter-spacing: 5px;
        ">饥荒 MOD 生成器</h1>

        <p style="
            font-family: 'Griffy', cursive;
            color: #aa8855;
            font-size: 1.4rem;
            letter-spacing: 3px;
            margin-top: 5px;
            text-transform: uppercase;
            text-align: center;
        ">DON'T STARVE TOGETHER MOD GENERATOR</p>

        <hr style="border: 0; border-top: 2px solid #5a3a1a; width: 50%; margin: 20px auto; opacity: 0.7;">

        <p style="
            font-family: 'Griffy', cursive;
            font-size: 1.1rem;
            line-height: 1.7;
            color: #d4c4a0;
            max-width: 800px;
            margin: 0 auto 30px auto;
            text-shadow: 1px 1px 3px #000;
            text-align: center;
        ">
        当理智的 san 值归零，现实的法则在此崩塌。<br>
        <span style="color:#88aa66; text-shadow: 0 0 10px rgba(136, 170, 102, 0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
        你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
        在永恒领域的边缘，用代码重塑你的疯狂。<br>
        <span style="color:#88aa66; text-shadow: 0 0 10px rgba(136, 170, 102, 0.5);">Weave your madness into the Constant.</span>
        </p>

        <hr style="border: 0; border-top: 2px solid #5a3a1a; width: 40%; margin: 25px auto; opacity: 0.7;">

        <div style="display:flex; gap:20px; flex-wrap:wrap; justify-content:center;">
            <div style="
                flex: 1; min-width: 320px;
                background: rgba(30, 20, 10, 0.7);
                border: 2px solid #aa7733;
                padding: 20px;
                border-radius: 6px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(0, 0, 0, 0.5);
            ">
                <div style="font-family:'Creepster'; color:#ffaa60; font-size:1.7rem; text-align:center;">🔥 快速生成 / RAPID</div>
                <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.95rem; margin-top:10px; line-height:1.7;">
                适用于意志坚定的造物主。<br>当你已明确 Mod 的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。<br>
                <span style="color:#888; font-size:0.8em; display:block; margin-top:10px; font-style:italic;">For when your vision is clear. Forge it now.</span>
                </p>
            </div>

            <div style="
                flex: 1; min-width: 320px;
                background: rgba(20, 30, 20, 0.7);
                border: 2px solid #668844;
                padding: 20px;
                border-radius: 6px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(0, 0, 0, 0.5);
            ">
                <div style="font-family:'Creepster'; color:#aadd88; font-size:1.7rem; text-align:center;">👁️ 探索设计 / EXPLORE</div>
                <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.95rem; margin-top:10px; line-height:1.7;">
                适用于在迷雾中低语的探索者。<br>当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。<br>
                <span style="color:#888; font-size:0.8em; display:block; margin-top:10px; font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
    """渲染聊天记录"""
    if not messages:
        return
    
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            css_class = 'user' if role == 'user' else 'assistant'
            icon_color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            
            st.markdown(f"""
            <div class='chat-box {css_class}' style='
                background: rgba(25, 20, 15, 0.9);
                border-left: 4px solid {icon_color} !important;
                padding: 15px 20px;
                margin: 15px 0;
                border-radius: 8px;
                color: #F5E6C8;
                font-family: 'IM Fell English SC', serif !important;
                box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6);
                max-width: 95%;
            '>
                <b style="font-family:'Creepster'; font-size:1.2rem; color:{icon_color}; display:block; margin-bottom:8px; text-shadow: 0 0 8px {icon_color};">
                    {name}
                </b>
                <div style="font-size:1.1rem; line-height:1.7;">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-box' style='
                background: rgba(25, 20, 15, 0.9);
                padding: 15px 20px;
                margin: 15px 0;
                border-radius: 8px;
                color: #F5E6C8;
                font-family: 'IM Fell English SC', serif !important;
                box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6);
            '>
                {msg}
            </div>
            """, unsafe_allow_html=True)


def render_loading():
    """渲染加载动画"""
    st.markdown("""
    <div style="text-align: center; padding: 40px; margin: 30px 0;">
        <div style="
            font-family: 'Creepster', cursive;
            font-size: 2.5rem;
            color: #FFD700;
            text-align: center;
            animation: flicker 1.5s infinite alternate;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
        ">世界正在扭曲......<br>REALITY IS WARPING...</div>

        <div style="
            font-family: 'IM Fell English SC';
            font-size: 1.2rem;
            color: #aa8855;
            margin-top: 20px;
            animation: float 3s ease-in-out infinite;
        ">
            暗影正在编织你的疯狂......<br>The shadows are weaving your madness...
        </div>

        <style>
        @keyframes flicker {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.8; }
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        </style>
    </div>
    """, unsafe_allow_html=True)


def render_mode_confirmation(mode):
    """渲染模式确认动画"""
    mode_config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活!**\\nRAPID GENERATION ACTIVATED!"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活!**\\nDEEP EXPLORATION ACTIVATED!"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**\\nREALITY REWRITING IN PROGRESS..."),
        "generated": ("✅", "#66aa66", "**Mod 已完成!**\\nMOD COMPLETED!")
    }
    
    config = mode_config.get(mode, ("❓", "#888", "**未知模式**"))
    icon, color, text = config
    
    st.markdown(f"""
    <div style="
        color: {color};
        font-family: 'Creepster', cursive;
        font-size: 2rem;
        text-align: center;
        margin: 20px 0;
        padding: 15px 30px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 6px;
        border: 2px dashed {color};
        box-shadow: 0 0 20px {color};
        animation: pulse 1.5s infinite;
    ">{icon} {text}</div>
    """, unsafe_allow_html=True)


def render_mod_history(mods):
    """渲染侧边栏 Mod 历史记录"""
    if not mods:
        st.markdown("""
        <div style="
            background: rgba(0, 0, 0, 0.3);
            border: 1px dashed #A67C3B;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
        ">
            <p style="font-family:'IM Fell English SC'; color:#888; font-size:0.9rem;">No Mods Created Yet<br>暂无创作的 Mod</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("<h4 style='font-family:Griffy; color:#AA7733; margin-bottom:15px;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
    
    for mod in mods:
        with st.container():
            st.markdown(f"""
            <div style="
                background: rgba(30, 20, 10, 0.7);
                border: 1px solid #A67C3B;
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 10px;
                box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            ">
                <div style="font-family:'Creepster'; color:#FFD700; font-size:1.1rem;">{mod['name']}</div>
                <div style="font-family:'IM Fell English SC'; color:#888; font-size:0.8rem; margin-top:5px;">
                    {mod['date']} • {mod.get('status', 'ready')}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_download_section(mod):
    """渲染下载区域"""
    if not mod:
        return
    
    st.markdown("---")
    st.markdown(f"""
    <div style="
        background: rgba(30, 20, 10, 0.8);
        border: 2px solid #FFD700;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    ">
        <h4 style="font-family:'Creepster'; color:#FFD700; margin-top:0;">⬇️ 下载 Mod</h4>
        <p style="font-family:'IM Fell English SC'; color:#D4C4A0; font-size:0.9rem;">Download Your Creation</p>
        <div style="font-size:0.9rem; color:#aaa; margin-bottom:15px;">{mod.get('desc', '无描述')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 立即下载", key=f"download_{mod['id']}", use_container_width=True):
            st.success(f"✅ {mod['name']} 已开始下载!")
    with col2:
        if st.button("🔄 重新生成", key=f"regen_{mod['id']}", use_container_width=True):
            st.info("正在重新生成该 Mod...")


# 修复：确保所有函数都被导出
__all__ = [
    'render_banner',
    'render_chat',
    'render_loading',
    'render_mode_confirmation',
    'render_mod_history',
    'render_download_section'
]
