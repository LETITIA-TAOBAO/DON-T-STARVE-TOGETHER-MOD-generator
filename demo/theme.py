def inject_theme(bg_base64=None):
    if bg_base64:
        bg_image = f'url("data:image/png;base64,{bg_base64}")'
    else:
        bg_image = 'url("https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80")'
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

    :root {{
        --thorn-color: #8B4513;
        --dark-bg: rgba(15, 10, 5, 0.85);
        --light-bg: rgba(25, 20, 10, 0.80);
        --highlight: #FFD700;
        --text-primary: #F5E6C8;
        --text-secondary: #D4C4A0;
        --border-color: #A67C3B;
    }}

    .stApp {{
        background:
            linear-gradient(rgba(10, 6, 3, 0.75), rgba(8, 4, 2, 0.95)),
            {bg_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--text-primary);
        font-family: 'IM Fell English SC', serif !important;
    }}

    /* 背景纹理叠加 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px);
        pointer-events: none; z-index: 0;
    }}

    /* 隐藏 Streamlit 默认元素 */
    header, #MainMenu, footer, [data-testid="stHeader"] {{
        display: none !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        padding-top: 20px !important;
        position: relative; z-index: 1;
    }}

    /* ===== ⚠️ 关键修复：对话框强制深色背景 ===== */
    [data-testid="stChatInput"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 20px !important;
    }}

    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(25, 20, 15, 0.95) !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        font-size: 16px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 15px !important;
        min-height: 80px !important;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6) !important;
    }}

    [data-testid="stChatInput"] textarea:focus {{
        outline: none !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3) !important;
    }}

    /* ===== 按钮荆棘效果 ===== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 20px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        line-height: 1.3 !important;
        padding: 20px 15px !important;
        background: linear-gradient(180deg, #3A2E1D, #1A120B) !important;
        color: var(--highlight) !important;
        border: 3px solid var(--border-color) !important;
        border-radius: 0 !important;
        box-shadow: 0 0 15px rgba(255, 170, 96, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.7) !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        min-height: 80px !important;
    }}

    div[data-testid="stButton"] > button:before {{
        content: "✦  ";
        position: absolute;
        top: 5px; left: 5px; right: 5px;
        color: rgba(139, 69, 19, 0.5);
        font-size: 18px; letter-spacing: 10px;
        pointer-events: none; z-index: -1;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 0 30px rgba(255, 170, 96, 0.5) !important;
        color: #FFF !important;
        border-color: #FFD700 !important;
    }}

    /* ===== 容器荆棘框 ===== */
    .thorn-container {{
        background: rgba(20, 15, 10, 0.75) !important;
        border: 3px solid var(--border-color) !important;
        padding: 30px !important;
        margin: 20px auto !important;
        max-width: 1000px !important;
        box-shadow: 0 0 50px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(0, 0, 0, 0.6) !important;
        position: relative !important;
    }}

    .thorn-container::before,
    .thorn-container::after {{
        content: "";
        position: absolute;
        width: 80px; height: 80px;
        border: 2px solid var(--thorn-color);
    }}

    .thorn-container::before {{
        top: 10px; left: 10px;
        border-right: none; border-bottom: none;
        border-radius: 8px 0 0 0;
    }}

    .thorn-container::after {{
        bottom: 10px; right: 10px;
        border-left: none; border-top: none;
        border-radius: 0 0 8px 0;
    }}

    /* ===== 标题和文本 ===== */
    h1, h2, h3 {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight) !important;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 215, 0, 0.3) !important;
    }}

    h1 {{ font-size: 3.5rem !important; letter-spacing: 4px !important; }}
    p, span, label {{
        font-family: 'IM Fell English SC', serif !important;
        color: var(--text-secondary) !important;
    }}

    /* ===== 聊天消息框 ===== */
    .chat-box {{
        background: rgba(25, 20, 15, 0.9) !important;
        border-left: 4px solid var(--highlight) !important;
        padding: 15px 20px !important;
        margin: 15px 0 !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6) !important;
        max-width: 95% !important;
    }}

    .chat-box.user {{ border-left-color: #FF8C00 !important; }}
    .chat-box.assistant {{ border-left-color: #4CAF50 !important; }}

    /* ===== 加载文字 ===== */
    .loading-text {{
        font-family: 'Creepster', cursive !important;
        font-size: 2.5rem !important;
        color: var(--highlight) !important;
        text-align: center !important;
        margin: 40px 0 !important;
        animation: flicker 1.5s infinite alternate !important;
    }}

    @keyframes flicker {{
        0% {{ opacity: 0.7; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.8; }}
    }}

    /* ===== 模式确认 ===== */
    .mode-confirmation {{
        font-family: 'Creepster', cursive !important;
        font-size: 2rem !important;
        text-align: center !important;
        margin: 20px 0 !important;
        animation: pulse 1.5s infinite !important;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}

    /* ===== 侧边栏 ===== */
    section[data-testid="stSidebar"] {{
        background: rgba(15, 10, 5, 0.95) !important;
        border-right: 2px solid var(--border-color) !important;
    }}

    section[data-testid="stSidebar"] * {{ color: var(--text-secondary) !important; }}

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-track {{ background: rgba(10, 6, 3, 0.8) !important; }}
    ::-webkit-scrollbar-thumb {{
        background: rgba(166, 124, 59, 0.4) !important;
        border-radius: 4px !important;
    }}

    /* ===== 信息卡片 ===== */
    .info-card {{
        background: rgba(30, 20, 10, 0.7) !important;
        border: 2px solid var(--thorn-color) !important;
        padding: 20px !important;
        border-radius: 6px !important;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(0, 0, 0, 0.5) !important;
    }}

    .info-card-title {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight) !important;
        font-size: 1.3rem !important;
        margin-bottom: 10px !important;
    }}
    </style>
    """
