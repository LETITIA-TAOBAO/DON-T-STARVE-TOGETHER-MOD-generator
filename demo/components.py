# components.py
import streamlit as st

def render_banner():
    st.markdown("""
    <div style="
        background: linear-gradient(180deg, rgba(30,25,20,0.95), rgba(15,12,8,0.98));
        border: 4px double #8b5a2b;
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        max-width: 1000px;
        margin: 20px auto;
        box-shadow: 0 0 50px rgba(0,0,0,0.9), inset 0 0 60px rgba(0,0,0,0.8);
        position: relative;
        overflow: hidden;
    ">
        <!-- 装饰性角落 -->
        <div style="position:absolute;top:0;left:0;width:100%;height:5px;background:linear-gradient(90deg, #5a3a1a, #a67c3b, #5a3a1a);"></div>
        <div style="position:absolute;bottom:0;left:0;width:100%;height:5px;background:linear-gradient(90deg, #5a3a1a, #a67c3b, #5a3a1a);"></div>

        <h1 style="
            font-size: 4rem;
            margin: 0;
            color: #ffaa60;
            text-shadow: 0 0 20px rgba(255, 100, 0, 0.8);
        ">
        饥荒 MOD 生成器
        </h1>

        <p style="
            font-family: 'Griffy', cursive;
            color: #aa8855;
            font-size: 1.5rem;
            letter-spacing: 3px;
            margin-top: 5px;
            text-transform: uppercase;
        ">
        DON'T STARVE TOGETHER MOD GENERATOR
        </p>

        <hr style="border:0; border-top:1px solid #5a3a1a; width: 50%; margin: 20px auto; opacity: 0.6;">

        <!-- 中二介绍文案 -->
        <p style="
            font-family: 'Griffy', cursive;
            font-size: 1.1rem;
            line-height: 1.6;
            color: #d4c4a0;
            max-width: 800px;
            margin: 0 auto 30px auto;
            text-shadow: 1px 1px 2px #000;
        ">
        当理智的san值归零，现实的法则在此崩塌。<br>
        <span style="color:#88aa66">You are no longer a survivor, but a Creator of Nightmares.</span><br>
        你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
        在永恒领域的边缘，用代码重塑你的疯狂。<br>
        <span style="color:#88aa66">Weave your madness into the Constant.</span>
        </p>

        <!-- 模式说明卡片 -->
        <div style="display:flex; gap:20px; flex-wrap:wrap; justify-content:center;">
            
            <!-- 快速生成说明 -->
            <div style="
                flex: 1; min-width: 300px;
                background: rgba(40, 30, 20, 0.6);
                border: 2px solid #aa7733;
                padding: 15px;
                border-radius: 8px;
            ">
                <div style="font-family:'Creepster'; color:#ffaa60; font-size:1.6rem;">
                快速生成 / RAPID
                </div>
                <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.9rem; margin-top:10px;">
                适用于意志坚定的造物主。<br>
                当你已明确 Mod 的核心机制与物品属性，<br>
                无需犹豫，直接将构想铸造成可下载的文件。<br>
                <span style="color:#888; font-size:0.8em">For when your vision is clear. Forge it now.</span>
                </p>
            </div>

            <!-- 探索设计说明 -->
            <div style="
                flex: 1; min-width: 300px;
                background: rgba(25, 35, 25, 0.6);
                border: 2px solid #668844;
                padding: 15px;
                border-radius: 8px;
            ">
                <div style="font-family:'Creepster'; color:#aadd88; font-size:1.6rem;">
                探索设计 / EXPLORE
                </div>
                <p style="font-family:'Griffy'; color:#d4c4a0; font-size:0.9rem; margin-top:10px;">
                适用于在迷雾中低语的探索者。<br>
                当灵感混沌不清，与暗影对话以理清思路。<br>
                在反复试探中，让疯狂的蓝图逐渐清晰。<br>
                <span style="color:#888; font-size:0.8em">For when inspiration is foggy. Talk to the Shadow.</span>
                </p>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat(messages):
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                # 求生者样式
                st.markdown(f"""
                <div style="
                    background: rgba(30, 25, 20, 0.8);
                    border-left: 5px solid #aa7733;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 0 8px 8px 0;
                    color: #f5e6c8;
                    font-family: 'Griffy', cursive;
                    font-size: 1.1rem;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
                ">
                    <div style="font-family:'Creepster'; color:#aa7733; font-size:1.2rem; margin-bottom:5px;">
                    🧑‍🌾 求生者 / SURVIVOR
                    </div>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                # 暗影样式
                st.markdown(f"""
                <div style="
                    background: rgba(20, 30, 20, 0.8);
                    border-right: 5px solid #668844;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 8px 0 0 8px;
                    color: #d4f5d4;
                    font-family: 'Griffy', cursive;
                    font-size: 1.1rem;
                    box-shadow: -2px 2px 10px rgba(0,0,0,0.5);
                    text-align: right;
                ">
                    <div style="font-family:'Creepster'; color:#668844; font-size:1.2rem; margin-bottom:5px;">
                    👁️ 暗影 / SHADOW
                    </div>
                    {content}
                </div>
                """, unsafe_allow_html=True)
        else:
            # 兼容旧格式
            st.markdown(f"<div style='padding:10px; color:#aaa;'>{msg}</div>", unsafe_allow_html=True)

def render_loading():
    st.markdown("""
    <div style="text-align:center; padding: 60px 0;">
        <div style="
            font-family: 'Creepster', cursive;
            font-size: 3rem;
            color: #ff4444;
            animation: flicker 0.1s infinite alternate;
            text-shadow: 0 0 10px #ff0000;
        ">
        世界正在重构……
        </div>
        <div style="font-family:'Griffy'; color:#aa8855; font-size:1.5rem; margin-top:10px;">
        REALITY IS BEING REWRITTEN...
        </div>
        
        <style>
        @keyframes flicker {
            0% { opacity: 0.8; transform: scale(1); }
            100% { opacity: 1; transform: scale(1.02); }
        }
        </style>
    </div>
    """, unsafe_allow_html=True)
