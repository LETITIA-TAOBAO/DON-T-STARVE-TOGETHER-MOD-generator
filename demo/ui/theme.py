def inject_theme(bg_base64=None):

    bg_style = ""

    if bg_base64:
        bg_style = f"""
        background:
            linear-gradient(rgba(10,10,10,0.85), rgba(10,10,10,0.95)),
            url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        """

    else:
        bg_style = "background-color: #111;"


    return f"""
    <style>

    .stApp {{
        {bg_style}
        animation: bgBreath 12s ease-in-out infinite;
    }}

    @keyframes bgBreath {{
        0% {{ background-size: 100%; }}
        50% {{ background-size: 105%; }}
        100% {{ background-size: 100%; }}
    }}

    h1, h2, h3 {{
        color: #f2e6c9;
        text-shadow: 0 0 10px rgba(255,200,120,0.4);
    }}

    button {{
        background: linear-gradient(145deg, #3a2f25, #1e1812);
        color: #f5e6c8;
        border-radius: 10px;
        transition: all 0.2s;
    }}

    button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(255,200,120,0.5);
    }}

    </style>
    """
