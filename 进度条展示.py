# ----------------------------- 导入依赖 -----------------------------
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Any
from langchain_openai import ChatOpenAI
import os
from langgraph.graph.message import add_messages
from loguru import logger
import json
from operator import add


# ----------------------------- 定义状态 -----------------------------
class ProcessState(TypedDict):
    total_items: int
    process_items: Annotated[int, add]
    current_step: str
    progress: float


# ----------------------------- 定义节点 -----------------------------


def step1(state: ProcessState) -> dict[str, int | str | float]:
    """
    数据准备
    :param state: 状态
    :return: 更新 state
    """

    return {
        "process_items": 50,
        "current_step": "step1",
        "progress": 20,
    }



def step2(state: ProcessState) -> dict[str, int | str | float]:
    """
    step2
    :param state: 状态
    :return: 更新 state
    """

    return {
        "process_items": 20,
        "current_step": "step2",
        "progress": 60,
    }



def step3(state: ProcessState) -> dict[str, int | str | float]:
    """
    step3
    :param state:
    :return: 更新 state
    """

    return {
        "process_items": 30,
        "current_step": "step3",
        "progress": 100,
    }


# ----------------------------- 定义图 -----------------------------

graph = StateGraph(ProcessState)

graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)

graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

app = graph.compile()

# ----------------------------- 执行 -----------------------------

print("\n处理任务...")
for state in app.stream({"total_items": 100, "processed_items": 0}, stream_mode="values"):
    step = state.get("current_step", "初始化")
    progress = state.get("progress", 0)
    processed = state.get("processed_items", 0)
    bar_length = 30
    filled = int(bar_length * progress / 100)
    bar = "■" * filled + "░" * (bar_length - filled)
    print(f"\r{step}: [{bar}] {progress:.0f}% ({processed}/{state['total_items']})", end="", flush=True)
