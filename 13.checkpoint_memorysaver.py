# ----------------------------- 导入依赖 -----------------------------
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END


# ----------------------------- 定义状态 -----------------------------

class State(TypedDict):
    count: int


# ----------------------------- 定义节点 -----------------------------

def add(state: State) -> dict[str, int]:
    return {"count": state.get("count", 0) + 1}


# ----------------------------- 定义流程 -----------------------------

graph = StateGraph(State)
graph.add_node("add", add)
graph.add_edge(START, "add")
graph.add_edge("add", END)

# 创建内存保存器
memorysaver = MemorySaver()

# 编译图传入内存保存器
graph_compile = graph.compile(checkpointer=memorysaver)

# ----------------------------- 测试 -----------------------------

# 配置1
config1 = {"configurable": {"thread_id": "thread_1"}}

# 调用图
result = graph_compile.invoke(
    {},
    config=config1,
)
print(result)

# 再次调用
result = graph_compile.invoke(
    {},
    config=config1,
)
print(result)
