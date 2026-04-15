def inject_theme(bg_base64=None):

    if bg_base64:
        bg = f'url("data:image/png;base64,{bg_base64}")'
    else:
        bg = "url('https://images.unsplash.com/photo-1526779259212-756e0cf4b0b8')"

    return f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    .stApp {{
        background:
            linear-gradient(rgba(10,8,5,0.15), rgba(5,4,2,0.4)),
            {bg};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', cursive;
    }}

    header, #MainMenu, footer {{
        display: none !important;
    }}

    /* ===== 荆棘按钮 ===== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 26px !important;
        font-weight: bold !important;
        letter-spacing: 4px !important;
        padding: 20px !important;
        background: linear-gradient(180deg,#7a4f2b,#2a1a0c) !important;
        color: #ffd280 !important;
        border: 3px solid #a67c3b !important;
        border-radius: 8px !important;

        box-shadow:
            0 0 25px rgba(255,140,0,0.4),
            inset 0 0 20px rgba(0,0,0,0.7);

        position: relative;
        overflow: hidden;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.1) rotate(-1deg);
        box-shadow: 0 0 50px rgba(255,140,0,0.8);
    }}

    /* ===== 模式提示 ===== */
    .mode-box {{
        margin:20px auto;
        padding:15px;
        text-align:center;
        border:2px solid #a67c3b;
        background:rgba(20,16,10,0.85);
        font-family:Creepster;
        font-size:1.5rem;
        animation:fadeIn 0.5s ease;
    }}

    .mode-box span {{
        font-family:Griffy;
        font-size:0.9rem;
        color:#aa8855;
    }}

    .mode-box.explore {{
        border-color:#88aa66;
    }}

    @keyframes fadeIn {{
        from {{opacity:0; transform:translateY(10px)}}
        to {{opacity:1; transform:translateY(0)}}
    }}

    /* ===== 输入框修复（白色BUG）===== */
    textarea, textarea:focus {{
        background-color: rgba(25,20,12,0.95) !important;
        color: #f5e6c8 !important;
        border: 1px solid #6b4a2a !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background-color: rgba(25,20,12,0.95) !important;
    }}

    /* ===== 聊天框 ===== */
    .chat-box {{
        background: rgba(25,20,12,0.85);
        border-left: 5px solid #88aa55;
        padding: 14px;
        margin: 12px 0;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.7);
    }}

    h1,h2,h3 {{
        font-family: 'Creepster', cursive !important;
        color: #ffd280 !important;
    }}

    </style>
    """
