
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal,Annotated
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class CustomServiceState(TypedDict):
    user_query: str
    intent: str
    result: str
    experts_result: Annotated[list,lambda old,new: old+new]


# ----------------------------- 定义节点 -----------------------------

def supervisor_analyze_intent(state: CustomServiceState) -> dict[str, str]:
    """
    分析用户意图
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行分析用户意图")
    user_query = state.get("user_query", "")

    if "退款" in user_query or "售后" in user_query:
        return {"intent": "退款售后"}
    elif "订单" in user_query or "订单查询" in user_query:
        return {"intent": "订单查询"}
    elif "商品" in user_query or "商品查询" in user_query:
        return {"intent": "商品查询"}
    else:
        return {"intent": "其他"}


def refund_expert(state: CustomServiceState) -> dict[str, list[str]]:
    """
    退款售后专家
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("用户意图与售后相关")
    return {"experts_result": ["退款售后专家结果"]}


def shipping_expert(state: CustomServiceState) -> dict[str, list[str]]:
    """
    订单查询专家
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("用户意图与订单查询相关")
    return {"experts_result": ["订单查询专家结果"]}


def product_expert(state: CustomServiceState) -> dict[str, list[str]]:
    """
    商品查询专家
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("用户意图与商品查询相关")
    return {"experts_result": ["商品查询专家结果"]}


def general_expert(state: CustomServiceState) -> dict[str, list[str]]:
    """
    通用专家
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("用户意图与其他相关")
    return {"experts_result": ["通用专家结果"]}



def route_by_intent(state: CustomServiceState) -> Literal["refund_expert","shipping_expert","product_expert","general_expert"]:
    """
    根据用户意图路由到对应的专家
    :param state:
    :return:
    """
    intent = state.get("intent", "")
    if intent == "退款售后":
        return "refund_expert"
    elif intent == "订单查询":
        return "shipping_expert"
    elif intent == "商品查询":
        return "product_expert"
    else:
        return "general_expert"



# ----------------------------- 定义图 -----------------------------

graph = StateGraph(CustomServiceState)


graph.add_node("supervisor_analyze_intent", supervisor_analyze_intent)
graph.add_node("refund_expert", refund_expert)
graph.add_node("shipping_expert", shipping_expert)
graph.add_node("product_expert", product_expert)
graph.add_node("general_expert", general_expert)



graph.add_edge(START, "supervisor_analyze_intent")
graph.add_conditional_edges(
    "supervisor_analyze_intent",
    route_by_intent,
    {
        "refund_expert": "refund_expert",
        "shipping_expert": "shipping_expert",
        "product_expert": "product_expert",
        "general_expert": "general_expert"
    }
)
for node in ["refund_expert","shipping_expert","product_expert","general_expert"]:
    graph.add_edge(node, END)




graph_compile = graph.compile()

# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({"user_query": "帮我查询售后"})
print(f"最终结果：{result}")








