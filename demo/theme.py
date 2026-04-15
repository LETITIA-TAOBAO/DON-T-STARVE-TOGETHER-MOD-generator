def inject_theme(bg_base64=None):
    """注入全局主题 - 无语法错误的干净版本"""
    
    if bg_base64:
        bg_url = f'data:image/png;base64,{bg_base64}'
    else:
        bg_url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
    
    return '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
    }
    
    .stApp {
        background-image: 
            linear-gradient(rgba(10,6,3,0.8), rgba(5,4,2,0.9)),
            url(''' + bg_url + ''');
        background-size: cover !important;
        background-position: center !important;
        color: var(--text-primary) !important;
        font-family: 'IM Fell English SC', serif !important;
    }
    
    header, footer, #MainMenu { display: none !important; }
    
    [data-testid="stAppViewContainer"] {
        background-color: transparent !important;
    }
    
    section[data-testid="stSidebar"] {
        background: rgba(25,15,8,0.95) !important;
        border-right: 2px solid var(--border-gold) !important;
    }
    
    div[data-testid="stButton"] > button {
        font-family: 'Creepster' !important;
        color: var(--highlight-gold) !important;
        background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
        border: 2px solid var(--thorn-brown) !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background-color: rgba(20,15,10,0.95) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-gold) !important;
    }
    
    ::-webkit-scrollbar { width: 8px !important; }
    ::-webkit-scrollbar-thumb { background: rgba(166,124,59,0.4) !important; }
    </style>
    '''
