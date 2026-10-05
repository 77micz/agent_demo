
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class Review(TypedDict):
    content: str
    approved: bool
    feedback: str


# ----------------------------- 定义节点 -----------------------------

def generate(state: Review) -> dict[str, str]:
    """
    生成审核内容
    :param state: 审核状态
    :return: 更新 state
    """
    return {"content": "一条内容",}





def review(state: Review) -> dict[str, str]:
    """
    人工审核审核内容
    :param state: 审核状态
    :return: 更新 state
    """

    logger.info(f"正在人工审核内容：{state['content']}")

    approval = interrupt({"question": "是否通过审核？", "options": ["approve", "reject", "change"], })

    if approval == "approve":
        return {"approved": True, "feedback": "通过审核"}
    elif approval == "reject":
        return {"approved": False, "feedback": "拒绝通过"}
    else:
        return {"approved": False, "feedback": "请修改内容"}



def publish(state: Review) -> dict[str, str]:
    """
    发布审核内容
    :param state: 审核状态
    :return: 更新 state
    """
    logger.info(f"正在发布审核内容：{state['content']}")
    return {}


def reject(state: Review) -> dict[str, str]:
    """
    拒绝审核内容
    :param state: 审核状态
    :return: 更新 state
    """
    logger.info(f"拒绝发布内容：{state['content']}")
    return {}


def route(state: Review) -> Literal["publish", "reject"]:
    """
    根据审核结果路由审核内容
    :param state: 审核状态
    :return: 路由结果
    """
    if state.get("approved"):
        return "publish"
    else:
        return "reject"


# ----------------------------- 定义图 -----------------------------

graph = StateGraph(Review)

graph.add_node("review", review)
graph.add_node("publish", publish)
graph.add_node("reject", reject)
graph.add_node("generate", generate)

graph.add_edge(START, "generate")
graph.add_edge("generate", "review")
graph.add_conditional_edges(
    "review",
    route,
    {
        "publish": "publish",
        "reject": "reject",
    }
)

for node in ["publish", "reject"]:
    graph.add_edge(node, END)


memory_saver = MemorySaver()

graph_compile = graph.compile(checkpointer=memory_saver)

# ----------------------------- 执行 -----------------------------

config={"configurable": {"thread_id": "thread_0"}}
result = graph_compile.invoke({}, config=config)
print(f"{result}")

state = graph_compile.get_state(config=config)
print(f"暂停节点：{state.interrupts[0].value}")

logger.info("正在进行人工审核")
graph_compile.update_state(config=config, values={"approved": True, "feedback": "通过审核"})

# 继续执行
result = graph_compile.invoke(None, config=config)
print(f"最终结果：{result}")



