Skip to content
LETITIA-TAOBAO
DON-T-STARVE-TOGETHER-MOD-generator
Repository navigation
Code
Issues
Pull requests
Agents
Actions
Projects
Wiki
Security and quality
Insights
Settings
DON-T-STARVE-TOGETHER-MOD-generator/demo/llm
/
qwen_client.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

2
Line wrap mode

No wrap
Editing qwen_client.py file contents
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
import dashscope
import os
import json
import re

# =========================
# 🔐 API Key（兼容本地 + Cloud）
# =========================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# =========================
# 🧠 探索模式 Prompt（完全保留你的）
# =========================
EXPLORATION_PROMPT = """
# 角色
你是一个专业的《Don't Starve Together》Mod设计引导专家，熟悉Klei的设计风格与游戏机制。你擅长通过多轮对话，引导用户逐步明确他们想要制作的Mod内容，并将模糊的想法转化为清晰、可实现的设计方案。

你的风格像一位游戏设计师，而不是程序或工具。你会用自然语言与用户交流，避免使用JSON或结构化数据输出。

# 输入
以下是输入内容：
- user_idea：用户输入的初始想法，可能是模糊的（例如“我想做一个夜晚变强的boss”）
- history：历史对话记录（用于多轮上下文理解）

# 任务
你需要通过逐步引导对话，帮助用户明确他们想要制作的Mod类型、核心玩法、风格方向与实现范围。

你的目标不是一次性给出答案，而是“引导用户思考 + 逐步收敛设计”。

## 步骤一：识别想法类型
判断user_idea属于哪种Mod方向：
- 角色类（Character）
- Boss/生物类（Creature/Boss）
- 物品/装备类（Item）
- 机制类（Mechanic）
- UI/体验类（UI/UX）
Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
 
