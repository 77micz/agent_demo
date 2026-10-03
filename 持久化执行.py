# ----------------------------- 导入依赖 -----------------------------
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
import os
from operator import add
from loguru import logger





# ----------------------------- 连接数据库 -----------------------------

import sqlite3

thread_str="thread_3"
db_path = Path(__file__).parent/f"data/session_history/{thread_str}.db"
os.makedirs(db_path.parent, exist_ok=True)
# 连接数据库
conn = sqlite3.connect(
    db_path, # 数据库路径
    check_same_thread=False, # 允许在不同线程中使用
)



# ----------------------------- 定义状态 -----------------------------

class State(TypedDict):
    total_items: int
    process_items: Annotated[int, add]
    failed_items: Annotated[int, add]
    result: Annotated[list, lambda old,new:old+new]


# ----------------------------- 定义节点 -----------------------------


def fetch_item(state: State) -> dict[str, int]:
    return {"total_items": state.get("total_items", 0) + 100}



def batch_process_1(state: State) -> dict[str, int]:
    logger.info(f"正在处理1-33条数据")

    return {"process_items": 33,"result": [f"item_{i}" for i in range(1,34)]}


def batch_process_2(state: State) -> dict[str, int]:
    logger.info(f"正在处理34-66条数据")
    # if state.get("process_items") == 33:
    #     raise Exception("batch_process_2发生异常，处理失败")
    return {"process_items": 33, "result": [f"item_{i}" for i in range(34, 67)]}


def batch_process_3(state: State) -> dict[str, int]:
    logger.info(f"正在处理67-100条数据")

    return {"process_items": 34, "result": [f"item_{i}" for i in range(67, 101)]}


def final(state: State) -> dict:
    logger.info(f"""
处理完毕，详情如下：
已处理数据量：{state.get("process_items", 0)}
失败数据量：{state.get("failed_items", 0)}
处理结果：{state.get("result", [])}
""")
    return {"total_items": state.get("total_items", 0)}


# ----------------------------- 定义流程 -----------------------------

graph = StateGraph(State)
graph.add_node("fetch_item", fetch_item)
graph.add_node("batch_process_1", batch_process_1)
graph.add_node("batch_process_2", batch_process_2)
graph.add_node("batch_process_3", batch_process_3)
graph.add_node("final", final)

graph.add_edge(START, "fetch_item")
graph.add_edge("fetch_item", "batch_process_1")
graph.add_edge("batch_process_1", "batch_process_2")
graph.add_edge("batch_process_2", "batch_process_3")
graph.add_edge("batch_process_3", "final")
graph.add_edge("final", END)



# 创建sqlite保存器
sqlitesaver = SqliteSaver(conn=conn)

# 编译图传入sqlite保存器
graph_compile = graph.compile(checkpointer=sqlitesaver)

# ----------------------------- 测试 -----------------------------



# 配置1
config1 = {"configurable": {"thread_id": thread_str}}

# 调用图
try:
    result = graph_compile.invoke(
        {},
        config=config1,
    )
except Exception as e:
    logger.error(e)








