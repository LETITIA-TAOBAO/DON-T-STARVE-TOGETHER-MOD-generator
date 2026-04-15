import streamlit as st
import re
import json
import base64
import os

# =========================
# 🎨 页面配置（必须最前）
# =========================
st.set_page_config(page_title="DST Mod Designer", layout="wide")

# =========================
# 🖼️ 背景图（只做UI，不影响逻辑）
# =========================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# ⚠️ 图片必须放在项目目录（和app.py同级）
IMAGE_PATH = "封面图.png"

bg_base64 = ""
if os.path.exists(IMAGE_PATH):
    bg_base64 = get_base64_image(IMAGE_PATH)

# =========================
# 🎨 UI样式（核心）
# =========================
st.markdown(f"""
<style>

/* 整体背景 */
.stApp {{
    background-color: black;
}}

/* 背景图 */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("data:image/png;base64,{bg_base64}");
    background-size: cover;
    background-position: center;
    opacity: 0.25;
    z-index: -1;
}}

/* 黑色遮罩 */
.stApp::after {{
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: -1;
}}

/* 侧边栏 */
section[data-testid="stSidebar"] {{
    background-color: #0d0d0d !important;
}}

/* 输入框 */
.stTextInput input {{
    background-color: #1a1a1a;
    color: white;
    border: 1px solid #444;
}}

/* 按钮 */
.stButton button {{
    background-color: #2b2b2b;
    color: white;
    border-radius: 6px;
    border: 1px solid #555;
}}

.stButton button:hover {{
    background-color: #444;
}}

/* 内容卡片 */
.block-container {{
    background: rgba(0,0,0,0.6);
    padding: 2rem;
    border-radius: 12px;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# 🔑 LLM（保留你原来的）
# =========================
# ⚠️ 如果你不用OpenAI，这里可以删掉
# from openai import OpenAI
# client = OpenAI(api_key="YOUR_API_KEY")

# =========================
# 🧠 安全调用（保留）
# =========================
def safe_llm_call(messages):
    try:
        # 👉 这里保留你原来的逻辑（或接你自己的qwen）
        return "这里是测试回复（请接入你的LLM）"

    except Exception as e:
        return f"❌ API错误: {str(e)}"


# =========================
# 🧠 JSON解析（保留）
# =========================
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None


def clean_response_for_user(text):
    return re.sub(r"\{.*\}", "", text, flags=re.DOTALL).strip()


# =========================
# 💬 Prompt（保留）
# =========================
SYSTEM_PROMPT = """
你是一个Don't Starve Together Mod设计师。

输出：
- 自然语言交流
- 最后附带JSON
"""

# =========================
# 🖥 UI（基本不动）
# =========================
st.title("🎮 DST Mod Designer")

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# 💬 显示历史（恢复按钮消失问题）
# =========================
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**👤 你：** {msg['content']}")
    else:
        st.markdown(f"**🧠 AI：** {msg['content']}")

# =========================
# 🧠 输入（保持原结构）
# =========================
user_input = st.text_input("👉 输入你的Mod想法：")

if st.button("生成") and user_input:

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in st.session_state.history:
        messages.append(h)

    messages.append({"role": "user", "content": user_input})

    raw_output = safe_llm_call(messages)

    parsed_json = extract_json(raw_output)
    display_text = clean_response_for_user(raw_output)

    # 显示结果
    st.markdown("### 🧠 AI设计师回复")
    st.markdown(display_text)

    with st.expander("⚙️ 查看结构化数据"):
        if parsed_json:
            st.json(parsed_json)
        else:
            st.code(raw_output)

    # 保存历史
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": display_text})
