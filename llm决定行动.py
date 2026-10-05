
# ----------------------------- 导入依赖 -----------------------------
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Literal
from langchain_openai import ChatOpenAI
import os





# 初始化模型
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10,  # 超时时间，单位秒，默认10秒，10秒超时
    max_retries=3,  # 最大重试次数，默认3次
    model_kwargs={"response_format": {"type": "json_object"}},  # 响应格式为json_object
)



# ----------------------------- 定义状态 -----------------------------
class State(TypedDict):
    messages: list # 消息列表
    next_action: Literal["search","calculate","response"] # 下一步行动



# ----------------------------- 定义节点 -----------------------------


def next_action(state: State) -> Literal["search","calculate","response"]:
    """
    决定下一步行动
    :param state: 状态
    :return: 更新 state
    """

    messages = state.get("messages")

    # 提示词
    content = messages[-1].content
    prompt = f"""
    根据用户输入内容，判断下一步行动
    可选行动：
    - search：搜索相关资料
    - calculate：计算相关数据
    - response：直接回复用户
    只返回选择的行动不要包含其他内容，例如："search"
"""

    user_prompt = f"""用户输入：{content}"""

    # 替换第一个消息
    messages.pop()
    messages.insert(0,prompt)

    messages.append(user_prompt)

    # 调用模型
    response = client.invoke(messages)

    if response.content == "search":
        return "search"
    elif response.content == "calculate":
        return "calculate"
    elif response.content == "response":
        return "response"
    else:
        return "response"





def search(state: State) -> dict[str, str]:
    """
    搜索相关资料
    :param state: 状态
    :return: 更新 state
    """
    return {"next_action": "search"}


def calculate(state: State) -> dict[str, str]:
    """
    计算相关数据
    :param state: 状态
    :return: 更新 state
    """
    return {"next_action": "calculate"}


def response(state: State) -> dict[str, str]:
    """
    直接回复用户
    :param state: 状态
    :return: 更新 state
    """
    return {"next_action": "response"}


# ----------------------------- 定义图 -----------------------------

graph = StateGraph(State)

graph.add_node("next_action",next_action)
graph.add_node("search",search)
graph.add_node("calculate",calculate)
graph.add_node("response",response)



graph.add_edge(START,"next_action")
graph.add_conditional_edges(
    "next_action",
    next_action,
    {"search":"search","calculate":"calculate","response":"response"}
)

for node in ["search","calculate","response"]:
    graph.add_edge(node,END)

app = graph.compile()

# ----------------------------- 执行 -----------------------------
result = app.invoke({})
print(result)









