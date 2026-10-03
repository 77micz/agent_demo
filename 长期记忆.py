# ----------------------------- 导入依赖 -----------------------------
from langchain_openai import ChatOpenAI
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add
from loguru import logger
from langgraph.graph.message import add_messages
import json
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ----------------------------- 全局变量 -----------------------------


# 初始化模型
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10,  # 超时时间，单位秒，默认10秒，10秒超时
    max_retries=3,  # 最大重试次数，默认3次
    model_kwargs={"response_format": {"type": "json_object"}},  # 响应格式为json_object
)

# 提取结构
extract_schema = {
    "user_name": "用户名，没有返回空字符串''",
    "preference": {"language": "zh", "style": "正式", "如果没有偏好返回": "{}"},
    "facts": ["用户喜欢喝茶", "用户喜欢运动", "没有则返回空列表[]"]
}

extract_schema_json = json.dumps(extract_schema, ensure_ascii=False)


# ----------------------------- 定义状态 -----------------------------

class ChatState(TypedDict):
    # 消息列表
    messages: Annotated[list, add_messages]

    # 用户名
    user_name: str
    # 用户偏好
    preference: Annotated[dict[str, str], lambda old, new: {**old, **new}]
    # 用户事实
    facts: Annotated[list, lambda old, new: old + new]

    # 用户输入
    input: str


# ----------------------------- 定义节点 -----------------------------


def get_message(state: ChatState) -> dict:
    """
    获取用户消息
    :param state: 状态
    :return: 用户消息
    """

    # 从标准输入流获取用户输入
    input_ = input("请输入：")
    return {"messages": [], "input": input_}


def chat(state: ChatState) -> dict:
    """
    聊天流程
    :param state: 状态
    :return:
    """

    input_ = state.get("input", "")
    if not input_:
        raise ValueError("用户输入不能为空")

    # 获取历史消息
    messages = state.get("messages",[])

    # 获取用户信息
    user_name = state.get("user_name","")
    preference = state.get("preference",{})
    facts = state.get("facts",[])

    # 格式化系统提示
    system_prompt = """
    你是一个个性化聊天助手，你的任务是根据用户偏好和事实，回答用户的问题。
    用户名：%s
    偏好：%s
    事实：%s
    以json格式回复
    """
    system_prompt = system_prompt % (
        user_name if user_name else "用户",
        preference if preference else "暂无",
        facts if facts else "暂无")

    # 替换系统提示消息
    if len(messages) == 0:
        messages.append({"role": "system", "content": system_prompt})
    else:
        # 删除旧的系统提示消息
        messages.pop(0)
        # 插入系统提示消息到最前面
        messages.insert(0, {"role": "system", "content": system_prompt})
    # 添加用户消息
    messages.append({"role": "user", "content": input_})

    response = client.invoke(messages)

    # 更新状态
    return {"messages": [{"role": "assistant", "content": response.content}]}


def extract_user_info(state: ChatState) -> dict:
    """
    从历史消息中提取用户事实与偏好
    :param state: 状态
    :return:
    """

    # 获取最后两条历史消息
    messages = state.get("messages",[])
    last_message = messages[-2:]

    # 构建提示词
    system = f"""
    你是一个信息提取专家，你的任务是根据聊天记录，提取用户相关信息。
    以json格式回复，响应格式：
    {extract_schema_json}
"""

    prompt = f"""
    从以下聊天记录中提取用户名、偏好和事实：
    role:user, content:{last_message[0].content}
    role:assistant, content:{last_message[1].content}
    """

    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    # 调用模型
    response = client.invoke(messages)
    # 解析模型响应
    try:
        data = json.loads(response.content)
        return data
    except json.JSONDecodeError:
        logger.error("模型响应不是有效的JSON格式")
        return {"role": "assistant", "content": "模型响应不是有效的JSON格式"}


# ----------------------------- 定义流程 -----------------------------

graph = StateGraph(ChatState)
graph.add_node("get_message", get_message)
graph.add_node("chat", chat)
graph.add_node("extract_user_info", extract_user_info)
graph.add_edge(START, "get_message")
graph.add_edge("get_message", "chat")
graph.add_edge("chat", "extract_user_info")
graph.add_edge("extract_user_info", END)

# 创建保存器
thread_id = "thread_4"
connect = sqlite3.connect(f"data/session_history/{thread_id}.db", check_same_thread=False)
saver = SqliteSaver(connect)

# 编译
app = graph.compile(checkpointer=saver)

# 执行
response = app.invoke(
    {},
    config={"configurable": {"thread_id": thread_id}},
)
print(f"执行结果：{response}")
