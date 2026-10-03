# ----------------------------- 导入依赖 -----------------------------
import json

from langchain_core.runnables import RunnableConfig
# 导入模型
from langchain_openai import ChatOpenAI
# 导入消息
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
# 导入os
import os
# 导入日志类
from loguru import logger
# 导入提示词模板
from langchain_core.prompts import PromptTemplate
# 导入输出解析器
from langchain_core.output_parsers import PydanticOutputParser
# 导入数据模型和属性
from pydantic import BaseModel, Field
# 导入工具
from tools.ReAct_tools import *

## ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10,  # 超时时间，单位秒，默认10秒，10秒超时
    max_retries=3,  # 最大重试次数，默认3次
    model_kwargs={"response_format": {"type": "json_object"}}, # 响应格式为json_object
)

client_bind = client.bind(
    extra_body={"enable_thinking": False},  # 关闭思考
)

# 响应格式
response_format = {
    "tool_call": [
        {
            "type": "function",
            "function": {
                "name": "工具函数名",
                "params": {
                    "形参1": "实参1",
                    "形参2": "实参2"
                }
            }
        }
    ],
    "response": "响应内容"
}

# 工具调用结果格式
result_format = {
    "tool_call_results": [
        {
            "name": "工具函数名",
            "params": {
                "形参1": "实参1",
                "形参2": "实参2"
            },
            "result": "工具调用结果"
        }
    ]
}

# 最大循环次数
MAX_LOOP = 10


# ----------------------------- 工具调用结果解析 -----------------------------

# 工具函数映射
TOOL_MAP = {f.__name__: f for f in TOOLS}

def get_tool_result(tools):
    """
    解析工具调用结果
    :param tools: 工具列表
    :return: 工具调用结果
    """
    result_list = []
    for tool in tools:
        func = tool["function"]
        name = func["name"]
        params = func.get("params", {}) or {}
        fn = TOOL_MAP.get(name)
        result = fn(**params) if fn else f"未知工具:{name}"
        result_list.append({"name": name, "params": params, "result": result})
    return result_list


# ----------------------------- 流程 -----------------------------


def agent_loop(task: str) -> str:
    """
    智能体循环流程
    :param task: 任务
    :return: 任务结果
    """

    # 初始化消息列表
    messages = [
        SystemMessage(
            content=f"你是一个智能体，你的任务是根据用户的问题，调用工具函数，完成任务。以json格式返回响应，响应格式:{response_format}；工具:{get_all()}"),
        HumanMessage(content=task),
    ]

    # 初始化循环次数
    loop_count = 0

    # agent循环
    while True:
        # 检查循环次数是否超过最大循环次数
        if loop_count > MAX_LOOP:
            return "循环次数超过最大循环次数"

        # 请求大模型
        response = client.invoke(
            input=messages,  # 输入任务
            config=RunnableConfig(configurable={"enable_thinking": False}),  # 关闭思考
        )

        # 记录模型完整回复
        logger.info(f"模型回复：{response}")

        # json转为dict
        response_dict = json.loads(response.content)

        # 获取工具请求
        tool_calls = response_dict.get("tool_call", None)

        # 记录日志
        logger.info(tool_calls)

        # 检查工具请求
        if tool_calls:
            # 提取工具请求参数
            tools = tool_calls
            # 调用工具函数获取结果
            tool_results = get_tool_result(tools)
            # 加入消息列表
            messages.append(SystemMessage(content=json.dumps({"tool_call_results": tool_results}, ensure_ascii=False)))
        else:
            return response_dict["response"]
        loop_count += 1


# ----------------------------- 测试 -----------------------------
if __name__ == "__main__":
    logger.info(agent_loop("小明多少岁"))
