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
# 🖼️ 读取本地图片（必须放项目目录）
# =========================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

IMAGE_PATH = "封面图.png"  # 👉 把图片放到和 app.py 同一目录
bg_base64 = get_base64_image(IMAGE_PATH)

# =========================
# 🎨 页面配置 + 样式
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

/* 黑色遮罩 */
.stApp::after {{
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.75);
    z-index: -1;
}}

/* 侧边栏 */
section[data-testid="stSidebar"] {{
    background-color: #0d0d0d !important;
}}

/* 输入框 */
.stChatInput input {{
    background-color: #1a1a1a !important;
    color: white !important;
    border: 1px solid #444 !important;
}}

/* 聊天气泡 */
[data-testid="stChatMessage"] {{
    background: rgba(20,20,20,0.7);
    border-radius: 12px;
    padding: 10px;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 Prompt（保持你原逻辑）
# =========================
SYSTEM_PROMPT = """
你是一个Don't Starve Together Mod设计师。

输出要求：
1. 用自然语言和用户交流（像设计师）
2. 结构清晰，有段落
3. 最后附带一个JSON结构

JSON格式如下：
{
  "concept": "...",
  "mechanics": ["...", "..."],
  "code_hint": "..."
}

注意：
- JSON必须在最后
- JSON之外必须是自然语言
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
# 🚀 LLM调用
# =========================
def call_qwen(messages):
    try:
        response = dashscope.Generation.call(
            model="qwen-plus",
            messages=messages,
            result_format="message"
        )

        if response is None:
            return {"text": "❌ 模型无返回", "json": None, "raw": None}

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

# 初始化历史
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# 💬 显示历史（关键修复）
# =========================
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# 🧠 输入
# =========================
user_input = st.chat_input("👉 输入你的Mod想法")

if user_input:

    # 显示用户消息
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 构建 messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in st.session_state.history:
        messages.append(h)

    # 调用AI
    result = call_qwen(messages)

    # 显示AI回复
    with st.chat_message("assistant"):
        st.markdown(result["text"])

        with st.expander("⚙️ 结构化数据（用于生成Mod）"):
            if result["json"]:
                st.json(result["json"])
            else:
                st.error("JSON解析失败")
                st.code(result["raw"])

    # 存储AI回复
    st.session_state.history.append({
        "role": "assistant",
        "content": result["text"]
    })
