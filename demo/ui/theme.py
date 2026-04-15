def inject_theme(bg_base64=None):
    if bg_base64:
        bg_image = 'url("data:image/png;base64,' + bg_base64 + '")'
    else:
        bg_image = "none"

    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    .stApp {
        background:
            linear-gradient(rgba(8,6,4,0.82), rgba(3,3,3,0.95)),
            BG_IMAGE_PLACEHOLDER;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', 'Georgia', cursive, serif;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header {
        background-color: transparent !important;
        background: transparent !important;
    }

    [data-testid="stHeader"] {
        height: 0px !important;
        min-height: 0px !important;
        padding: 0 !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    h1 {
        font-family: 'Creepster', cursive !important;
        color: #ffd280 !important;
        letter-spacing: 4px !important;
        text-shadow:
            0 0 10px rgba(255,180,60,0.3),
            0 0 40px rgba(255,120,0,0.15),
            3px 3px 6px rgba(0,0,0,0.8) !important;
        font-size: 2.8rem !important;
    }

    h2 {
        font-family: 'Creepster', cursive !important;
        color: #e8c888 !important;
        letter-spacing: 3px !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.7) !important;
        font-size: 1.8rem !important;
    }

    h3 {
        font-family: 'Griffy', cursive !important;
        color: #d4b878 !important;
        letter-spacing: 2px !important;
    }

    p, span, label, li {
        color: #d4c4a0 !important;
        font-family: 'Griffy', 'Georgia', cursive !important;
        font-size: 1.05rem !important;
    }

    div[data-testid="stButton"] > button {
        background: linear-gradient(
            180deg,
            rgba(75,58,38,0.95),
            rgba(35,25,15,0.98)
        ) !important;
        color: #ffd280 !important;
        border: 2px solid rgba(255,190,90,0.3) !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-family: 'Creepster', cursive !important;
        font-size: 18px !important;
        letter-spacing: 2px !important;
        transition: all 0.25s ease !important;
        box-shadow:
            inset 0 0 15px rgba(0,0,0,0.7),
            0 4px 15px rgba(0,0,0,0.5),
            0 0 8px rgba(255,160,60,0.08) !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6) !important;
    }

    div[data-testid="stButton"] > button:hover {
        transform: scale(1.06) rotate(-0.8deg) !important;
        background: linear-gradient(
            180deg,
            rgba(100,78,48,0.98),
            rgba(50,35,22,0.98)
        ) !important;
        border-color: rgba(255,200,100,0.5) !important;
        color: #ffe8b0 !important;
        box-shadow:
            0 0 25px rgba(255,180,80,0.2),
            inset 0 0 15px rgba(0,0,0,0.5),
            0 6px 20px rgba(0,0,0,0.6) !important;
    }

    div[data-testid="stButton"] > button:active {
        transform: scale(0.97) rotate(0.3deg) !important;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background-color: rgba(20,16,10,0.92) !important;
        color: #f5e6c8 !important;
        border: 1px solid rgba(255,200,120,0.25) !important;
        border-radius: 8px !important;
        font-family: 'Griffy', cursive !important;
        font-size: 1rem !important;
        box-shadow: inset 0 0 12px rgba(0,0,0,0.8) !important;
        padding: 12px !important;
    }

    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255,180,80,0.5) !important;
        box-shadow:
            inset 0 0 12px rgba(0,0,0,0.8),
            0 0 10px rgba(255,180,80,0.15) !important;
        outline: none !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(200,180,140,0.4) !important;
    }

    .stChatMessage {
        background: rgba(35,28,18,0.8) !important;
        border: 1px solid rgba(255,200,120,0.12) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5) !important;
    }

    .stChatMessage p {
        color: #e0d0b0 !important;
        font-family: 'Griffy', cursive !important;
    }

    [data-testid="stChatInput"] {
        background-color: rgba(15,12,8,0.9) !important;
        border-top: 1px solid rgba(255,200,120,0.15) !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: rgba(25,20,12,0.95) !important;
        color: #f5e6c8 !important;
        font-family: 'Griffy', cursive !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(12,10,6,0.92) !important;
        border-right: 1px solid rgba(255,200,120,0.12) !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #c8b888 !important;
    }

    [data-testid="stAlert"] {
        background: rgba(30,25,15,0.85) !important;
        border: 1px solid rgba(255,200,120,0.2) !important;
        border-radius: 8px !important;
        color: #e0d0a0 !important;
    }

    code, pre {
        background: rgba(20,16,10,0.9) !important;
        color: #c8e888 !important;
        border: 1px solid rgba(255,200,120,0.1) !important;
        border-radius: 6px !important;
    }

    footer {
        visibility: hidden !important;
    }

    #MainMenu {
        visibility: hidden !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(10,8,5,0.8);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(180,140,80,0.4);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(200,160,90,0.6);
    }
    </style>
    """

    css = css.replace("BG_IMAGE_PLACEHOLDER", bg_image)
    return css
