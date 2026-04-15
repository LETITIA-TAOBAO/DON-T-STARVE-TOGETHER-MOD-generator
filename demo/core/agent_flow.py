# core/agent_flow.py

from llm.qwen_client import explore_with_llm, design_with_llm
from bridge.intent_builder import build_intent_from_design
from parser.recommender import recommend


def explore_step(messages):
    return explore_with_llm(messages)


def generate_step(messages):
    design_str = design_with_llm(messages)

    import json
    design = json.loads(design_str)

    intent = build_intent_from_design(design)
    result = recommend(intent)

    return design, result