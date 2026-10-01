
# 导入agent
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
# 导入模型
from langchain_openai import ChatOpenAI
# 导入os
import os

# 导入状态保存器
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

# 导入日志类
from loguru import logger
# 导入工具
from weather_tools import get_weather









# ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10000,  # 超时时间，单位毫秒，默认10000秒，10秒超时
)


# 创建agent
agent = create_agent(
    model=client, # 模型
    tools=[get_weather], # 工具列表
    system_prompt="你是一个智能体，你的任务是根据用户的问题判断是否需要调用工具，如果需要则调用工具函数。", # 系统提示
    checkpointer=InMemorySaver(), # 状态保存器
)




# 调用
response = agent.invoke(
    input=Command(update={"messages": [("user","深圳今天天气怎么样")]}), # 输入
    config=RunnableConfig(
        configurable={"thread_id": "123"}, # 线程id
    ), # 配置
)

# 打印响应
logger.info(response["messages"][-1].content)











