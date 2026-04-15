def inject_theme(bg_base64=None):
    # 如果没有图片，提供一个深色底色防止白屏
    bg_image = f'url("data:image/png;base64,{bg_base64}")' if bg_base64 else "none"

    return f"""
    <style>
    /* =========================
       🌑 全局基础风格
    ========================= */
    
    /* 1. 核心修复：直接给主容器设置背景，不再使用 ::before/::after 遮罩 */
    .stApp {{
        background: 
            linear-gradient(rgba(10, 10, 10, 0.8), rgba(5, 5, 5, 0.95)), 
            {bg_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: "Georgia", "Times New Roman", serif;
    }}

    /* 移除所有干扰背景的透明度设置，防止 UI 塌陷 */
    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
    }}

    /* =========================
       🪵 文字与标题风格
    ========================= */
    h1, h2, h3, p, span, label {{
        color: #f5e6c8 !important;
        letter-spacing: 1px;
    }}

    /* =========================
       🎮 按钮风格（饥荒木质感）
    ========================= */
    div[data-testid="stButton"] > button {{
        background: linear-gradient(
            180deg,
            rgba(70, 55, 35, 0.95),
            rgba(40, 30, 20, 0.95)
        ) !important;
        
        color: #f5e6c8 !important;
        border: 1px solid rgba(255, 210, 120, 0.35) !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 
            inset 0 0 10px rgba(0,0,0,0.6), 
            0 4px 10px rgba(0,0,0,0.4) !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05);
        background: linear-gradient(
            180deg,
            rgba(90, 70, 45, 0.98),
            rgba(50, 35, 25, 0.98)
        ) !important;
        box-shadow: 0 0 15px rgba(255, 200, 120, 0.3) !important;
        color: #fff !important;
    }}

    /* =========================
       ⌨️ 输入框（生存笔记本风）
    ========================= */
    /* 覆盖 Streamlit 的所有文本输入组件 */
    div[data-testid="stTextarea"] textarea, 
    div[data-testid="stTextInput"] input {{
        background-color: rgba(25, 20, 15, 0.9) !important;
        color: #f5e6c8 !important;
        border: 1px solid rgba(255, 220, 150, 0.3) !important;
        border-radius: 10px !important;
        box-shadow: inset 0 0 8px rgba(0,0,0,0.8) !important;
    }}

    /* =========================
       💬 聊天气泡风格
    ========================= */
    .stChatMessage {{
        background: rgba(40, 32, 22, 0.7) !important;
        border: 1px solid rgba(255, 220, 150, 0.15) !important;
        backdrop-filter: blur(8px);
        border-radius: 15px !important;
        color: #f5e6c8 !important;
        margin-bottom: 10px !important;
    }}

    /* =========================
       📜 侧边栏（地图风格）
    ========================= */
    section[data-testid="stSidebar"] {{
        background: rgba(15, 12, 10, 0.9) !important;
        border-right: 1px solid rgba(255, 210, 120, 0.2) !important;
    }}

    /* 隐藏 Streamlit 默认的水印和页脚 */
    footer {{
        visibility: hidden;
    }}

    #MainMenu {{
        visibility: hidden;
    }}
    </style>
    """
