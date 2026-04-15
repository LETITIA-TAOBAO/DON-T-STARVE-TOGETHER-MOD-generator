# theme.py
def inject_theme(bg_base64=None):
    # 如果没有提供 base64，则使用一个默认的深色背景
    bg_image = f'url("data:image/png;base64,{bg_base64}")' if bg_base64 else "none"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Griffy&display=swap');

    .stApp {{
        background: 
            linear-gradient(rgba(10, 8, 5, 0.3), rgba(20, 15, 10, 0.5)), 
            {bg_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', cursive;
    }}

    header, #MainMenu, footer, .stDecoration {{
        display: none !important;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Creepster', cursive !important;
        color: #ffd280 !important;
        text-shadow: 2px 2px 0px #000, 0 0 15px rgba(255, 160, 50, 0.6);
        text-align: center;
    }}

    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        color: #ffd280 !important;
        background: linear-gradient(180deg, #5c4023, #2a1a0c) !important;
        border: 3px solid #8b5a2b !important;
        border-radius: 4px !important;
        box-shadow: 
            inset 0 0 10px #000,
            0 0 0 2px #3e2712,
            0 0 15px rgba(0,0,0,0.8) !important;
        transition: all 0.2s ease;
        white-space: pre-line !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05);
        border-color: #a67c3b !important;
        box-shadow: 0 0 25px rgba(255, 140, 0, 0.6) !important;
    }}

    [data-testid="stChatInput"] {{
        background: rgba(15, 12, 8, 0.95) !important;
        border: 2px solid #5a3a1a !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: #f5e6c8 !important;
        font-family: 'Griffy', cursive !important;
    }}
    </style>
    """
