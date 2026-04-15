def inject_theme(bg_base64=None):
    if bg_base64:
        bg_image = 'url("data:image/png;base64,' + bg_base64 + '")'
    else:
        bg_image = "none"

    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    .stApp {
        background:
            linear-gradient(rgba(15, 12, 8, 0.35), rgba(8, 6, 4, 0.55)),
            BG_IMAGE_PLACEHOLDER;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', 'Georgia', cursive, serif;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header {
        background-color: transparent !important;
        background: transparent !important;
    }

    [data-testid="stHeader"] {
        height: 0px !important;
        min-height: 0px !important;
        padding: 0 !important;
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    .main h1:first-of-type {
        display: none !important;
    }

    /* =========================
       🎭 双语标题样式
    ========================= */
    h2 {
        font-family: 'Creepster', cursive !important;
        color: #e8c888 !important;
        letter-spacing: 3px !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.7) !important;
        font-size: 1.8rem !important;
        margin-bottom: 4px !important;
    }

    h3 {
        font-family: 'Griffy', cursive !important;
        color: #d4b878 !important;
        letter-spacing: 2px !important;
    }

    p, span, label, li {
        color: #d4c4a0 !important;
        font-family: 'Griffy', 'Georgia', cursive !important;
        font-size: 1.05rem !important;
    }

    /* =========================
       🎮 双语按钮（中文大，英文小）
    ========================= */
    div[data-testid="stButton"] > button {
        background: linear-gradient(
            180deg,
            rgba(60, 45, 30, 0.95),
            rgba(30, 20, 10, 0.98)
        ) !important;
        color: #ffd280 !important;
        border: 2px solid rgba(120, 80, 40, 0.8) !important;
        border-radius: 4px !important;
        padding: 16px 24px !important;
        font-family: 'Creepster', cursive !important;
        font-size: 20px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        text-shadow: 
            0 0 10px rgba(255, 100, 0, 0.5),
            2px 2px 4px rgba(0,0,0,0.8) !important;
        box-shadow:
            inset 0 0 20px rgba(0,0,0,0.6),
            0 0 15px rgba(80, 120, 40, 0.3),
            0 6px 0 rgba(20, 15, 8, 0.9),
            0 8px 10px rgba(0,0,0,0.5) !important;
        position: relative !important;
        overflow: visible !important;
        transform: skew(-2deg);
        transition: all 0.3s ease !important;
        line-height: 1.4 !important;
    }

    div[data-testid="stButton"] > button:hover {
        transform: skew(-2deg) scale(1.05) !important;
        background: linear-gradient(
            180deg,
            rgba(90, 65, 40, 0.98),
            rgba(45, 30, 18, 0.98)
        ) !important;
        border-color: rgba(255, 150, 50, 0.8) !important;
        color: #ffeebb !important;
        box-shadow:
            0 0 30px rgba(255, 150, 0, 0.4),
            0 0 60px rgba(100, 255, 100, 0.1),
            inset 0 0 20px rgba(0,0,0,0.5),
            0 6px 0 rgba(40, 30, 15, 0.9) !important;
        letter-spacing: 3px !important;
    }

    div[data-testid="stButton"] > button:active {
        transform: skew(-2deg) scale(0.98) translateY(4px) !important;
        box-shadow:
            0 0 20px rgba(255, 150, 0, 0.3),
            inset 0 0 30px rgba(0,0,0,0.8) !important;
    }

    /* 按钮内英文副标题样式 */
    .btn-subtitle {
        display: block;
        font-size: 11px !important;
        color: rgba(200, 180, 140, 0.7) !important;
        letter-spacing: 1px !important;
        font-weight: normal !important;
        margin-top: 2px !important;
        text-transform: uppercase !important;
    }

    /* =========================
       🗡️ 输入框双语样式
    ========================= */
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input,
    [data-testid="stChatInput"] textarea {
        background-color: rgba(20, 16, 10, 0.85) !important;
        color: #f5e6c8 !important;
        border: 1px solid rgba(100, 80, 40, 0.6) !important;
        border-left: 3px solid rgba(80, 120, 40, 0.5) !important;
        border-right: 3px solid rgba(80, 120, 40, 0.5) !important;
        border-radius: 2px !important;
        font-family: 'Griffy', cursive !important;
        font-size: 1rem !important;
        box-shadow: 
            inset 0 0 15px rgba(0,0,0,0.7),
            0 0 10px rgba(40, 60, 20, 0.2) !important;
        padding: 14px !important;
        line-height: 1.6 !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(160, 140, 100, 0.5) !important;
        font-style: italic !important;
    }

    /* =========================
       💬 聊天气泡
    ========================= */
    .stChatMessage {
        background: rgba(25, 20, 12, 0.8) !important;
        border: 1px solid rgba(100, 80, 40, 0.25) !important;
        border-left: 4px solid rgba(80, 120, 40, 0.4) !important;
        backdrop-filter: blur(10px);
        border-radius: 4px !important;
        margin-bottom: 15px !important;
        box-shadow: 
            inset 0 0 20px rgba(0,0,0,0.5),
            0 4px 15px rgba(0,0,0,0.3),
            0 0 8px rgba(40, 60, 20, 0.1) !important;
        position: relative !important;
    }

    .stChatMessage::before {
        content: "" !important;
        position: absolute !important;
        top: 0 !important;
        left: 10% !important;
        right: 10% !important;
        height: 2px !important;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(100, 140, 60, 0.3),
            rgba(150, 100, 50, 0.3),
            transparent
        ) !important;
    }

    .stChatMessage p {
        color: #e0d0b0 !important;
        font-family: 'Griffy', cursive !important;
    }

    [data-testid="stChatInput"] {
        background-color: rgba(20, 16, 10, 0.9) !important;
        border: 2px solid rgba(100, 80, 40, 0.4) !important;
        border-radius: 4px !important;
        padding: 10px !important;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6) !important;
    }

    [data-testid="stChatInput"] > div {
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] button {
        background-color: rgba(60, 45, 30, 0.9) !important;
        border: 1px solid rgba(255, 180, 80, 0.3) !important;
        color: #ffd280 !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(12, 10, 6, 0.9) !important;
        border-right: 2px solid rgba(80, 60, 30, 0.3) !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #c8b888 !important;
    }

    [data-testid="stAlert"] {
        background: rgba(30, 25, 15, 0.85) !important;
        border: 1px solid rgba(100, 80, 40, 0.3) !important;
        border-radius: 4px !important;
        color: #e0d0a0 !important;
    }

    footer, #MainMenu {
        visibility: hidden !important;
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(10, 8, 5, 0.8);
        border: 1px solid rgba(60, 50, 30, 0.3);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(100, 80, 40, 0.6);
        border-radius: 2px;
        border: 1px solid rgba(60, 80, 40, 0.3);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(140, 110, 60, 0.8);
    }

    /* =========================
       ⏳ 加载动画样式
    ========================= */
    .dont-starve-loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background: rgba(10, 8, 5, 0.9);
        border: 2px solid rgba(100, 80, 40, 0.4);
        border-radius: 8px;
        box-shadow: 
            0 0 30px rgba(0,0,0,0.8),
            inset 0 0 20px rgba(255, 150, 50, 0.05);
    }

    .loading-zh {
        font-family: 'Creepster', cursive;
        color: #ffd280;
        font-size: 1.6rem;
        letter-spacing: 4px;
        text-shadow: 0 0 20px rgba(255, 150, 0, 0.5);
        margin-bottom: 4px;
    }

    .loading-en {
        font-family: 'Griffy', cursive;
        color: rgba(200, 180, 140, 0.7);
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* =========================
       🎯 模式指示器双语
    ========================= */
    .mode-indicator-zh {
        font-family: 'Creepster', cursive;
        color: #ffd280;
        font-size: 1.4rem;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(255, 150, 0, 0.4);
    }

    .mode-indicator-en {
        font-family: 'Griffy', cursive;
        color: rgba(200, 180, 140, 0.6);
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    </style>
    """
    
    css = css.replace("BG_IMAGE_PLACEHOLDER", bg_image)
    return css
