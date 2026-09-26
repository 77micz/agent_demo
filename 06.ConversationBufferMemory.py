


# ----------------------------- 导入依赖 -----------------------------
from langchain_core.runnables import RunnableConfig
# 导入模型
from langchain_openai import ChatOpenAI
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
# 导入会话记忆
from langchain_core.chat_history import InMemoryChatMessageHistory
# 导入记忆管理
from langchain_core.runnables.history import RunnableWithMessageHistory

# ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10000,  # 超时时间，单位毫秒，默认10000秒，10秒超时
)



# 提示词模板
template = """
{question}
"""


# 创建提示词模板实例
prompt = PromptTemplate(
    template=template,  # 提示词模板
    input_variables=["question"],  # 输入变量
)

# 创建记忆管理，根据会话id存储记忆
store={}


def get_history(session_id: str):
    """
    获取会话记忆
    :param session_id: 会话id
    :return: 会话记忆
    """
    if session_id not in store:
        # 如果会话id不存在，创建一个新的会话记忆
        logger.info(f"创建会话记忆: {session_id}")
        store[session_id] = InMemoryChatMessageHistory()

    return store[session_id]



def get_session_id():
    """
    获取会话id
    :return: 会话id
    """
    # 根据当前时间生成会话id，格式：YYYY_MM_DD HH:MM:SS
    from datetime import datetime
    return datetime.now().strftime("%Y_%m_%d_%H:%M:%S")




# 管理会话记忆
chat_with_history = RunnableWithMessageHistory(
    runnable=client, # 调用模型客户端
    get_session_history=get_history, # 获取会话记忆
)


# 会话id
session_id = get_session_id()

# 调用模型客户端
chat_with_history.invoke(
    {"question": "你好我叫张三"},
    config=RunnableConfig(configurable={"enable_thinking": False, "session_id": session_id}),  # 关闭思考，指定会话id为当前时间戳
)

response = chat_with_history.invoke(
    {"question": "我的名字是什么？"},
    config=RunnableConfig(configurable={"enable_thinking": False, "session_id": session_id}),  # 关闭思考，指定会话id为当前时间戳
)

logger.info(response.content)





