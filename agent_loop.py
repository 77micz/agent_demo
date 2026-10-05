# ----------------------------- 导入依赖 -----------------------------
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Any
from langchain_openai import ChatOpenAI
import os
from langgraph.graph.message import add_messages
from loguru import logger
import json

# 初始化模型
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10,  # 超时时间，单位秒，默认10秒，10秒超时
    max_retries=3,  # 最大重试次数，默认3次
    model_kwargs={"response_format": {"type": "json_object"}},  # 响应格式为json_object
)

# 返回结构
result_format = {
    "final_result": "最终结果。任务完成时返回，否则为空字符串''",
    "tool_call": ["工具调用1", "工具调用2", "没有返回空列表[]"],
    "response": "未完成任务时的思考内容,任务已完成时为空字符串''"
}
result_format_json = json.dumps(result_format, ensure_ascii=False)


# ----------------------------- 定义状态 -----------------------------
class AgentLoopState(TypedDict):
    messages: Annotated[list, add_messages]  # 消息列表
    times: int  # 循环次数
    max_times: int  # 最大循环次数
    final_result: str  # 最终结果


# ----------------------------- 定义节点 -----------------------------


def route(state: AgentLoopState) -> Literal["act", "end"]:
    """
    决定是否继续循环或结束循环
    :param state: 状态
    :return: 更新 state
    """

    # 检查是否有最终答案
    if state.get("final_result", None) is not None:
        return "end"

    # 检查是否超过最大循环次数
    if state.get("times", 0) >= state.get("max_times"):
        return "end"

    # 继续循环
    return "act"


def think(state: AgentLoopState) -> dict[str, list[dict[str, str | list[Any]]]]:
    """
    思考
    :param state: 状态
    :return: 更新 state
    """

    logger.info("思考中...")

    messages = state.get("messages")

    # 提示词

    content = messages[-1].content
    prompt = f"""
    你需要在每次返回中，判断任务是否已完成
    以json格式返回，响应结构：
{result_format_json}
    """

    user_prompt = f"""用户输入：{content}"""

    # 替换系统消息
    if state.get("times", 0) != 0:
        messages.pop()
    messages.insert(0, prompt)

    messages.append({"role": "user", "content": user_prompt})

    # 调用模型
    response = client.invoke(messages)

    return {"messages": [{"role": "assistant", "content": response.content}], "times": state.get("times", 0) + 1}


def act(state: AgentLoopState) -> dict[str, list[dict[str, str]]]:
    """
    执行
    :param state: 状态
    :return: 更新 state
    """

    logger.info("调用工具...")

    return {"messages": [{"role": "system", "content": "模拟调用工具结果"}]}


# ----------------------------- 定义图 -----------------------------

graph = StateGraph(AgentLoopState)

graph.add_node("think", think)
graph.add_node("act", act)

graph.add_edge(START, "think")
graph.add_conditional_edges(
    "think",
    route,
    {"act": "act", "end": END}
)
graph.add_edge("act", "think")

app = graph.compile()

# ----------------------------- 执行 -----------------------------
result = app.invoke({"messages": [{"role": "user", "content": "你好"}], "times": 0, "max_times": 3})
print(result)
