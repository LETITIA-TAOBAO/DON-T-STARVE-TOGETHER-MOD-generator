import re
from .keywords import *

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

def parse(text):
    intent = ModIntent()

    # 实体
    if "怪物" in text:
        intent.entity = "creature"

    # 触发条件
    if "晚上" in text:
        intent.triggers.append("night")

    # 行为
    if "发光" in text:
        intent.behaviors.append("light")

    if "变强" in text:
        intent.behaviors.append("buff")

    # 参数
    if "高血量" in text:
        intent.params["health"] = 200

    return intent