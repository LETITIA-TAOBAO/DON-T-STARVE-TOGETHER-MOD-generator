# ui/theme.py

THEME = {
    "bg": "#0f0f0f",
    "panel": "#1a1a1a",
    "panel_light": "#222222",
    "text": "#e6e6e6",
    "sub_text": "#aaaaaa",
    "border": "#333333",
    "accent": "#7c6cff",
    "accent2": "#4fd1c5",
}


def inject_theme():
    return f"""
    <style>
    html, body {{
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    .stApp {{
        background-color: {THEME["bg"]};
    }}

    h1, h2, h3 {{
        color: {THEME["text"]};
    }}

    /* 输入框 */
    input, textarea {{
        background-color: {THEME["panel"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border"]} !important;
    }}

    /* 按钮 */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME["accent"]}, {THEME["accent2"]});
        color: white;
        border-radius: 10px;
        border: none;
        padding: 8px 16px;
    }}

    .stButton > button:hover {{
        transform: scale(1.02);
        transition: 0.2s;
    }}

    /* 卡片 */
    .card {{
        background: {THEME["panel"]};
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }}

    /* 代码块 */
    code {{
        background-color: {THEME["panel_light"]} !important;
    }}
    </style>
    """