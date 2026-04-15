def inject_theme(bg_base64=None):
    bg_image = f'url("data:image/png;base64,{bg_base64}")' if bg_base64 else "none"

    return f"""
    <style>
    /* =========================
       🔤 引入饥荒风格字体（手写/歪扭感）
    ========================= */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');

    /* =========================
       🌑 全局基础
    ========================= */
    .stApp {{
        background:
            linear-gradient(rgba(8, 6, 4, 0.82), rgba(3, 3, 3, 0.95)),
            {bg_image};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5e6c8;
        font-family: 'Griffy', 'Georgia', cursive, serif;
    }}

    /* 去掉所有容器默认白色背景 */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* 顶部白条彻底消失 */
    [data-testid="stHeader"] {{
        height: 0px !important;
        min-height: 0px !important;
        padding: 0 !important;
    }}

    /* =========================
       🪵 标题（饥荒歪扭手写风）
    ========================= */
    h1 {{
        font-family: 'Creepster', cursive !important;
        color: #ffd280 !important;
        letter-spacing: 4px !important;
        text-shadow:
            0 0 10px rgba(255, 180, 60, 0.3),
            0 0 40px rgba(255, 120, 0, 0.15),
            3px 3px 6px rgba(0, 0, 0, 0.8) !important;
        font-size: 2.8rem !important;
    }}

    h2 {{
        font-family: 'Creepster', cursive !important;
        color: #e8c888 !important;
        letter-spacing: 3px !important;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.7) !important;
        font-size: 1.8rem !important;
    }}

    h3 {{
        font-family: 'Griffy', cursive !important;
        color: #d4b878 !important;
        letter-spacing: 2px !important;
    }}

    p, span, label, li {{
        color: #d4c4a0 !important;
        font-family: 'Griffy', 'Georgia', cursive !important;
        font-size: 1.05rem !important;
    }}

    /* =========================
       🎮 按钮（饥荒木板/皮革感）
    ========================= */
    div[data-testid="stButton"] > button {{
        background: linear-gradient(
            180deg,
            rgba(75, 58, 38, 0.95),
            rgba(35, 25, 15, 0.98)
        ) !important;

        color: #ffd280 !important;

        border: 2px solid rgba(255, 190, 90, 0.3) !important;
        border-radius: 8px !important;

        padding: 12px 24px !important;

        font-family: 'Creepster', cursive !important;
        font-size: 18px !important;
        letter-spacing: 2px !important;

        transition: all 0.25s ease !important;

        box-shadow:
            inset 0 0 15px rgba(0,0,0,0.7),
            0 4px 15px rgba(0,0,0,0.5),
            0 
