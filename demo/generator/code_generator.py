def generate_code(intent):
    lines = []

    # ===== 触发条件 =====
    if "night" in intent.triggers:
        lines.append("if TheWorld.state.isnight then")

    # ===== 行为 =====
    if "light" in intent.behaviors:
        lines.append("    inst.entity:AddLight()")

    if "buff" in intent.behaviors:
        lines.append("    inst:AddComponent('combat')")
        lines.append("    inst.components.combat:SetDamage(50)")

    # ===== 结束 =====
    if "night" in intent.triggers:
        lines.append("end")

    return "\n".join(lines)