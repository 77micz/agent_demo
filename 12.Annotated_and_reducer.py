
# ----------------------------- 导入依赖 -----------------------------
# 导入类型提示
from typing import TypedDict,Annotated
# 导入加法运算符
from operator import add
# 导入消息
from langgraph.graph.message import add_messages



# ----------------------------- 定义状态 -----------------------------

class State(TypedDict):
    # 普通字段
    name: str
    age: int

    # 累加字段
    count: Annotated[int, add]

    # 不同的更新策略
    messages: Annotated[list, add_messages]

    tags: Annotated[list, lambda old,new: list(set(old + new))]









