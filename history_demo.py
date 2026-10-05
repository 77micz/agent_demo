
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class History(TypedDict):
    count: int
    history: list[str]


# ----------------------------- 定义节点 -----------------------------

def increment(state: History) -> dict[str, str]:
    """
    增加历史记录计数
    :param state: 历史记录状态
    :return: 更新 state
    """
    new_count = state.get("count", 0) + 1
    return {"count": new_count, "history": state.get("history", [])+[f"第{new_count}条记录"]}



# ----------------------------- 定义图 -----------------------------

graph = StateGraph(History)

graph.add_node("increment1", increment)
graph.add_node("increment2", increment)
graph.add_node("increment3", increment)


graph.add_edge(START, "increment1")
graph.add_edge("increment1", "increment2")
graph.add_edge("increment2", "increment3")
graph.add_edge("increment3", END)


memory_saver = MemorySaver()

graph_compile = graph.compile(checkpointer=memory_saver)

# ----------------------------- 执行 -----------------------------

config={"configurable": {"thread_id": "history_demo"}}
result = graph_compile.invoke({"count": 0,"history": []}, config=config)
print(f"最终结果：{result}")


# ----------------------------- 获取执行历史 -----------------------------
history = graph_compile.get_state_history(config=config)

# # 打印执行历史
# for item in history:
#     print(item)



# ----------------------------- 回溯历史节点 -----------------------------
target_point=list(history)[-2]
print(f"回溯到节点：{target_point.values}")

new_config = {
    "configurable": {
        "thread_id": "history_demo", # history_demo历史记忆
        "checkpoint_id": target_point.config["configurable"]["checkpoint_id"], # 回溯到目标节点的checkpoint_id
    }
}


# 继续执行
result = graph_compile.invoke(None, config=new_config)
print(f"最终结果：{result}")







