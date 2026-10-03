# ----------------------------- 导入依赖 -----------------------------
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
import os





# ----------------------------- 连接数据库 -----------------------------

import sqlite3

db_path = Path(__file__).parent/"data/session_history/test.db"
os.makedirs(db_path.parent, exist_ok=True)
# 连接数据库
conn = sqlite3.connect(
    db_path, # 数据库路径
    check_same_thread=False, # 允许在不同线程中使用
)



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

# 创建sqlite保存器
sqlitesaver = SqliteSaver(conn=conn)

# 编译图传入sqlite保存器
graph_compile = graph.compile(checkpointer=sqlitesaver)

# ----------------------------- 测试 -----------------------------

# 配置1
config1 = {"configurable": {"thread_id": "thread_2"}}

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
