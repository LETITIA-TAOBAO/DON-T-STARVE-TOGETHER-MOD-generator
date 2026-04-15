from llm.qwen_client import design_with_llm
from bridge.intent_builder import build_intent_from_design
from parser.recommender import recommend
from generator.code_generator import generate_code
import json


def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except:
                pass

    return {
        "concept": "解析失败",
        "entity": "Unknown Boss",
        "mechanics": [],
        "questions": ["请重新描述你的需求"]
    }


def main():
    print("🎮 AI Mod Designer（完整闭环版）")

    while True:
        user_input = input("\n👉 输入你的想法：")

        if user_input.lower() == "exit":
            break

        # ===== 1. LLM设计 =====
        design_str = design_with_llm(user_input)
        design = safe_json_parse(design_str)

        print("\n🧠 设计概念：")
        print(design.get("concept", ""))

        print("\n❓ AI建议你补充：")
        for q in design.get("questions", []):
            print("-", q)

        # ===== 2. intent =====
        intent = build_intent_from_design(design)

        print("\nDEBUG intent:", intent)

        # ===== 3. 推荐 =====
        result = recommend(intent) or {}

        print("\n🔧 推荐API：")
        for api in result.get("apis", []):
            print("-", api)

        print("\n📌 实现步骤：")
        for i, step in enumerate(result.get("steps", []), 1):
            print(f"{i}. {step}")

        print("\n💻 示例Lua代码（可用于mod）：")
        print(result.get("code", "-- no code generated"))

        # ===== 4. 生成代码（保留） =====
        code = generate_code(intent)

        print("\n🧾 额外生成代码：")
        print(code)


if __name__ == "__main__":
    main()