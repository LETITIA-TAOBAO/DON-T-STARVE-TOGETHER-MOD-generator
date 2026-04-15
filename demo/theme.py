def inject_theme():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    /* ===== 背景优化（更亮）===== */
    .stApp {
        background:
            linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)),
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

    /* ===== 按钮（荆棘强化）===== */
    div[data-testid="stButton"] > button {
        font-family: 'Creepster', cursive !important;
        font-size: 26px !important;
        font-weight: bold !important;
        letter-spacing: 4px !important;
        padding: 20px !important;
        background: linear-gradient(180deg,#7a4f2a,#2b1a0c) !important;
        color: #ffd280 !important;
        border: 3px solid #c89b5a !important;
        border-radius: 10px !important;
        box-shadow:
            0 0 25px rgba(255,140,0,0.5),
            inset 0 0 20px rgba(0,0,0,0.7);
        position: relative;
    }

    div[data-testid="stButton"] > button:hover {
        transform: scale(1.1);
        box-shadow:
            0 0 40px rgba(255,180,80,0.9),
            inset 0 0 25px rgba(0,0,0,0.8);
    }

    /* ===== 输入框修复白色BUG ===== */
    textarea {
        background-color: rgba(25,20,12,0.95) !important;
        color: #f5e6c8 !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: rgba(25,20,12,0.95) !important;
        color: #f5e6c8 !important;
    }

    /* ===== 模式提示 ===== */
    .mode-box {
        margin-top:20px;
        padding:15px;
        border:2px solid #ffaa60;
        background: rgba(30,20,10,0.8);
        text-align:center;
        font-family:Creepster;
        font-size:1.2rem;
        color:#ffd280;
        animation: glow 1s infinite alternate;
    }

    .mode-box.green {
        border-color:#88cc66;
        color:#aadd88;
    }

    @keyframes glow {
        from {box-shadow:0 0 10px rgba(255,140,0,0.4);}
        to {box-shadow:0 0 25px rgba(255,140,0,0.9);}
    }

    </style>
    """
