def inject_theme(bg_base64=None):

    return f"""
    <style>

    /* =========================
       🌑 全局背景 & 基础风格
    ========================= */

    html, body, [class*="css"] {{
        background: transparent !important;
        font-family: "Georgia", "Times New Roman", serif;
    }}

    .stApp {{
        position: relative;
        overflow: hidden;
        color: #f5e6c8;
    }}

    /* =========================
       🌲 饥荒风背景层
    ========================= */

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;

        background:
            linear-gradient(
                rgba(10,10,10,0.78),
                rgba(5,5,5,0.92)
            ),
            url("data:image/png;base64,{bg_base64}");

        background-size: cover;
        background-position: center;
        filter: blur(2.5px) contrast(1.1);
        z-index: -2;
    }}

    /* 暗角（更压抑氛围） */
    .stApp::after {{
        content: "";
        position: fixed;
        width: 100%;
        height: 100%;
        background: radial-gradient(
            circle,
            transparent 35%,
            rgba(0,0,0,0.88)
        );
        z-index: -1;
    }}

    /* =========================
       🪵 标题风格（旧书/生存日志）
    ========================= */

    h1, h2, h3 {{
        color: #f5e6c8 !important;
        letter-spacing: 2px;
    }}

    /* =========================
       🎮 🔥 核心修复：Streamlit按钮
       ⚠️ 关键：必须用 data-testid
    ========================= */

    div[data-testid="stButton"] > button {{
        background: linear-gradient(
            180deg,
            rgba(70,55,35,0.95),
            rgba(40,30,20,0.95)
        );

        color: #f5e6c8 !important;

        border: 1px solid rgba(255, 210, 120, 0.35);
        border-radius: 12px;

        padding: 10px 18px;

        font-size: 16px;
        font-weight: 500;

        transition: all 0.2s ease;

        box-shadow:
            inset 0 0 10px rgba(0,0,0,0.6),
            0 4px 10px rgba(0,0,0,0.4);

        cursor: pointer;
    }}

    /* hover：轻微“跳动 + 发光” */
    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.06) rotate(-0.5deg);

        background: linear-gradient(
            180deg,
            rgba(90,70,45,0.98),
            rgba(50,35,25,0.98)
        );

        box-shadow:
            0 0 18px rgba(255,200,120,0.25),
            inset 0 0 12px rgba(0,0,0,0.6);
    }}

    /* active：按下效果 */
    div[data-testid="stButton"] > button:active {{
        transform: scale(0.98);
    }}

    /* =========================
       ⌨️ 输入框（生存笔记本风）
    ========================= */

    textarea, input {{
        background: rgba(25,20,15,0.92) !important;
        color: #f5e6c8 !important;

        border-radius: 10px !important;
        border: 1px solid rgba(255,220,150,0.25) !important;

        padding: 10px !important;

        box-shadow: inset 0 0 8px rgba(0,0,0,0.6);
    }}

    textarea:focus, input:focus {{
        border: 1px solid rgba(255,200,120,0.5) !important;
        outline: none !important;
    }}

    /* =========================
       💬 聊天气泡（旧日志风）
    ========================= */

    .stChatMessage {{
        background: rgba(40,32,22,0.75);
        border: 1px solid rgba(255,220,150,0.12);

        backdrop-filter: blur(6px);

        border-radius: 12px;
        padding: 10px 12px;

        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }}

    /* =========================
       📜 sidebar（地图/笔记风）
    ========================= */

    section[data-testid="stSidebar"] {{
        background: rgba(15,12,10,0.85);
        border-right: 1px solid rgba(255,220,150,0.15);
    }}

    /* =========================
       🔥 隐藏Streamlit默认水印感UI
    ========================= */

    footer {{
        visibility: hidden;
    }}

    </style>
    """
