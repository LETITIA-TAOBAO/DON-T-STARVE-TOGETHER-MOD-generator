import streamlit as st


def render_banner():
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
        max-width: 800px;
        text-align: center;
        position: relative;
    ">
        <div style="position: absolute; top: -10px; left: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(-45deg);">🌿</div>
        <div style="position: absolute; top: -10px; right: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(45deg);">🌿</div>
        <div style="position: absolute; bottom: -10px; left: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(-135deg);">🌿</div>
        <div style="position: absolute; bottom: -10px; right: -10px; font-size: 30px; opacity: 0.5; filter: grayscale(100%) brightness(0.7); transform: rotate(135deg);">🌿</div>
        
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
        
        <p style="
            font-family: 'Creepster', cursive;
            color: rgba(200, 160, 100, 0.9);
            font-size: 1.2rem;
            margin: 0 0 20px 0;
            letter-spacing: 4px;
            text-transform: uppercase;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        ">Don't Starve Together Mod Generator</p>
        
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
        
        <p style="
            font-family: 'Griffy', cursive;
            color: rgba(180, 160, 120, 0.7);
            font-size: 0.95rem;
            line-height: 1.6;
            font-style: italic;
            max-width: 600px;
            margin: 0 auto;
            letter-spacing: 1px;
        ">
            When sanity reaches zero, and shadow creatures lurk by the campfire,<br>
            the true creator awakens. This is not a workshop, but an altar of forbidden knowledge.<br>
            Weave nightmares with code, create madness on the edge of survival and destruction.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
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
