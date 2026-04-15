import streamlit as st

def render_banner():
    st.markdown("""
    <div style="
        background: rgba(20,16,10,0.95);
        border: 3px solid #a67c3b;
        border-radius: 12px;
        padding: 50px;
        text-align:center;
        max-width:900px;
        margin:auto;
        box-shadow: 0 0 60px rgba(0,0,0,0.9);
    ">

        <h1 style="font-size:3.5rem;">饥荒MOD生成器</h1>

        <p style="letter-spacing:4px;color:#aa8855;">
        DON'T STARVE TOGETHER MOD GENERATOR
        </p>

        <hr style="border:1px solid #5a3a1a;width:60%;margin:20px auto;">

        <p style="line-height:1.8;">
        理智终将崩塌，规则不再稳定。<br>
        在这片破碎的世界中，你不只是幸存者——<br>
        你是编织噩梦的造物主。<br>
        将疯狂具现，将幻想实体化。<br><br>

        Sanity will collapse. Reality will fracture.<br>
        You are no longer surviving — you are creating.<br>
        Shape nightmares. Forge impossible worlds.
        </p>

        <hr style="border:1px solid #5a3a1a;width:40%;margin:25px auto;">

        <div style="display:flex;gap:30px;flex-wrap:wrap;justify-content:center;">

            <div style="flex:1;min-width:260px;">
                <h3>快速生成</h3>
                <p>RAPID GENERATION</p>

                <p>
                已有清晰构想？直接降临现实。<br>
                一键生成完整Mod与下载文件。<br><br>

                Have a clear idea?<br>
                Instantly generate a complete mod package.
                </p>
            </div>

            <div style="flex:1;min-width:260px;">
                <h3>探索设计</h3>
                <p>DEEP EXPLORATION</p>

                <p>
                灵感尚未成形？与暗影对话。<br>
                逐步构建、确认，并最终创造。<br><br>

                No clear idea yet?<br>
                Explore, refine, and evolve your design.
                </p>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat(messages):
    for msg in messages:
        st.markdown(f"<div class='chat-box'>{msg}</div>", unsafe_allow_html=True)


def render_loading():
    st.markdown("""
    <div style="text-align:center;padding:40px;">
        <div style="
            font-family:Creepster;
            font-size:2rem;
            animation:flicker 1s infinite alternate;
        ">
        世界正在扭曲……
        </div>

        <div>
        REALITY IS BREAKING APART...
        </div>

        <style>
        @keyframes flicker {
            from {opacity:0.5;}
            to {opacity:1;}
        }
        </style>
    </div>
    """, unsafe_allow_html=True)
