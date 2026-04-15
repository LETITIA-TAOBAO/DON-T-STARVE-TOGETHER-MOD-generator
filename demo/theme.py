import os
from pathlib import Path

def inject_theme():
    """注入全局主题 - 修复白框 + 饥荒风格"""
    
    # GitHub 环境检测
    is_github = 'GITHUB_ACTIONS' in os.environ
    
    return '''
    <style>
    /* ========== 字体导入 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Rye&display=swap');
    
    /* ========== 饥荒配色 ========== */
    :root {
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --orange-glow: #ffaa60;
        --green-glow: #66aa66;
        --dark-wood: #2a1a0c;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
        --overlay-black: rgba(5, 3, 1, 0.95);
    }
    
    /* ========== 关键：全局透明背景 ========== */
    html, body, [class*="css"], .stApp, .st-emotion-cache-ky0p7d, .st-emotion-cache-1uvv7i1 {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    .stApp {
        position: relative !important;
        min-height: 100vh;
    }
    
    /* 背景图片层 */
    .background-layer::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -2 !important;
        background: 
            linear-gradient(rgba(10,6,3,0.7), rgba(5,3,1,0.9)),
            url('/api/static/background_image') center/cover no-repeat;
        filter: contrast(1.1) brightness(0.9);
    }
    
    /* 纹理叠加层 */
    .background-layer::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1 !important;
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23A67C3B' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
        opacity: 0.5;
        pointer-events: none;
    }
    
    /* ========== 隐藏 Streamlit 默认元素 ========== */
    header, footer, #MainMenu, [data-testid="stHeader"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* ========== 关键：所有容器透明 ========== */
    [data-testid="stAppViewContainer"],
    [data-testid="stBlockContainer"],
    [data-testid="stVerticalBlock"],
    .st-emotion-cache-16idsys {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* 聊天输入框周围的白色容器 */
    [data-testid="stChatInput"].stSticky {
        background-color: transparent !important;
    }
    
    [data-testid="stChatInput"] div[data-testid="stWidgetLabel"] {
        background-color: transparent !important;
    }
    
    [data-testid="stChatInput"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* ========== 侧边栏饥荒风格 ========== */
    section[data-testid="stSidebar"] {
        background: var(--overlay-black) !important;
        border-right: 2px solid var(--border-gold) !important;
        backdrop-filter: blur(10px);
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    /* ========== 按钮荆棘风格 ========== */
    div[data-testid="stButton"] > button {
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
        box-shadow: 
            0 0 15px rgba(255,170,96,0.3),
            inset 0 0 20px rgba(0,0,0,0.7),
            0 4px 15px rgba(0,0,0,0.6) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    div[data-testid="stButton"] > button:before {
        content: "✦ ✦";
        position: absolute;
        top: 3px; left: 5px; right: 5px;
        color: rgba(139, 69, 19, 0.4);
        font-size: 16px;
        letter-spacing: 8px;
        text-align: center;
        pointer-events: none;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 
            0 0 25px rgba(255,170,96,0.5),
            inset 0 0 20px rgba(0,0,0,0.8),
            0 6px 20px rgba(0,0,0,0.7) !important;
        color: #FFF !important;
        border-color: var(--highlight-gold) !important;
    }
    
    div[data-testid="stButton"] > button:active {
        transform: scale(0.98) !important;
    }
    
    /* ========== 聊天框深色背景 ========== */
    [data-testid="stChatInput"] textarea {
        background-color: rgba(25,20,15,0.95) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-gold) !important;
        border-radius: 0 !important;
        font-family: 'IM Fell English SC', serif !important;
        font-size: 16px !important;
        padding: 15px !important;
        min-height: 80px !important;
        box-shadow: 
            inset 0 0 15px rgba(0,0,0,0.6),
            0 0 10px rgba(0,0,0,0.5) !important;
    }
    
    [data-testid="stChatInput"] textarea:focus {
        outline: none !important;
        border-color: var(--highlight-gold) !important;
        box-shadow: 0 0 20px rgba(255,215,0,0.3) !important;
    }
    
    /* ========== 信息卡片饥荒风格 ========== */
    .info-card {
        background: rgba(30,20,10,0.75) !important;
        border: 2px solid var(--thorn-brown) !important;
        border-radius: 0 !important;
        padding: 20px !important;
        box-shadow: 
            0 0 20px rgba(0,0,0,0.7),
            inset 0 0 15px rgba(0,0,0,0.5) !important;
        position: relative !important;
    }
    
    .info-card::before {
        content: "✷";
        position: absolute;
        top: -10px; right: -10px;
        font-size: 24px;
        color: var(--thorn-brown);
        transform: rotate(45deg);
    }
    
    /* ========== 标题饥荒风格 ========== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3) !important;
    }
    
    h1 {
        letter-spacing: 4px !important;
    }
    
    p, span, label {
        font-family: 'IM Fell English SC', serif !important;
        color: var(--text-primary) !important;
    }
    
    .subtitle {
        font-family: 'Griffy', cursive !important;
    }
    
    /* ========== 滚动条饥荒风格 ========== */
    ::-webkit-scrollbar {
        width: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10,6,3,0.8) !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(166,124,59,0.5) !important;
        border-radius: 4px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(166,124,59,0.8) !important;
    }
    
    /* ========== 警告信息饥荒风格 ========== */
    [data-testid="stInfo"] {
        background: rgba(30,20,10,0.8) !important;
        border: 2px solid var(--border-gold) !important;
        color: var(--text-primary) !important;
        border-radius: 0 !important;
    }
    
    [data-testid="stInfo"] p {
        color: var(--text-primary) !important;
    }
    
    /* ========== 加载动画 ========== */
    @keyframes flicker {
        0% { opacity: 0.7; text-shadow: 0 0 10px rgba(255,215,0,0.5); }
        50% { opacity: 1; text-shadow: 0 0 20px rgba(255,215,0,0.9); }
        100% { opacity: 0.8; text-shadow: 0 0 15px rgba(255,215,0,0.7); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    
    .loading-text {
        animation: flicker 1.5s infinite alternate;
    }
    
    .mode-confirm {
        animation: pulse 1.5s infinite;
    }
    </style>
    '''
