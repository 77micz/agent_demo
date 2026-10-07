

# ----------------------------- 导入依赖 -----------------------------
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Literal



# ----------------------------- 定义状态 -----------------------------
class State(TypedDict):
    score: float # 用户输入的分数
    decision: Literal["accept","reject","review"] # 路由决策



# ----------------------------- 定义节点 -----------------------------


def evaluate_score(state: State) -> dict[str, float]:
    """
    评估用户输入的分数
    :param state: 状态
    :return: 更新 state
    """
    return {"score": 0.75}


def route(state: State) -> Literal["accept","reject","review"]:
    """
    路由用户输入的分数
    :param state: 状态
    :return: 更新 state
    """
    if state.get("score") < 0.5:
        return "accept"
    elif state.get("score") < 0.75:
        return "review"
    else:
        return "reject"


def accept(state: State) -> dict[str, str]:
    """
    通过用户输入的分数
    :param state: 状态
    :return: 更新 state
    """
    return {"decision": "accept"}


def reject(state: State) -> dict[str, str]:
    """
    拒绝用户输入的分数
    :param state: 状态
    :return: 更新 state
    """
    return {"decision": "reject"}


def review(state: State) -> dict[str, str]:
    """
    审核用户输入的分数
    :param state: 状态
    :return: 更新 state
    """
    return {"decision": "review"}


# ----------------------------- 定义图 -----------------------------

graph = StateGraph(State)

graph.add_node("route",route)
graph.add_node("accept",accept)
graph.add_node("reject",reject)
graph.add_node("review",review)
graph.add_node("evaluate_score",evaluate_score)


graph.add_edge(START,"evaluate_score")
graph.add_conditional_edges(
    "evaluate_score",
    route,
    {"accept":"accept","reject":"reject","review":"review"}
)

for node in ["accept","reject","review"]:
    graph.add_edge(node,END)

app = graph.compile()

# ----------------------------- 执行 -----------------------------
result = app.invoke({})
print(result)
print(type(result))









