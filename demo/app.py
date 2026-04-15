import streamlit as st
import re
import json
from openai import OpenAI

# =========================
# 🔑 初始化
# =========================
client = OpenAI(api_key="YOUR_API_KEY")

st.set_page_config(page_title="DST Mod Designer", layout="wide")

# =========================
# 🧠 工具函数：安全调用LLM
# =========================
def safe_llm_call(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-5-3",
            messages=messages,
        )

        if response is None:
            return "❌ API返回为空"

        if not hasattr(response, "choices") or len(response.choices) == 0:
            return "❌ API结构异常"

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ API错误: {str(e)}"


# =========================
# 🧠 工具函数：提取JSON
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
# 🧠 工具函数：清理展示文本（去JSON）
# =========================
def clean_response_for_user(text):
    # 去掉JSON部分
    cleaned = re.sub(r"\{.*\}", "", text, flags=re.DOTALL)
    return cleaned.strip()


# =========================
# 💬 Prompt（关键）
# =========================
SYSTEM_PROMPT = """
你是一个Don't Starve Together Mod设计师。

输出要求：
1. 用自然语言和用户交流（像设计师）
2. 结构清晰，有段落
3. 最后附带一个JSON结构，用于程序解析

JSON格式如下（必须在最后）：
{
  "concept": "...",
  "mechanics": ["...", "..."],
  "code_hint": "简单描述代码方向"
}

注意：
- JSON必须是最后一部分
- JSON之外必须是自然语言
"""


# =========================
# 🖥 UI
# =========================
st.title("🎮 DST Mod Designer（稳定版）")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("👉 输入你的Mod想法：")

if st.button("生成") and user_input:

    # 构建messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in st.session_state.history:
        messages.append(h)

    messages.append({"role": "user", "content": user_input})

    # 调用LLM
    raw_output = safe_llm_call(messages)

    # 提取JSON
    parsed_json = extract_json(raw_output)

    # 清理展示内容
    display_text = clean_response_for_user(raw_output)

    # =========================
    # 💬 显示对话
    # =========================
    st.markdown("### 🧠 AI设计师回复")
    st.markdown(display_text)

    # =========================
    # 🧩 JSON结果（隐藏/调试）
    # =========================
    with st.expander("⚙️ 查看结构化数据（用于生成Mod）"):
        if parsed_json:
            st.json(parsed_json)
        else:
            st.error("❌ JSON解析失败")
            st.code(raw_output)

    # 存入历史
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": raw_output})
