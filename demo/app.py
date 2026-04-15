import streamlit as st
import dashscope
import os
import json
import re
import base64

# =========================
# 🔐 API KEY
# =========================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# =========================
# 🖼️ 背景图处理（关键！）
# =========================
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ⚠️ 本地路径（你自己的）
IMAGE_PATH = "封面图.png"  # 👉 建议把图片放到项目目录！

bg_base64 = ""
if os.path.exists(IMAGE_PATH):
    bg_base64 = get_base64_image(IMAGE_PATH)

# =========================
# 🎨 页面样式（核心UI优化）
# =========================
st.set_page_config(page_title="DST Mod Designer", layout="wide")

st.markdown(f"""
<style>

/* 整体背景 */
.stApp {{
    background: black;
}}

/* 背景图片 */
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

/* 遮罩 */
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
    border-radius: 8px;
    border: 1px solid #555;
}}

.stButton button:hover {{
    background-color: #444;
}}

/* 卡片 */
.block-container {{
    background: rgba(0,0,0,0.6);
    padding: 2rem;
    border-radius: 16px;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 Prompt（保留你原逻辑）
# =========================
SYSTEM_PROMPT = """
你是一个Don't Starve Together Mod设计师。

用自然语言和用户交流。

最后附带JSON：
{
  "concept": "...",
  "mechanics": ["...", "..."],
  "code_hint": "..."
}
"""

# =========================
# 🧠 工具函数
# =========================
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None

def clean_text(text):
    return re.sub(r"\{.*\}", "", text, flags=re.DOTALL).strip()

# =========================
# 🚀 LLM调用（直接内置，不再import）
# =========================
def call_qwen(messages):
    try:
        response = dashscope.Generation.call(
            model="qwen-plus",
            messages=messages,
            result_format="message"
        )

        content = response.output.choices[0].message.content

        return {
            "text": clean_text(content),
            "json": extract_json(content),
            "raw": content
        }

    except Exception as e:
        return {
            "text": f"❌ API错误: {str(e)}",
            "json": None,
            "raw": None
        }

# =========================
# 🖥 UI
# =========================
st.title("🔥 Don't Starve Together · Mod Designer")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("👉 输入你的Mod想法：")

if st.button("生成") and user_input:

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in st.session_state.history:
        messages.append(h)

    messages.append({"role": "user", "content": user_input})

    result = call_qwen(messages)

    # 显示
    st.markdown("### 🧠 AI设计师")
    st.markdown(result["text"])

    # JSON
    with st.expander("⚙️ 结构化数据"):
        if result["json"]:
            st.json(result["json"])
        else:
            st.error("JSON解析失败")
            st.code(result["raw"])

    # 存历史
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": result["text"]})
