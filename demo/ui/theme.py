def inject_theme():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    /* ===== 全局背景（更清晰） ===== */
    .stApp {
        background:
            linear-gradient(rgba(10,8,5,0.25), rgba(5,4,2,0.5)),
            url("https://images.unsplash.com/photo-1526779259212-756e0cf4b0b8");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', cursive;
    }

    header, #MainMenu, footer {
        display: none !important;
    }

    /* ===== 按钮（DST风） ===== */
    div[data-testid="stButton"] button {
        font-family: 'Creepster', cursive !important;
        font-size: 24px !important;
        letter-spacing: 3px !important;
        padding: 18px !important;

        background: linear-gradient(180deg,#6b4423,#2a1a0c) !important;
        color: #ffd280 !important;

        border: 3px solid #a67c3b !important;
        border-radius: 6px !important;

        box-shadow:
            0 0 20px rgba(255,140,0,0.4),
            inset 0 0 20px rgba(0,0,0,0.6);

        transition: all 0.25s ease;
    }

    div[data-testid="stButton"] button:hover {
        transform: scale(1.08);
        box-shadow:
            0 0 40px rgba(255,140,0,0.8),
            inset 0 0 20px rgba(0,0,0,0.6);
    }

    /* ===== 选中态 ===== */
    .mode-active button {
        border: 3px solid #88ffcc !important;
        box-shadow:
            0 0 30px #88ffcc,
            inset 0 0 20px rgba(0,0,0,0.6) !important;
    }

    /* ===== 输入框修复 ===== */
    textarea {
        background-color: rgba(20,16,10,0.9) !important;
        color: #f5e6c8 !important;
        border: 1px solid #6b4a2a !important;
    }

    /* ===== 聊天框 ===== */
    .chat-box {
        background: rgba(25,20,12,0.85);
        border-left: 4px solid #88aa55;
        padding: 12px;
        margin: 10px 0;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
    }

    </style>
    """
