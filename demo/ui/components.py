import streamlit as st


def render_banner():
    st.markdown("""
    <div style="
        background: linear-gradient(180deg,rgba(20,16,10,0.95),rgba(10,8,5,0.98));
        border: 3px solid #a67c3b;
        border-radius: 10px;
        padding: 50px;
        text-align:center;
        max-width:900px;
        margin:auto;
        box-shadow:
            0 0 50px rgba(0,0,0,0.8),
            inset 0 0 40px rgba(0,0,0,0.6);
    ">
        <h1 style="
            font-family:Creepster;
            font-size:3.5rem;
            color:#ffd280;
            letter-spacing:6px;
        ">
        饥荒MOD生成器
        </h1>

        <p style="
            font-family:Creepster;
            color:#aa8855;
            letter-spacing:4px;
        ">
        DON'T STARVE TOGETHER MOD GENERATOR
        </p>

        <hr style="border:1px solid #5a3a1a;width:60%;margin:20px auto;">

        <!-- 核心中二介绍 -->
        <p style="font-family:Griffy;font-size:1.1rem;line-height:1.8;">
        当理智坠入深渊，世界的法则开始破碎。<br>
        你不再只是求生者，而是支配噩梦的造物主。<br>
        在篝火微光之外，编织属于你的疯狂与奇迹。<br><br>

        When sanity collapses, the laws of this world begin to fracture.<br>
        You are no longer a survivor, but a creator who shapes nightmares.<br>
        Beyond the fading firelight, weave your own madness into reality.
        </p>

        <hr style="border:1px solid #5a3a1a;width:40%;margin:25px auto;">

        <!-- 模式说明 -->
        <div style="display:flex;gap:30px;flex-wrap:wrap;justify-content:center;">

            <!-- 快速模式 -->
            <div style="
                flex:1;
                min-width:260px;
                background:rgba(40,30,20,0.7);
                padding:20px;
                border:2px solid #aa7733;
            ">
                <div style="font-family:Creepster;color:#ffaa60;font-size:1.4rem;">
                快速生成
                </div>
                <div style="font-family:Griffy;color:#aa8855;font-size:0.8rem;">
                RAPID GENERATION
                </div>

                <p style="margin-top:10px;">
                当疯狂的构想已然成型，不必犹豫。<br>
                在此刻，将你的意志直接铸造成现实。<br>
                生成完整的MOD，并化为可触及的存在。<br><br>

                When your vision is already clear, hesitate no more.<br>
                Forge your idea directly into reality,<br>
                and summon a complete, playable Mod artifact.
                </p>
            </div>

            <!-- 探索模式 -->
            <div style="
                flex:1;
                min-width:260px;
                background:rgba(25,35,25,0.7);
                padding:20px;
                border:2px solid #668844;
            ">
                <div style="font-family:Creepster;color:#aadd88;font-size:1.4rem;">
                探索设计
                </div>
                <div style="font-family:Griffy;color:#88aa66;font-size:0.8rem;">
                DEEP EXPLORATION
                </div>

                <p style="margin-top:10px;">
                当灵感如迷雾般低语，与未知对话。<br>
                在不断试探中揭示真正的设计。<br>
                直到混沌凝聚，化为清晰的创世蓝图。<br><br>

                When inspiration whispers like fog, explore the unknown.<br>
                Refine your ideas through dialogue and iteration,<br>
                until chaos converges into a clear design.
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
            color:#ffd280;
            animation:flicker 1s infinite alternate;
        ">
        世界正在重构……
        </div>

        <div style="font-family:Griffy;">
        REALITY IS BEING REWRITTEN...
        </div>

        <style>
        @keyframes flicker {
            from {opacity:0.5;}
            to {opacity:1;}
        }
        </style>
    </div>
    """, unsafe_allow_html=True)
