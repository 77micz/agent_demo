# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver


# ----------------------------- 定义状态 -----------------------------
class MainGraph(TypedDict):
    user_query: str
    search_results: list[str]
    final_result: str


class SubGraph(TypedDict):
    query: str
    search: list[str]


# ----------------------------- 定义节点 -----------------------------


def sub_to_main(state: SubGraph) -> dict[str, list[str]]:
    """
    子图映射到主图
    :param state: 子图状态
    :return:
    """

    logger.info(state)

    return {"search_results": state.get("search", ["message"])}


def main_to_sub(state: MainGraph) -> dict[str, str]:
    """
    主图映射到子图
    :param state: 主图状态
    :return:
    """
    return {"query": state.get("user_query", "")}


def use_map(state: MainGraph) -> dict[str, list[str]]:
    """
    调用子图
    :param state:
    :return:
    """

    # 主图映射到子图
    sub_input = main_to_sub(state)

    # 调用子图
    sub_result=sub_graph_compile.invoke(sub_input)

    # 子图映射到主图
    return sub_to_main(sub_result)




# ----------------------------- 定义图 -----------------------------

graph = StateGraph(MainGraph)
sub_graph = StateGraph(SubGraph)

graph.add_node("main_to_sub", main_to_sub)
sub_graph.add_node("sub_to_main", sub_to_main)
graph.add_node("use_map", use_map)

graph.add_edge(START, "main_to_sub")
graph.add_edge("main_to_sub", "use_map")
graph.add_edge("use_map",END)

sub_graph.add_edge(START, "sub_to_main")
sub_graph.add_edge("sub_to_main", END)


graph_compile = graph.compile()
sub_graph_compile = sub_graph.compile()

# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({"user_query": "你好"})
logger.info(result)

