API_MAP = {
    "light": {
        "apis": [
            "inst.entity:AddLight()"
        ],
        "desc": "添加发光效果"
    },
    "buff": {
        "apis": [
            "inst:AddComponent('combat')",
            "inst.components.combat:SetDamage(50)"
        ],
        "desc": "增强战斗能力"
    },
    "night": {
        "apis": [
            "TheWorld.state.isnight"
        ],
        "desc": "判断是否为夜晚"
    }
}