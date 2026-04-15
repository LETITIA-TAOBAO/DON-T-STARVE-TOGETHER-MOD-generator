def inject_theme(bg_base64=None):
    """注入全局主题样式"""
    if bg_base64:
        bg_image = f'url("data:image/png;base64,{bg_base64}")'
    else:
        bg_image = 'url("https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80")'
    
    return f"""
    <style>
    /* 字体导入 */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {{
        --thorn-color: #8B4513;
        --highlight: #FFD700;
        --text-primary: #F5E6C8;
        --border-color: #A67C3B;
    }}
    
    /* 关键修复：确保背景覆盖全屏 */
    .stApp {{
        background: linear-gradient(rgba(10, 6, 3, 0.85), rgba(8, 4, 2, 0.95)), {bg_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--text-primary);
        font-family: 'IM Fell English SC', serif !important;
        position: relative;
        overflow-x: hidden;
    }}
    
    /* 背景纹理叠加 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px);
        pointer-events: none; z-index: 0;
    }}
    
    /* 隐藏默认元素 */
    header, #MainMenu, footer, [data-testid="stHeader"] {{
        display: none !important;
    }}
    
    /* 关键修复：容器透明 */
    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        padding-top: 20px !important;
        position: relative; z-index: 1;
    }}
    
    [data-testid="stBlockWrapper"] {{
        background-color: transparent !important;
        position: relative; z-index: 1;
    }}
    
    /* 关键修复：对话框深色背景 */
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(25, 20, 15, 0.95) !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
        font-size: 16px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 15px !important;
        min-height: 80px !important;
    }}
    
    [data-testid="stChatInput"] textarea:focus {{
        outline: none !important;
        border-color: #FFD700 !important;
    }}
    
    /* 关键修复：侧边栏样式 */
    section[data-testid="stSidebar"] {{
        background: rgba(30, 20, 10, 0.98) !important;
        border-right: 3px solid var(--border-color) !important;
        backdrop-filter: blur(10px);
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {{
        color: var(--text-primary) !important;
    }}
    
    section[data-testid="stSidebar"] button {{
        background: rgba(40, 30, 20, 0.8) !important;
        color: #FFD700 !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* 按钮样式 */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        font-size: 20px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        line-height: 1.3 !important;
        padding: 20px 15px !important;
        background: linear-gradient(180deg, #3A2E1D, #1A120B) !important;
        color: #FFD700 !important;
        border: 3px solid var(--border-color) !important;
        border-radius: 0 !important;
        box-shadow: 0 0 15px rgba(255, 170, 96, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.7) !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        min-height: 80px !important;
    }}
    
    div[data-testid="stButton"] > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 0 30px rgba(255, 170, 96, 0.5) !important;
        color: #FFF !important;
        border-color: #FFD700 !important;
    }}
    
    /* 滚动条 */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-track {{ background: rgba(10, 6, 3, 0.8) !important; }}
    ::-webkit-scrollbar-thumb {{
        background: rgba(166, 124, 59, 0.4) !important;
        border-radius: 4px !important;
    }}
    </style>
    """
