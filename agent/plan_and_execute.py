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
from tools.plan_tools import *

# ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=120,  # 超时时间，单位秒，默认120秒，120秒超时
    max_retries=3,  # 最大重试次数，默认3次，3次重试
    model_kwargs={"response_format": {"type": "json_object"}},  # 响应格式为json_object
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
    ],  # 工具调用列表，每个元素是一个字典，包含工具函数名和参数
    "response": "响应内容",  # 响应内容
    "steps": ["步骤1描述", "步骤2描述", "如果不需要分步执行任务，steps:[]", "..."],  # 需要分步执行的任务拆成多个步骤，每个步骤是一个字符串用列表存储
    "is_completed": "是否已完成当前步骤，返回'是'或'否';没有步骤时默认'否'表示当前任务未完成",  # 是否已完成当前步骤
}

# 消息格式
message_format = {
    "tool_call_results": [
        {
            "name": "工具函数名",
            "params": {
                "形参1": "实参1",
                "形参2": "实参2"
            },
            "result": "工具调用结果"
        }
    ],  # 工具调用结果列表，每个元素是一个字典，包含工具函数名、参数和结果
    "current_step": "当前步骤描述，如果没有步骤时默认''，",  # 当前步骤
}

# 系统提示词
sys_prompt = f"""
你是一个智能体，你的任务是根据用户的问题，调用工具函数，完成任务。以json格式返回响应
你的响应格式:{response_format};
客户端的消息格式:{message_format};
工具:{get_all()};
"""

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
        SystemMessage(content=sys_prompt),
        HumanMessage(content=task),
    ]

    # 初始化循环次数
    loop_count = 0

    # 保存任务步骤
    steps = []

    # 当前任务索引
    index = 0

    # 记录当前任务是否分步
    flag = False

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
        logger.info(f"工具请求：{tool_calls}")

        # 初始化消息
        message = {}

        # 第一次循环检查是否有任务步骤
        if loop_count == 0 and response_dict.get("steps", None):
            # 标记为分步执行任务
            flag = True
            # 保存步骤
            steps = response_dict["steps"]
            logger.info(f"任务步骤：{steps}")
            # 提取第一个步骤
            message["current_step"] = steps[index] if steps else ""
            logger.info(f"当前步骤：{message['current_step']};当前步骤索引：{index}")

        # 检查当前步骤是否完成(第一次循环不检查)
        if flag and response_dict.get("is_completed", None) == '是' and loop_count != 0:
            logger.info(f"步骤：{steps[index]};已完成")
            # 更新当前步骤
            index += 1
            message["current_step"] = steps[index] if index < len(steps) else ""
            logger.info(f"当前步骤：{message['current_step']};当前步骤索引：{index}")
        elif flag:
            logger.info(f"步骤：{message['current_step']};正在执行")
            # 当前步骤未完成，继续循环
            pass
        else:
            # 未分步执行任务，当前步骤为空
            message["current_step"] = ""

        # 判断是否是有步骤任务
        if flag:
            # 检查是不是最后一步
            if index >= len(steps) - 1 and response_dict.get("is_completed", None) == '是':
                # 最后一步，返回结果
                return response_dict["response"]
            else:
                # 非最后一步，继续循环
                # 调用工具函数获取结果
                tool_results = get_tool_result(tool_calls)
                # 加入消息
                message["tool_call_results"] = tool_results
                # 加入消息列表
                messages.append(SystemMessage(content=json.dumps(message, ensure_ascii=False)))
        else:
            # 检查工具请求
            if tool_calls:
                # 调用工具函数获取结果
                tool_results = get_tool_result(tool_calls)
                # 加入消息
                message["tool_call_results"] = tool_results
                # 加入消息列表
                messages.append(SystemMessage(content=json.dumps(message, ensure_ascii=False)))
            else:
                return response_dict["response"]

        loop_count += 1


# ----------------------------- 测试 -----------------------------
if __name__ == "__main__":
    logger.info(agent_loop("今天东京天气怎么样，适合穿什么衣服"))
