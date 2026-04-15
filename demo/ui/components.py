import streamlit as st


def render_banner():
    st.markdown("""
    <div style="
        background: rgba(20, 18, 15, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 220, 150, 0.15);
        box-shadow:
            0 0 40px rgba(0,0,0,0.6),
            inset 0 0 20px rgba(255, 200, 120, 0.05);
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 30px;
    ">
        <h1 style="
            font-family: 'Creepster', cursive;
            color: #ffd280;
            font-size: 2.5rem;
            margin: 0 0 8px 0;
            text-shadow: 0 0 15px rgba(255,180,60,0.3), 3px 3px 6px rgba(0,0,0,0.8);
        ">🌙 AI 饥荒 Mod 生成器</h1>
        <p style="
            color: rgba(200, 180, 140, 0.6);
            font-family: 'Griffy', cursive;
            font-size: 1.1rem;
            margin: 0;
            font-style: italic;
        ">Design nightmares for Don't Starve</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            icon = "🧑‍💻"
            bg = "rgba(50, 40, 25, 0.7)"
            border_color = "rgba(255, 200, 120, 0.2)"
            name = "你"
        else:
            icon = "🤖"
            bg = "rgba(30, 25, 15, 0.7)"
            border_color = "rgba(180, 220, 255, 0.15)"
            name = "AI 设计师"

        st.markdown(f"""
        <div style="
            background: {bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 15px 18px;
            margin-bottom: 12px;
            box-shadow: inset 0 0 12px rgba(0,0,0,0.4);
        ">
            <div style="
                font-family: 'Creepster', cursive;
                color: #ffd280;
                font-size: 0.85rem;
                margin-bottom: 6px;
                letter-spacing: 1px;
            ">{icon} {name}</div>
            <div style="
                color: #d4c4a0;
                font-family: 'Griffy', cursive;
                font-size: 1rem;
                line-height: 1.6;
            ">{content}</div>
        </div>
        """, unsafe_allow_html=True)
