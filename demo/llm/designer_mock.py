def design_with_llm(user_input):
    result = {
        "concept": "",
        "entity": "boss" if "boss" in user_input else "creature",
        "mechanics": [],
        "design": {},
        "questions": []
    }

    if "晚上" in user_input:
        result["mechanics"].append("night")

    if "发光" in user_input:
        result["mechanics"].append("light")

    if "变强" in user_input:
        result["mechanics"].append("buff")

    result["concept"] = f"一个具有{','.join(result['mechanics'])}特性的{result['entity']}"

    result["questions"] = [
        "这个Boss的攻击方式是？（近战 / 远程 / 召唤）",
        "它是否敌对玩家？",
        "是否有特殊技能（范围攻击 / 控制）？",
        "是否有阶段变化（例如二阶段）？"
    ]

    return result