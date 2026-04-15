import streamlit as st


def render_banner():
    """
    中央祭坛风格 Banner - 双语版 + 双模式说明
    """
    st.markdown("""
    <div style="
        background: linear-gradient(
            180deg,
            rgba(25, 20, 12, 0.9),
            rgba(15, 12, 8, 0.95)
        );
        border: 2px solid rgba(100, 80, 40, 0.4);
        border-top: 3px solid rgba(120, 90, 50, 0.5);
        border-bottom: 3px solid rgba(80, 60, 30, 0.6);
        box-shadow:
            0 0 40px rgba(0,0,0,0.6),
            inset 0 0 30px rgba(0,0,0,0.4),
            0 0 15px rgba(80, 120, 40, 0.1);
        border-radius: 8px;
        padding: 40px 30px;
        margin: 20px auto 40px auto;
        max-width: 900px;
        text-align: center;
        position: relative;
    ">
        <!-- 四角装饰性荆棘 -->
        <div style="position: absolute; top: -10px; left: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(-45deg);">🌿</div>
        <div style="position: absolute; top: -10px; right: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(45deg);">🌿</div>
        <div style="position: absolute; bottom: -10px; left: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(-135deg);">🌿</div>
        <div style="position: absolute; bottom: -10px; right: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(135deg);">🌿</div>
        
        <!-- 主标题：中文 -->
        <h1 style="
            font-family: 'Creepster', cursive;
            color: #ffd280;
            font-size: 3.2rem;
            margin: 0 0 5px 0;
            text-shadow:
                0 0 20px rgba(255, 150, 0, 0.4),
                0 0 40px rgba(255, 100, 0, 0.2),
                3px 3px 6px rgba(0,0,0,0.9);
            letter-spacing: 6px;
        ">饥荒MOD生成器</h1>
        
        <!-- 副标题：英文 -->
        <p style="
            font-family: 'Creepster', cursive;
            color: rgba(200, 160, 100, 0.9);
            font-size: 1.2rem;
            margin: 0 0 20px 0;
            letter-spacing: 4px;
            text-transform: uppercase;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        ">Don't Starve Together Mod Generator</p>
        
        <!-- 分割线 -->
        <div style="
            width: 60%;
            height: 2px;
            margin: 0 auto 25px auto;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(100, 140, 60, 0.4),
                rgba(180, 140, 80, 0.4),
                rgba(100, 140, 60, 0.4),
                transparent
            );
        "></div>
        
        <!-- 中文介绍 -->
        <p style="
            font-family: 'Griffy', cursive;
            color: rgba(220, 200, 160, 0.95);
            font-size: 1.15rem;
            line-height: 1.8;
            margin: 0 0 15px 0;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        ">
            当理智值归零，暗影生物在篝火边缘游荡，真正的造物主开始苏醒。<br>
            这里不是工坊，而是<span style="color: #ffaa60;">禁忌知识的祭坛</span>。<br>
            用代码编织噩梦，在生存与毁灭的边界创造疯狂。
        </p>
        
        <!-- 英文介绍 -->
        <p style="
            font-family: 'Griffy', cursive;
            color: rgba(180, 160, 120, 0.7);
            font-size: 0.95rem;
            line-height: 1.6;
            font-style: italic;
            max-width: 600px;
            margin: 0 auto 30px auto;
            letter-spacing: 1px;
        ">
            When sanity reaches zero, and shadow creatures lurk by the campfire,<br>
            the true creator awakens. This is not a workshop, but an altar of forbidden knowledge.<br>
            Weave nightmares with code, create madness on the edge of survival and destruction.
        </p>

        <!-- 🎮 双模式说明卡片 -->
        <div style="
            width: 40%;
            height: 1px;
            margin: 25px auto;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 140, 60, 0.3),
                transparent
            );
        "></div>
        
        <div style="
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            max-width: 800px;
            margin: 0 auto;
        ">
            <!-- 速铸模式卡片 -->
            <div style="
                flex: 1;
                min-width: 280px;
                background: rgba(40, 30, 20, 0.6);
                border: 1px solid rgba(255, 180, 80, 0.2);
                border-top: 3px solid rgba(255, 140, 60, 0.5);
                border-radius: 6px;
                padding: 20px;
                text-align: left;
                position: relative;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.4);
            ">
                <div style="
                    font-family: 'Creepster', cursive;
                    color: #ffaa60;
                    font-size: 1.3rem;
                    margin-bottom: 8px;
                    letter-spacing: 2px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span style="font-size: 1.5rem;">⚡</span>
                    速铸模式
                    <span style="font-size: 0.75rem; color: rgba(200,180,140,0.6); margin-left: auto; letter-spacing: 1px;">RAPID FORGING</span>
                </div>
                <p style="
                    font-family: 'Griffy', cursive;
                    color: rgba(220, 200, 170, 0.9);
                    font-size: 0.95rem;
                    line-height: 1.7;
                    margin: 0 0 10px 0;
                ">
                    当你的脑海中已然浮现完整的疯狂蓝图，直接将其实物化。<br>
                    <span style="color: #ffaa60;">无需徘徊</span>，立即生成可执行的Mod圣物。
                </p>
                <p style="
                    font-family: 'Griffy', cursive;
                    color: rgba(180, 160, 130, 0.7);
                    font-size: 0.8rem;
                    font-style: italic;
                    line-height: 1.5;
                    margin: 0;
                    border-top: 1px solid rgba(255,200,150,0.1);
                    padding-top: 8px;
                ">
                    When the complete blueprint of madness haunts your mind, materialize it directly. No wandering—generate the executable Mod artifact immediately.
                </p>
                <div style="position: absolute; bottom: -8px; right: -5px; font-size: 18px; opacity: 0.4; filter: grayscale(100%) brightness(0.6);">🌿</div>
            </div>

            <!-- 深潜模式卡片 -->
            <div style="
                flex: 1;
                min-width: 280px;
                background: rgba(30, 35, 25, 0.6);
                border: 1px solid rgba(140, 180, 100, 0.2);
                border-top: 3px solid rgba(100, 160, 80, 0.5);
                border-radius: 6px;
                padding: 20px;
                text-align: left;
                position: relative;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.4);
            ">
                <div style="
                    font-family: 'Creepster', cursive;
                    color: #aadd88;
                    font-size: 1.3rem;
                    margin-bottom: 8px;
                    letter-spacing: 2px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span style="font-size: 1.5rem;">👁️</span>
                    深潜模式
                    <span style="font-size: 0.75rem; color: rgba(200,180,140,0.6); margin-left: auto; letter-spacing: 1px;">DEEP EXPLORATION</span>
                </div>
                <p style="
                    font-family: 'Griffy', cursive;
                    color: rgba(220, 200, 170, 0.9);
                    font-size: 0.95rem;
                    line-height: 1.7;
                    margin: 0 0 10px 0;
                ">
                    当灵感如迷雾中的低语，与古老存在对话以剥离现实的伪装。<br>
                    <span style="color: #aadd88;">逐步揭开</span>设计的面纱，直至真相足够清晰，方可铸就永恒。
                </p>
                <p style="
                    font-family: 'Griffy', cursive;
                    color: rgba(180, 160, 130, 0.7);
                    font-size: 0.8rem;
                    font-style: italic;
                    line-height: 1.5;
                    margin: 0;
                    border-top: 1px solid rgba(200,220,150,0.1);
                    padding-top: 8px;
                ">
                    When inspiration whispers like mist, converse with ancient beings to peel away reality's disguise. Gradually unveil the design until truth is clear enough to forge eternity.
                </p>
                <div style="position: absolute; bottom: -8px; right: -5px; font-size: 18px; opacity: 0.4; filter: grayscale(100%) brightness(0.6);">🌿</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
    """
    渲染聊天记录 - 双语标签
    """
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            icon = "🧑‍💻"
            bg = "rgba(40, 30, 18, 0.75)"
            border_left = "4px solid rgba(180, 140, 80, 0.4)"
            name_zh = "求生者"
            name_en = "SURVIVOR"
            color = "#e8c888"
        else:
            icon = "👁️"
            bg = "rgba(25, 20, 12, 0.8)"
            border_left = "4px solid rgba(80, 120, 40, 0.5)"
            name_zh = "暗影设计师"
            name_en = "SHADOW DESIGNER"
            color = "#a8d080"

        st.markdown(f"""
        <div style="
            background: {bg};
            border: 1px solid rgba(100, 80, 40, 0.25);
            border-left: {border_left};
            border-radius: 4px;
            padding: 15px 18px;
            margin-bottom: 12px;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.4);
            position: relative;
        ">
            <div style="
                font-family: 'Creepster', cursive;
                color: {color};
                font-size: 0.9rem;
                margin-bottom: 8px;
                letter-spacing: 2px;
                opacity: 0.9;
            ">
                {icon} {name_zh} <span style="font-size: 0.7rem; opacity: 0.6; margin-left: 8px;">{name_en}</span>
            </div>
            <div style="
                color: #e0d0b0;
                font-family: 'Griffy', cursive;
                font-size: 1rem;
                line-height: 1.6;
            ">{content}</div>
        </div>
        """, unsafe_allow_html=True)


def render_loading(zh_text="正在生成世界...", en_text="GENERATING WORLD..."):
    """
    饥荒风格的加载动画 - 双语
    """
    loading_html = f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 50px;
        background: linear-gradient(
            180deg,
            rgba(20, 16, 10, 0.95),
            rgba(10, 8, 5, 0.98)
        );
        border: 2px solid rgba(100, 80, 40, 0.5);
        border-radius: 8px;
        margin: 30px auto;
        max-width: 500px;
        box-shadow: 
            0 0 40px rgba(0,0,0,0.8),
            inset 0 0 30px rgba(255, 150, 50, 0.05);
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: 5px; left: 5px; font-size: 20px; opacity: 0.3; filter: grayscale(100%);">🌿</div>
        <div style="position: absolute; top: 5px; right: 5px; font-size: 20px; opacity: 0.3; filter: grayscale(100%); transform: scaleX(-1);">🌿</div>
        <div style="position: absolute; bottom: 5px; left: 5px; font-size: 20px; opacity: 0.3; filter: grayscale(100%); transform: scaleY(-1);">🌿</div>
        <div style="position: absolute; bottom: 5px; right: 5px; font-size: 20px; opacity: 0.3; filter: grayscale(100%); transform: scale(-1, -1);">🌿</div>
        
        <div style="
            width: 70px;
            height: 70px;
            border: 3px solid rgba(100, 80, 40, 0.3);
            border-top: 3px solid #ffd280;
            border-radius: 50%;
            animation: spin 2s linear infinite;
            box-shadow: 0 0 20px rgba(255, 150, 0, 0.3);
            position: relative;
        ">
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 30px;
                animation: counter-spin 2s linear infinite;
            ">🌙</div>
        </div>
        
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        @keyframes counter-spin {{
            0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
            100% {{ transform: translate(-50%, -50%) rotate(-360deg); }}
        }}
        </style>
        
        <p style="
            margin-top: 25px;
            font-family: 'Creepster', cursive;
            color: #ffd280;
            font-size: 1.6rem;
            letter-spacing: 4px;
            text-shadow: 0 0 20px rgba(255, 150, 0, 0.5);
            margin-bottom: 5px;
        ">
            {zh_text}
        </p>
        
        <p style="
            font-family: 'Griffy', cursive;
            color: rgba(200, 180, 140, 0.7);
            font-size: 0.9rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin: 0;
        ">
            {en_text}
        </p>
        
        <p style="
            margin-top: 15px;
            font-family: 'Griffy', cursive;
            color: rgba(180, 160, 120, 0.5);
            font-size: 0.85rem;
            font-style: italic;
        ">
            请不要熄灭篝火 / Don't let the fire die
        </p>
    </div>
    """
    st.markdown(loading_html, unsafe_allow_html=True)


