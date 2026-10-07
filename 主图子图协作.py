
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class MainGraph(TypedDict):
    number: int
    final_result: int


class SubGraph(TypedDict):
    num: int
    result: int

# ----------------------------- 定义节点 -----------------------------


def sub_step1(state:SubGraph) -> dict[str, int]:
    """
    子图1：返回num
    :param state: 子图状态
    :return:
    """
    return {"num": state.get("num", 0)+10}
def sub_step2(state:SubGraph) -> dict[str, int]:
    """
    子图2：返回result
    :param state: 子图状态
    :return:
    """
    return {"result": state.get("num", 0)*2}


def main_step1(state:MainGraph) -> dict[str, int]:
    """
    主图1：返回number
    :param state: 主图状态
    :return:
    """

    return {"number": 30}


def main_step2(state:MainGraph) -> dict[str, int]:
    """
    主图2：调用子图
    :param state: 主图状态
    :return:
    """
    result = subGraph_compile.invoke({"num": state.get("number", 0)})
    return {"final_result": result.get("result", 0)}


# ----------------------------- 子图 -----------------------------

subGraph = StateGraph(SubGraph)

subGraph.add_node("sub_step1", sub_step1)
subGraph.add_node("sub_step2", sub_step2)


subGraph.add_edge(START, "sub_step1")
subGraph.add_edge("sub_step1", "sub_step2")
subGraph.add_edge("sub_step2", END)



subGraph_compile = subGraph.compile()



# ----------------------------- 主图 -----------------------------

graph = StateGraph(MainGraph)

graph.add_node("main_step1", main_step1)

graph.add_node("main_step2", main_step2)
graph.add_edge(START, "main_step1")
graph.add_edge("main_step1", "main_step2")
graph.add_edge("main_step2", END)

graph_compile = graph.compile()


# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({})
print(f"最终结果：{result}")







