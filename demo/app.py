import streamlit as st
import os
import base64
from datetime import datetime
import time
import urllib.request
import io
import zipfile

# LLM Import
try:
    from qwen_client import design_with_llm, explore_with_llm
except Exception as e:
    print(f"LLM module load failed, using mock mode")
    
    def mock_explore(messages):
        return {
            "text": f"Shadow responds to your summoning...\nAbout '{messages[-1]['content'][:30]}...' is interesting!",
            "data": None
        }
    
    def mock_design(idea):
        return {
            "text": f"Mod generated!\nName: Mod_{datetime.now().strftime('%H%M')}",
            "data": {
                "name": f"Mod_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "desc": idea,
                "lua_code": "-- DST Mod\nprint('Hello')",
                "modinfo": 'version = 1\nname = "AI Mod"'
            }
        }
    
    design_with_llm = mock_design
    explore_with_llm = mock_explore

# Theme CSS
def get_theme_css(bg_url):
    return f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Griffy&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');
    
    :root {{
        --bg-image: url('{bg_url}') center/cover no-repeat;
        --thorn-brown: #8B4513;
        --highlight-gold: #FFD700;
        --text-primary: #F5E6C8;
        --border-gold: #A67C3B;
    }}
    
    html, body {{
        background-color: rgba(0,0,0,1) !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    .stApp, [class*="css"], [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    body::before {{
        content: "" !important;
        position: fixed !important;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1000 !important;
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), var(--bg-image) !important;
        background-size: cover !important;
    }}
    
    h1, h2, h3 {{ font-family: 'Creepster', cursive !important; color: var(--highlight-gold) !important; }}
    p, span, label, div {{ font-family: 'IM Fell English SC', serif !important; color: var(--text-primary) !important; }}
    
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(20,15,10,0.98) !important;
        border: 2px solid var(--border-gold) !important;
    }}
    
    ::-webkit-scrollbar {{ width: 8px !important; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(166,124,59,0.5) !important; }}
    </style>
    '''

# Session State
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_mods" not in st.session_state:
    st.session_state.generated_mods = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

# Background Image
def get_background_base64():
    try:
        bg_path = os.path.join(os.path.dirname(__file__), "封面图.png")
        if os.path.exists(bg_path):
            with open(bg_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        
        url = 'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=2073&q=80'
        with urllib.request.urlopen(url) as response:
            return base64.b64encode(response.read()).decode()
    except Exception as e:
        print(f"Background image load failed: {e}")
        return None

bg_base64 = get_background_base64()
bg_url = f'data:image/png;base64,{bg_base64}' if bg_base64 else '#000000'

# Inject Theme
print("=== App Starting ===")
theme_css = get_theme_css(bg_url)
st.markdown(theme_css, unsafe_allow_html=True)

# Banner
banner_html = '''
<div style="position:relative;z-index:5;text-align:center;margin:20px auto;max-width:950px;padding:50px;">
    <h1 style="font-family:'Creepster';font-size:3.8rem;color:#ffaa60;letter-spacing:5px;text-shadow:0 0 25px rgba(255,170,96,0.8);">饥荒 MOD 生成器</h1>
    <p class="subtitle" style="font-family:'Griffy';color:#aa8855;font-size:1.5rem;letter-spacing:3px;margin-top:10px;">DON'T STARVE TOGETHER MOD GENERATOR</p>
    
    <hr style="width:50%;border:none;border-top:2px solid #5a3a1a;margin:25px auto;opacity:0.7;">
    
    <p style="font-family:'IM Fell English SC';color:#d4c4a0;line-height:1.8;font-size:1.15rem;max-width:850px;margin:0 auto 35px;">
    When sanity reaches zero, reality collapses here.<br>
    <span style="color:#88aa66;">You are no longer a survivor, but a Creator of Nightmares.</span><br>
    Not a desperate survivor, but a creator weaving nightmares.<br>
    <span style="color:#88aa66;">Weave your madness into the Constant.</span>
    </p>
    
    <hr style="width:40%;border:none;border-top:2px solid #5a3a1a;margin:30px auto;opacity:0.7;">
    
    <div style="display:flex;gap:25px;flex-wrap:wrap;justify-content:center;margin-top:30px;">
        <div style="flex:1;min-width:300px;background:rgba(30,20,10,0.85)!important;border:2px solid #aa7733;padding:25px;">
            <div style="font-family:'Creepster';color:#ffaa60;font-size:1.7rem;text-align:center;margin-bottom:15px;">🔥 快速生成 / RAPID</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">For creators with clear vision. Directly forge your concept into downloadable files.</p>
        </div>
        
        <div style="flex:1;min-width:300px;background:rgba(20,30,20,0.85)!important;border:2px solid #668844;padding:25px;">
            <div style="font-family:'Creepster';color:#aadd88;font-size:1.7rem;text-align:center;margin-bottom:15px;">👁️ 探索设计 / EXPLORE</div>
            <p style="font-family:'IM Fell English SC';color:#d4c4a0;font-size:0.95rem;line-height:1.7;margin-top:10px;text-align:center;">For explorers in foggy inspiration. Dialogue with shadows to clarify your design.</p>
        </div>
    </div>
