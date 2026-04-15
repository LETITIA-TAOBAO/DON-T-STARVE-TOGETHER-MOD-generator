def inject_theme(bg_base64=None):

    return f"""
    <style>

    /* ===== 去除白边 ===== */
    html, body, [class*="css"] {{
        background: transparent !important;
    }}

    .stApp {{
        position: relative;
        overflow: hidden;
        color: #f5e6c8;
    }}

    /* ===== 背景层 ===== */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;

        background:
            linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.9)),
            url("data:image/png;base64,{bg_base64}");

        background-size: cover;
        background-position: center;
        filter: blur(2px);
        z-index: -2;
    }}

    /* ===== 暗角 ===== */
    .stApp::after {{
        content: "";
        position: fixed;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, transparent 40%, rgba(0,0,0,0.85));
        z-index: -1;
    }}

    /* ===== 按钮 ===== */
    button {{
        background: rgba(50,40,25,0.85);
        color: #f5e6c8;
        border: 1px solid rgba(255,220,150,0.3);
        border-radius: 12px;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }}

    button:hover {{
        transform: scale(1.08) rotate(-1deg);
        background: rgba(80,60,40,0.95);
        box-shadow: 0 0 20px rgba(255,200,120,0.4);
    }}

    /* ===== 输入框 ===== */
    textarea, input {{
        background: rgba(30,25,20,0.9) !important;
        color: #f5e6c8 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,220,150,0.2) !important;
    }}

    /* ===== 聊天气泡 ===== */
    .stChatMessage {{
        background: rgba(60,50,35,0.65);
        border: 1px solid rgba(255,220,150,0.15);
        backdrop-filter: blur(6px);
        border-radius: 10px;
        padding: 10px;
    }}

    </style>
    """
