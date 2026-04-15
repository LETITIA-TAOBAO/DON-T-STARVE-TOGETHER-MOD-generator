def inject_theme(bg_base64=None):
    """注入全局主题 - 带背景图支持"""
    
    if bg_base64:
        bg_url = f'data:image/png;base64,{bg_base64}'
    else:
        # 备用网络图片
        bg_url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
    
    return f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {{
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
    }}
    
    /* ========== 关键：全局透明 ========== */
    html, body, [class*="css"], .stApp, .st-emotion-cache {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    .stApp {{
        position: relative !important;
        min-height: 100vh;
    }}
    
    /* 背景图层 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -2 !important;
        background: 
            linear-gradient(rgba(10,6,3,0.65), rgba(5,3,1,0.85)),
            url('{bg_url}') center/cover no-repeat;
        filter: contrast(1.08) brightness(0.88);
    }}
    
    /* 纹理叠加 */
    .stApp::after {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.06'/%3E%3C/svg%3E");
        pointer-events: none;
    }}
    
    /* ========== 隐藏 Streamlit 元素 ========== */
    header, footer, #MainMenu, [data-testid="stHeader"], [data-testid="stDecoration"] {{
        display: none !important;
    }}
    
    /* ========== 关键：容器透明化 ========== */
    [data-testid="stAppViewContainer"],
    [data-testid="stBlockContainer"],
    [data-testid="verticalContainer"],
    .st-emotion-cache-16idsys {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    /* ========== 关键：对话框无白底 ========== */
    [data-testid="stChatInput"].stSticky {{
        background-color: transparent !important;
        border: none !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    
    [data-testid="stChatInput"] > div {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(25,20,15,0.95) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-gold) !important;
        border-radius: 0 !important;
        font-family: 'IM Fell English SC', serif !important;
        font-size: 16px !important;
        padding: 15px !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
    }}
    
    [data-testid="stChatInput"] textarea:focus {{
        outline: none !important;
        border-color: var(--highlight-gold) !important;
    }}
    
    /* ========== 侧边栏 ========== */
    section[data-testid="stSidebar"] {{
        background: rgba(25,15,8,0.98) !important;
        border-right: 3px solid var(--border-gold) !important;
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    
    /* ========== 按钮风格 ========== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 18px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        line-height: 1.4 !important;
        padding: 20px 15px !important;
        background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
        color: var(--highlight-gold) !important;
        border: 3px solid var(--thorn-brown) !important;
        border-radius: 0 !important;
        box-shadow: 0 0 15px rgba(255,170,96,0.3), inset 0 0 20px rgba(0,0,0,0.7) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }}
    
    div[data-testid="stButton"] > button:before {{
        content: "✦ ";
        position: absolute;
        top: 3px; left: 5px; right: 5px;
        color: rgba(139, 69, 19, 0.4);
        font-size: 16px;
        text-align: center;
        pointer-events: none;
    }}
    
    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 0 25px rgba(255,170,96,0.5), inset 0 0 20px rgba(0,0,0,0.8) !important;
        color: #FFF !important;
        border-color: var(--highlight-gold) !important;
    }}
    
    /* ========== 标题与文本 ========== */
    h1, h2, h3 {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3) !important;
    }}
    
    h1 {{ letter-spacing: 4px !important; }}
    
    p, span, label {{
        font-family: 'IM Fell English SC', serif !important;
        color: var(--text-primary) !important;
    }}
    
    .subtitle {{ font-family: 'Griffy', cursive !important; }}
    
    /* ========== 信息卡片 ========== */
    .info-card {{
        background: rgba(30,20,10,0.75) !important;
        border: 2px solid var(--thorn-brown) !important;
        padding: 25px !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.7), inset 0 0 15px rgba(0,0,0,0.5) !important;
        position: relative !important;
        border-radius: 0 !important;
    }}
    
    .info-card::before {{
        content: "✷";
        position: absolute;
        top: -12px; right: -12px;
        font-size: 28px;
        color: var(--thorn-brown);
        transform: rotate(45deg);
    }}
    
    /* ========== 聊天消息框 ========== */
    .chat-box {{
        background: rgba(25,20,15,0.9) !important;
        border-left: 4px solid var(--highlight-gold) !important;
        border: 1px solid rgba(166,124,59,0.3) !important;
        padding: 15px 20px !important;
        margin: 15px 0 !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
    }}
    
    /* ========== 动画 ========== */
    @keyframes flicker {{
        0% {{ opacity: 0.7; text-shadow: 0 0 10px rgba(255,215,0,0.5); }}
        50% {{ opacity: 1; text-shadow: 0 0 20px rgba(255,215,0,0.9); }}
        100% {{ opacity: 0.8; text-shadow: 0 0 15px rgba(255,215,0,0.7); }}
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03); }}
        100% {{ transform: scale(1); }}
    }}
    
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    .loading-text {{ animation: flicker 1.5s infinite alternate; }}
    .mode-confirm {{ animation: pulse 1.5s infinite; }}
    
    /* ========== 滚动条 ========== */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-track {{ background: rgba(10,6,3,0.8) !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166,124,59,0.5) !important; border-radius: 4px !important; }}
    </style>
    '''
