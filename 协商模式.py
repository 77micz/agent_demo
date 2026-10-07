
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal,Annotated
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class VotingState(TypedDict):
    proposal: str
    votes: Annotated[list,lambda old,new: old+new]
    decision: str


# ----------------------------- 定义节点 -----------------------------

def agent1_vote(state: VotingState) -> dict[str, list[dict[str, str]]]:
    """
    代理1投票
    :param state: 投票状态
    :return: 更新 state
    """
    logger.info("执行代理1投票")
    proposal = state.get("proposal", "")
    if "退款" in proposal:
        return {"votes": [{"agent":"agent1","vote":"同意"}]}
    else:
        return {"votes": [{"agent":"agent1","vote":"不同意"}]}


def agent2_vote(state: VotingState) -> dict[str, list[dict[str, str]]]:
    """
    代理2投票
    :param state: 投票状态
    :return: 更新 state
    """
    logger.info("执行代理2投票")
    proposal = state.get("proposal", "")
    if "成本" in proposal:
        return {"votes": [{"agent":"agent2","vote":"同意"}]}
    else:
        return {"votes": [{"agent":"agent2","vote":"不同意"}]}


def agent3_vote(state: VotingState) -> dict[str, list[dict[str, str]]]:
    """
    代理3投票
    :param state: 投票状态
    :return: 更新 state
    """
    logger.info("执行代理3投票")
    proposal = state.get("proposal", "")
    if "优化" in proposal:
        return {"votes": [{"agent":"agent3","vote":"同意"}]}
    else:
        return {"votes": [{"agent":"agent3","vote":"不同意"}]}





def calculate_votes(state: VotingState) -> dict[str, str]:
    """
    计算投票结果
    :param state: 投票状态
    :return: 更新 state
    """
    logger.info("计算投票结果，超过一半同意同意，否则不同意。")
    votes = state.get("votes", [])
    if sum([1 for vote in votes if vote["vote"] == "同意"]) > len(votes) / 2:
        return {"decision": "同意"}
    else:
        return {"decision": "不同意"}



# ----------------------------- 定义图 -----------------------------

graph = StateGraph(VotingState)


graph.add_node("agent1_vote", agent1_vote)
graph.add_node("agent2_vote", agent2_vote)
graph.add_node("agent3_vote", agent3_vote)
graph.add_node("calculate_votes", calculate_votes)





graph.add_edge(START, "agent1_vote")
graph.add_edge(START, "agent2_vote")
graph.add_edge(START, "agent3_vote")

for node in ["agent1_vote","agent2_vote","agent3_vote"]:
    graph.add_edge(node, "calculate_votes")
graph.add_edge("calculate_votes", END)




graph_compile = graph.compile()

# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({"proposal": "帮我查询退款"})
print(f"最终结果：{result}")








