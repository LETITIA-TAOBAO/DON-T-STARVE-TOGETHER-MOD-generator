def inject_theme(bg_base64=None):
    """注入全局主题 - 放在最前面"""
    
    if bg_base64:
        bg_img = f'data:image/png;base64,{bg_base64}'
    else:
        bg_img = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
    
    return f'''
    <style>
    /* ========== 字体导入 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    /* ========== 全局变量 ========== */
    :root {{
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --dark-bg: rgba(15, 10, 5, 0.9);
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
        --orange-glow: #ffaa60;
        --green-glow: #66aa66;
    }}
    
    /* ========== 关键：强制透明背景 ========== */
    .stApp {{
        background: 
            linear-gradient(rgba(10, 6, 3, 0.8), rgba(5, 4, 2, 0.9)),
            url('{bg_img}');
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        position: relative !important;
    }}
    
    /* 隐藏 Streamlit 默认元素 */
    header, footer, #MainMenu, [data-testid="stHeader"] {{
        display: none !important;
    }}
    
    /* 关键：容器透明 */
    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        padding: 0 !important;
    }}
    
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {{
        background: rgba(25, 15, 8, 0.95) !important;
        border-right: 2px solid var(--border-gold) !important;
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    
    /* ========== 按钮荆棘风格 ========== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 18px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        padding: 18px 12px !important;
        background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
        color: var(--highlight-gold) !important;
        border: 3px solid var(--thorn-brown) !important;
        border-radius: 0 !important;
        box-shadow: 0 0 15px rgba(255, 170, 96, 0.3), inset 0 0 20px rgba(0,0,0,0.7) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }}
    
    div[data-testid="stButton"] > button::before {{
        content: "✦";
        position: absolute;
        top: 5px; left: 10px;
        color: var(--thorn-brown);
        font-size: 20px;
    }}
    
    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 0 25px rgba(255, 170, 96, 0.5) !important;
        color: #FFF !important;
    }}
    
    /* ========== 聊天框深色背景 ========== */
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(20, 15, 10, 0.95) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-gold) !important;
        border-radius: 8px !important;
        font-family: 'IM Fell English SC', serif !important;
        padding: 12px !important;
        min-height: 70px !important;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5) !important;
    }}
    
    [data-testid="stChatInput"] textarea:focus {{
        outline: none !important;
        border-color: var(--highlight-gold) !important;
    }}
    
    /* 滚动条 */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-track {{ background: rgba(10, 6, 3, 0.8) !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166, 124, 59, 0.4) !important; border-radius: 4px !important; }}
    </style>
    '''
