# 🎨 终极深色背景修复版

根据你描述的问题（对话框周围是白色 + 背景图不显示），这是 **Streamlit 默认容器白底** 的问题。下面是完整修复方案：

---

## ✅ app.py (强制全黑背景版)

```python
import streamlit as st
import os
import base64
from datetime import datetime
import time
import urllib.request

# ========================
# ⚠️ LLM 安全导入 + 降级模式
# ========================
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"⚠️ LLM模块加载失败，使用降级模式")
    
    def mock_explore(messages):
        return {
            "text": f"👁️ **暗影回应了你的召唤**...\n\n关于 '{messages[-1]['content'][:30]}...' 的想法很有趣！",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f"✅ **Mod 已生成！**\n名称：Mod_{datetime.now().strftime('%H%M')}",
            "data": {"name": f"Mod_{datetime.now().strftime('%Y%m%d_%H%M')}", "desc": idea}
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore


# ========================
# 🎨 核心 CSS - 强制全黑背景
# ========================
def get_theme_css(bg_url):
    """生成带背景图的CSS - 超强力版"""
    return f'''
    <style>
    /* ========== 全局变量 ========== */
    :root {{
        --bg-image: url('{bg_url}') center/cover no-repeat;
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
        --black-bg: rgba(0, 0, 0, 1);
    }}
    
    /* ========== 1. 最外层强制透明 ========== */
    html, body {{
        background-color: var(--black-bg) !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* ========== 2. 超强力覆盖所有 Streamlit 容器 ========== */
    .stApp, 
    [class*="css"], 
    .st-emotion-cache-*,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stColumn"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stScrollArea"],
    .stMarkdown,
    .stHtml,
    .stMarkdown > div,
    section.st-section,
    div.st-column,
    div.block-container,
    .st-emotion-cache-vxkz7u,
    .st-emotion-cache-q423b9,
    .st-emotion-cache-1cxfkq8 {{
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        color: var(--text-primary) !important;
    }}
    
    /* ========== 3. 背景图层 - 确保在最底层 ========== */
    body::before,
    .stApp::before {{
        content: "" !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: -1000 !important;
        background: 
            linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)),
            var(--bg-image) !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        filter: contrast(1.05) brightness(0.85) !important;
    }}
    
    /* ========== 4. 额外备用遮罩层 ========== */
    body::after {{
        content: "" !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: -999 !important;
        background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.95) 100%) !important;
        pointer-events: none !important;
    }}
    
    /* ========== 5. 隐藏所有Streamlit默认元素 ========== */
    header, footer, #MainMenu, [data-testid="stHeader"], [data-testid="stDecoration"],
    [data-testid="stToolbar"], [data-testid="stSidebarClose"] {{
        display: none !important;
    }}
    
    /* ========== 6. 文本和标题样式 ========== */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3) !important;
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    p, span, label, li, div, td, th, a, small, em {{
        font-family: 'IM Fell English SC', serif !important;
        color: var(--text-primary) !important;
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    .subtitle {{
        font-family: 'Griffy', cursive !important;
    }}
    
    /* ========== 7. 输入框深色背景 ========== */
    [data-testid="stChatInput"].stSticky {{
        background-color: transparent !important;
        border: none !important;
        margin-bottom: 0 !important;
        box-shadow: none !important;
        padding-bottom: 0 !important;
    }}
    
    [data-testid="stChatInput"] > div {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(20, 15, 10, 0.98) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-gold) !important;
        border-radius: 0 !important;
        font-family: 'IM Fell English SC', serif !important;
        padding: 15px !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
        caret-color: var(--highlight-gold) !important;
    }}
    
    /* ========== 8. 按钮风格 ========== */
    div[data-testid="stButton"] > button {{
        font-family: 'Creepster', cursive !important;
        color: var(--highlight-gold) !important;
        background: linear-gradient(180deg, #3a2e1d, #1a120b) !important;
        border: 3px solid var(--thorn-brown) !important;
        border-radius: 0 !important;
        box-shadow: 0 0 15px rgba(255,170,96,0.3), inset 0 0 20px rgba(0,0,0,0.7) !important;
    }}
    
    /* ========== 9. 信息卡片 ========== */
    .info-card {{
        background: rgba(30,20,10,0.85) !important;
        border: 2px solid var(--thorn-brown) !important;
        padding: 25px !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.8), inset 0 0 15px rgba(0,0,0,0.6) !important;
        border-radius: 0 !important;
        color: var(--text-primary) !important;
    }}
    
    /* ========== 10. 聊天消息框 ========== */
    .chat-box {{
        background: rgba(25,20,15,0.92) !important;
        border-left: 4px solid var(--highlight-gold) !important;
        padding: 15px 20px !important;
        margin: 15px 0 !important;
        color: var(--text-primary) !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6) !important;
    }}
    
    /* ========== 11. 动画 ========== */
    @keyframes flicker {{
        0% {{ opacity: 0.7; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.8; }}
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03); }}
        100% {{ transform: scale(1); }}
    }}
    
    .loading-text {{ animation: flicker 1.5s infinite alternate; }}
    .mode-confirm {{ animation: pulse 1.5s infinite; }}
    
    /* ========== 12. 滚动条 ========== */
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.8) !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166,124,59,0.5) !important; border-radius: 4px !important; }}
    </style>
    '''


# ========================
# 🔧 Session State
# ========================
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False


# ========================
# 🖼️ 背景图处理
# ========================
def get_background_base64():
    try:
        bg_path = os.path.join(os.path.dirname(__file__), "封面图.png")
        if os.path.exists(bg_path):
            with open(bg_path, "rb") as f:
                bg64 = base64.b64encode(f.read()).decode()
                print(f"✅ 背景图加载成功：{bg_path}")
                return bg64
        
        # 备用网络图片
        print("⚠️ 本地背景图未找到，使用网络备用图")
        url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
        with urllib.request.urlopen(url) as response:
            return base64.b64encode(response.read()).decode()
    except Exception as e:
        print(f"❌ 背景图加载失败：{e}")
        # 纯色黑色背景备用
        return None


bg_base64 = get_background_base64()
bg_url = f'data:image/png;base64,{bg_base64}' if bg_base64 else '#000000'


# ========================
# 🎨 注入主题 (最最前面执行！)
# ========================
print("=== 启动 App ===")
print(f"背景图 URL: {bg_url[:50]}..." if len(bg_url) > 50 else f"背景图 URL: {bg_url}")

theme_css = get_theme_css(bg_url)
st.markdown(theme_css, unsafe_allow_html=True)


# ========================
# 📄 Banner HTML
# ========================
banner_html = '''
<div style="position:relative;z-index:5;text-align:center;margin:20px auto;max-width:950px;padding:50px;">
    <h1 style="font-family:'Creepster';font-size:3.8rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.5rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.8;font-size:1.15rem;max-width:850px;margin:0 auto 35px;background:transparent!important;">
    当理智的 san 值归零，现实的法则在此崩塌。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    你不再是苟延残喘的求生者，而是编织噩梦的造物主。<br>
    <span style="color:#88aa66;text-shadow:0 0 10px rgba(136,170,102,0.5);">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:30px auto;opacity:0.7;">
    
    <div style="display:flex;gap:25px;flex-wrap:wrap;justify-content:center;margin-top:30px;">
        <div class="info-card" style="flex:1;min-width:300px;background:rgba(30,20,10,0.85)!important;border:2px solid #aa7733;padding:25px;">
            <div style="font-family:'Creepster';color:#ffaa60;font-size:1.7rem;text-align:center;margin-bottom:15px;">🔥 快速生成 / RAPID</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">适用于意志坚定的造物主。当你已明确 Mod 的核心机制与物品属性，无需犹豫，直接将构想铸造成可下载的文件。<br><span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when your vision is clear. Forge it now.</span></p>
        </div>
        
        <div class="info-card" style="flex:1;min-width:300px;background:rgba(20,30,20,0.85)!important;border:2px solid #668844;padding:25px;">
            <div style="font-family:'Creepster';color:#aadd88;font-size:1.7rem;text-align:center;margin-bottom:15px;">👁️ 探索设计 / EXPLORE</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">适用于在迷雾中低语的探索者。当灵感混沌不清，与暗影对话以理清思路，在反复试探中让疯狂的蓝图逐渐清晰。<br><span style="color:#888;font-size:0.8em;display:block;margin-top:12px;font-style:italic;">For when inspiration is foggy. Talk to the Shadow.</span></p>
        </div>
    </div>
</div>
'''

st.markdown(banner_html, unsafe_allow_html=True)


# ========================
# 🔘 模式选择按钮
# ========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("**🔥 快速生成**\\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

# 模式确认
if st.session_state.mode != "home":
    mode_config = {
        "rapid": ("⚡", "#FFD700", "**快速生成模式已激活**"),
        "explore": ("👁️", "#4CAF50", "**探索设计模式已激活**"),
        "generating": ("⚙️", "#FF8C00", "**正在重构现实...**"),
        "generated": ("✅", "#66aa66", "**Mod 已完成**")
    }
    icon, color, text = mode_config.get(st.session_state.mode, ("❓", "#888", "**未知模式**"))
    st.markdown(f'<div class="mode-confirm" style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.5)!important;border:2px dashed {color};"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>', unsafe_allow_html=True)


# ========================
# 💬 聊天输入处理
# ========================
if st.session_state.mode == "explore":
    st.info("💬 **与暗影对话以明确设计思路**")
    user_input = st.chat_input("描述你的想法...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

elif st.session_state.mode == "rapid":
    user_input = st.chat_input("输入你的完整 Mod 构想...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()


# ========================
# ⏳ 生成响应阶段
# ========================
if st.session_state.is_generating:
    loading_html = '''<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 class="loading-text" style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);">世界正在扭曲......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">暗影正在编织你的疯狂......<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
    </div>'''
    st.markdown(loading_html, unsafe_allow_html=True)
    
    time.sleep(2.5)
    
    try:
        if st.session_state.mode == "explore":
            result = explore_with_llm(st.session_state.messages)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        st.session_state.messages.append({"role": "assistant", "content": result.get('text', '暗影已回应...')})
        
        mod_data = result.get('data', {})
        if mod_data and st.session_state.mode == "rapid":
            st.session_state.generated_mods.append({
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', '新 Mod'),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ 生成失败：{str(e)}"})
    
    st.session_state.is_generating = False
    st.rerun()


# ========================
# 💬 显示聊天历史
# ========================
if st.session_state.messages:
    for msg in st.session_state.messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = '🧙‍♂️ 求生者 / SURVIVOR' if role == 'user' else '👁️ 暗影 / SHADOW'
            chat_html = f'<div class="chat-box" style="border-left-color:{color}!important;"><b style="font-family:Creepster;color:{color};font-size:1.2rem;">{name}</b><br><span style="font-size:1.1rem;line-height:1.7;">{content}</span></div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box">{msg}</div>', unsafe_allow_html=True)


# ========================
# 📦 侧边栏
# ========================
with st.sidebar:
    st.markdown("### 📦 Mod 库")
    
    if not st.session_state.generated_mods:
        st.markdown('<div style="background:rgba(0,0,0,0.5)!important;border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Created Yet<br>暂无 Mod</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h4 style='font-family:Griffy;color:#AA7733;'>📜 创作记录 / CREATIONS</h4>", unsafe_allow_html=True)
        for mod in st.session_state.generated_mods:
            st.markdown(f'<div style="background:rgba(30,20,10,0.7)!important;border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="font-family:Creepster;color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>', unsafe_allow_html=True)
    
    st.divider()
    st.write(f"💬 对话：{len(st.session_state.messages)} 条")
    
    if st.session_state.generated_mods:
        st.markdown("---")
        mod = st.session_state.generated_mods[-1]
        st.markdown(f'<div style="background:rgba(30,20,10,0.8)!important;border:2px solid #FFD700;padding:15px;"><h4 style="font-family:Creepster;color:#FFD700;margin-top:0;">⬇️ 下载 Mod</h4><p style="color:#aaa;font-size:0.9rem;margin-bottom:15px;">{mod.get("desc", "")}</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 下载", key=f"download_{mod['id']}", use_container_width=True):
                st.success(f"{mod['name']} 已开始下载!")
        with col2:
            if st.button("🔄 重新生成", key=f"regen_{mod['id']}", use_container_width=True):
                st.info("正在重新生成该 Mod...")
    
    st.divider()
    if st.button("🗑️ 清除记录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
```

---

## 🎯 关键修复点

| 修复项 | CSS 规则 | 说明 |
|--------|---------|------|
| **全黑背景** | `--black-bg: rgba(0,0,0,1)` | 纯黑作为备用 |
| **双层遮罩** | `body::before` + `body::after` | 确保背景图在最底层 |
| **超强力覆盖** | 10+个选择器加`!important` | 优先于所有默认样式 |
| **z-index** | `-1000` 到 `-999` | 背景在最底 |
| **Console 日志** | 打印背景图 URL | 方便调试 |

---

## ✅ 部署步骤

### 1. GitHub上传
```bash
git add app.py
git commit -m "Fix white background issue - force black"
git push
```

### 2. Streamlit Cloud查看控制台日志
应该看到：
```
=== 启动 App ===
✅ 背景图加载成功：...
或
⚠️ 本地背景图未找到，使用网络备用图
```

### 3. 如果还有白色区域
在浏览器按 F12 → Console 输入：
```javascript
document.body.style.backgroundColor = 'black';
```

现在刷新页面，整个界面应该都是纯黑/深色背景了！如果还有问题请告诉我具体位置～