</div>
'''

st.markdown(banner_html, unsafe_allow_html=True)

# Mode Buttons
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("**🔥 快速生成**\nRAPID GENERATION", key="rapid_btn", use_container_width=True):
        st.session_state.mode = "rapid"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

with col2:
    if st.button("**👁️ 探索设计**\nDEEP EXPLORATION", key="explore_btn", use_container_width=True):
        st.session_state.mode = "explore"
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()

# Mode Confirmation
if st.session_state.mode != "home":
    mode_config = {
        "rapid": ("⚡", "#FFD700", "**Rapid Generation Activated**"),
        "explore": ("👁️", "#4CAF50", "**Deep Exploration Activated**"),
        "generating": ("⚙️", "#FF8C00", "**Reality Rewriting...**"),
        "generated": ("✅", "#66aa66", "**Mod Completed**")
    }
    icon, color, text = mode_config.get(st.session_state.mode, ("❓", "#888", "**Unknown Mode**"))
    st.markdown(f'<div style="text-align:center;padding:15px;margin:20px 0;background:rgba(0,0,0,0.5)!important;border:2px dashed {color};"><h3 style="color:{color};font-family:Creepster;">{icon} {text}</h3></div>', unsafe_allow_html=True)

# Explore Mode
if st.session_state.mode == "explore":
    st.info("💬 Talk to Shadow to refine design ideas")
    
    user_input = st.chat_input("Describe your ideas...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()
    
    # Generate Button
    if len(st.session_state.messages) >= 2:
        st.markdown("---")
        col1_gen, col2_gen = st.columns([4, 1])
        with col2_gen:
            if st.button("✨ Generate Final Mod", key="gen_from_explore", use_container_width=True):
                summary = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                st.session_state.final_prompt = summary
                st.session_state.mode = "generating"
                st.session_state.is_generating = True
                st.rerun()

# Rapid Mode
elif st.session_state.mode == "rapid":
    user_input = st.chat_input("Enter complete Mod concept...")
    if user_input and not st.session_state.is_generating:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_generating = True
        st.rerun()

# Generating Stage
if st.session_state.is_generating:
    loading_html = '''<div style="text-align:center;padding:40px;margin:30px 0;">
        <h2 style="font-family:'Creepster';color:#FFD700;font-size:2.5rem;text-shadow:0 0 15px rgba(255,215,0,0.7);animation:flicker 1.5s infinite alternate;">World Warping......<br>REALITY IS WARPING...</h2>
        <p style="font-family:'Griffy';color:#aa8855;font-size:1.2rem;margin-top:20px;">Shadows weaving your madness...<br>The shadows are weaving your madness...</p>
        <div style="margin-top:30px;font-size:2rem;color:#A67C3B;animation:rotate 3s linear infinite;">✦</div>
    </div>'''
    st.markdown(loading_html, unsafe_allow_html=True)
    
    time.sleep(2.5)
    
    try:
        if st.session_state.mode == "explore":
            result = design_with_llm(st.session_state.final_prompt)
        else:
            result = design_with_llm(st.session_state.messages[0]['content'])
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get('text', 'Shadow has responded...')
        })
        
        mod_data = result.get('data', {})
        if mod_data:
            new_mod = {
                "id": len(st.session_state.generated_mods) + 1,
                "name": mod_data.get('name', f"Mod #{len(st.session_state.generated_mods)+1}"),
                "desc": mod_data.get('desc', ''),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "lua_code": mod_data.get('lua_code', ''),
                "modinfo": mod_data.get('modinfo', '')
            }
            st.session_state.generated_mods.append(new_mod)
    
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Failed to generate: {str(e)}"
        })
    
    st.session_state.is_generating = False
    st.session_state.mode = "generated"
    st.rerun()

# Show Chat History
if st.session_state.messages:
    for msg in st.session_state.messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            color = '#FF8C00' if role == 'user' else '#4CAF50'
            name = 'Survivor' if role == 'user' else 'Shadow'
            chat_html = f'<div style="background:rgba(25,20,15,0.9)!important;border-left:4px solid {color}!important;padding:15px 20px!important;margin:15px 0!important;color:#F5E6C8;"><b style="color:{color};">{name}</b><br>{content}</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Mod Library")
    
    if not st.session_state.generated_mods:
        st.markdown('<div style="background:rgba(0,0,0,0.5)!important;border:1px dashed #A67C3B;padding:20px;text-align:center;"><p style="color:#888;font-size:0.9rem;margin:0;">No Mods Yet</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h4 style='color:#AA7733;'>Mod Records</h4>", unsafe_allow_html=True)
        for mod in st.session_state.generated_mods:
            st.markdown(f'<div style="background:rgba(30,20,10,0.7)!important;border:1px solid #A67C3B;padding:12px;margin-bottom:10px;"><strong style="color:#FFD700;">{mod["name"]}</strong><br><small style="color:#888;">{mod["date"]}</small></div>', unsafe_allow_html=True)
    
    st.divider()
    st.write(f"Chat: {len(st.session_state.messages)} messages")
    
    if st.session_state.generated_mods:
        st.markdown("---")
        mod = st.session_state.generated_mods[-1]
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("modinfo.lua", mod.get("modinfo", ""))
            zip_file.writestr("main.lua", mod.get("lua_code", "") or "print('Hello')")
        
        zip_buffer.seek(0)
        
        col1_dl, col2_dl = st.columns(2)
        with col1_dl:
            st.download_button(
                label="Download ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"{mod['name'].replace(' ', '_')}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        with col2_dl:
            if st.button("Regenerate", use_container_width=True):
                st.session_state.mode = "explore"
                st.session_state.messages = []
                st.rerun()
    
    st.divider()
    if st.button("Clear All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