def render_mode_indicator(zh_mode, en_mode):
    """
    显示当前选中的模式 - 双语
    """
    indicator_html = f"""
    <div style="
        background: linear-gradient(
            90deg,
            rgba(80, 60, 30, 0.4),
            rgba(120, 90, 40, 0.6),
            rgba(80, 60, 30, 0.4)
        );
        border: 1px solid rgba(255, 180, 80, 0.3);
        border-left: 4px solid #ffd280;
        border-right: 4px solid #ffd280;
        padding: 15px 24px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 
            0 4px 15px rgba(0,0,0,0.4),
            inset 0 0 20px rgba(0,0,0,0.3);
        animation: glow 2s ease-in-out infinite alternate;
    ">
        <div style="
            font-family: 'Creepster', cursive;
            color: #ffd280;
            font-size: 1.4rem;
            letter-spacing: 4px;
            text-shadow: 0 0 15px rgba(255, 150, 0, 0.4);
            margin-bottom: 4px;
        ">
            ⚡ {zh_mode} ⚡
        </div>
        <div style="
            font-family: 'Griffy', cursive;
            color: rgba(200, 180, 140, 0.6);
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-transform: uppercase;
        ">
            {en_mode}
        </div>
    </div>
    <style>
    @keyframes glow {{
        from {{ box-shadow: 0 4px 15px rgba(0,0,0,0.4), inset 0 0 20px rgba(0,0,0,0.3); }}
        to {{ box-shadow: 0 4px 25px rgba(255, 150, 0, 0.2), inset 0 0 20px rgba(0,0,0,0.3); }}
    }}
    </style>
    """
    st.markdown(indicator_html, unsafe_allow_html=True)
