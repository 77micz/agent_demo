
# 导入langgraph
from langgraph.graph import StateGraph,START,END
# 导入TypeDict
from typing import TypedDict



# 定义状态
class HelloState(TypedDict):
    name: str
    greeting: str


# 定义节点
def greet(state:HelloState) -> dict[str, str]:
    name = state["name"]
    return {"greeting": f"你好,{name}!"}

def hello(state:HelloState) -> dict[str, str]:
    greeting = state["greeting"]
    return {"greeting": greeting+"hello"}


# 定义图
graph = StateGraph(HelloState)
# 添加节点
graph.add_node("greet",greet)
graph.add_node("hello",hello)
# 添加边
graph.add_edge(START,"greet")
graph.add_edge("greet","hello")
graph.add_edge("hello",END)


# 编译图
graph_compile = graph.compile()

state = {"name": "张三"}

# 执行图
result = graph_compile.invoke(state)
print(result)





