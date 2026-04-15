import streamlit as st
import random

def render_banner():
    st.markdown("""
    <div style="
        background: rgba(10,8,5,0.95);
        border: 3px solid #a67c3b;
        border-radius: 12px;
        padding: 60px;
        text-align:center;
        max-width:900px;
        margin:auto;
        box-shadow: 0 0 60px rgba(0,0,0,0.9);
    ">

        <h1 style="
            font-family:Creepster;
            font-size:4rem;
            color:#ffd280;
            letter-spacing:8px;
        ">
        饥荒MOD生成器
        </h1>

        <p style="font-family:Creepster;color:#aa8855;">
        DON'T STARVE TOGETHER MOD GENERATOR
        </p>

        <hr style="margin:25px 0;">

        <p style="font-family:Griffy;color:#d4c4a0;font-size:1.1rem;">
        当世界濒临崩坏，你将成为规则的编织者。<br>
        在理智与疯狂之间，创造属于你的存在。<br><br>

        When the world begins to fracture, you become its architect.<br>
        Between sanity and madness, forge your own creation.
        </p>

        <hr style="margin:25px 0;">

        <div style="display:flex;gap:30px;justify-content:center;flex-wrap:wrap;">

            <div style="border:2px solid #ffaa60;padding:20px;">
                <b>快速生成</b><br>
                RAPID GENERATION<br><br>
                适用于已有完整想法的造物主。<br>
                直接生成完整Mod并导出。<br><br>

                For creators with a clear vision.<br>
                Instantly generate a complete playable mod.
            </div>

            <div style="border:2px solid #88aa66;padding:20px;">
                <b>探索设计</b><br>
                DEEP EXPLORATION<br><br>
                从混沌中构建灵感。<br>
                通过对话逐步完善设计。<br><br>

                Shape ideas from chaos.<br>
                Refine your mod through iterative dialogue.
            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(f"<div class='chat-box'>🧑‍💻 {content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-box' style='border-left:4px solid #88aa55;'>👁️ {content}</div>", unsafe_allow_html=True)


def render_loading():
    texts = [
        "世界正在重构…… / REALITY IS BREAKING...",
        "暗影正在低语…… / SHADOWS ARE WHISPERING...",
        "规则正在崩塌…… / LAWS ARE COLLAPSING...",
    ]

    st.markdown(f"""
    <div style="text-align:center;padding:40px;">
        <div style="
            font-family:Creepster;
            font-size:2rem;
            color:#ffd280;
            animation:flicker 1s infinite alternate;
        ">
        {random.choice(texts)}
        </div>
    </div>

    <style>
    @keyframes flicker {{
        from {{opacity:0.5;}}
        to {{opacity:1;}}
    }}
    </style>
    """, unsafe_allow_html=True)
