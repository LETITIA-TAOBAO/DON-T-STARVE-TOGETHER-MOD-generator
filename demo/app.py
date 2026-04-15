import streamlit as st
import re
import json

# 👇 引入你刚刚写的 Qwen模块
from qwen_client import design_with_llm

st.set_page_config(page_title="DST Mod Designer", layout="wide")

# =========================
# 🧠 工具函数：提取JSON（保留）
# =========================
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group(0))
    except:
        return None


# =========================
# 🧠 工具函数：清理展示文本（保留）
# =========================
def clean_response_for_user(text):
    return re.sub(r"\{.*\}", "", text, flags=re.DOTALL).strip()


# =========================
# 🖥 UI
# =========================
st.title("🎮 DST Mod Designer（稳定版）")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("👉 输入你的Mod想法：")

if st.button("生成") and user_input:

    # =========================
    # 🚀 调用你封装好的Qwen
    # =========================
    result = design_with_llm(user_input)

    # result结构：
    # {
    #   "text": "...",
    #   "json": {...},
    #   "raw": "..."
    # }

    display_text = result["text"]
    parsed_json = result["json"]
    raw_output = result["raw"]

    # =========================
    # 💬 显示对话（正常）
    # =========================
    st.markdown("### 🧠 AI设计师回复")
    st.markdown(display_text)

    # =========================
    # 🧩 JSON（隐藏）
    # =========================
    with st.expander("⚙️ 查看结构化数据（用于生成Mod）"):
        if parsed_json:
            st.json(parsed_json)
        else:
            st.error("❌ JSON解析失败")
            st.code(raw_output)

    # =========================
    # 🧠 保存历史（用于后续扩展）
    # =========================
    st.session_state.history.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.history.append({
        "role": "assistant",
        "content": display_text
    })
