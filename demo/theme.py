# theme.py
def inject_theme():
    return """
    <style>
    /* 1. 字体引入 */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Griffy&display=swap');

    /* 2. 全局背景 - 调亮 */
    .stApp {
        background:
            linear-gradient(rgba(10, 8, 5, 0.25), rgba(20, 15, 10, 0.4)), /* 遮罩变淡 */
            url("https://images.unsplash.com/photo-1526779259212-756e0cf4b0b8");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', cursive;
    }

    /* 3. 隐藏 Streamlit 默认元素 */
    header, #MainMenu, footer, .stDecoration {
        display: none !important;
    }
    
    /* 4. 标题样式 - 夸张中二 */
    h1, h2, h3, h4 {
        font-family: 'Creepster', cursive !important;
        color: #ffd280 !important;
        text-shadow: 2px 2px 0px #000, 0 0 15px rgba(255, 160, 50, 0.6);
        margin-top: 0 !important;
        text-align: center;
    }

    /* 5. 按钮样式 - 荆棘与羊皮纸风格 */
    div[data-testid="stButton"] > button {
        font-family: 'Creepster', cursive !important;
        font-size: 22px !important;
        letter-spacing: 2px !important;
        padding: 15px 30px !important;
        color: #ffd280 !important;
        background: linear-gradient(180deg, #5c4023, #2a1a0c) !important;
        border: 2px solid #8b5a2b !important;
        border-radius: 4px !important;
        /* 模拟荆棘/粗糙边缘 */
        box-shadow: 
            inset 0 0 10px #000,
            0 0 0 2px #3e2712,
            0 0 15px rgba(0,0,0,0.8) !important;
        transition: all 0.2s ease;
        text-transform: uppercase;
        white-space: pre-line !important;
    }

    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05);
        background: linear-gradient(180deg, #7a5530, #3e2712) !important;
        box-shadow: 
            inset 0 0 15px #000,
            0 0 0 2px #a67c3b,
            0 0 25px rgba(255, 140, 0, 0.6) !important;
        color: #fff !important;
    }

    /* 6. 聊天输入框 - 修复白底 Bug */
    [data-testid="stChatInput"] {
        background: rgba(15, 12, 8, 0.95) !important;
        border: 2px solid #5a3a1a !important;
        border-radius: 8px !important;
        padding: 10px;
    }
    
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #f5e6c8 !important;
        font-family: 'Griffy', cursive !important;
        font-size: 1.1rem !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #887755 !important;
    }

    /* 7. 滚动条 */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1510;
    }
    ::-webkit-scrollbar-thumb {
        background: #5c4023;
        border: 1px solid #1a1510;
    }
    </style>
    """
