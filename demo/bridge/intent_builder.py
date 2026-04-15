class ModIntent:
    def __init__(self):
        self.entity = None
        self.triggers = []
        self.behaviors = []
        self.params = {}

    def to_dict(self):
        return {
            "entity": self.entity,
            "triggers": self.triggers,
            "behaviors": self.behaviors,
            "params": self.params
        }


def build_intent_from_design(design):
    intent = ModIntent()

    # 实体
    intent.entity = design.get("entity", "creature")

    # mechanics → triggers / behaviors
    for m in design.get("mechanics", []):
        if m == "night":
            intent.triggers.append("night")
        elif m == "light":
            intent.behaviors.append("light")
        elif m == "buff":
            intent.behaviors.append("buff")

    return intent
