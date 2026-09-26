

# ----------------------------- 导入依赖 -----------------------------
from langchain_core.runnables import RunnableConfig
# 导入模型
from langchain_openai import ChatOpenAI
# 导入os
import os
# 导入日志类
from loguru import logger
# 导入提示词模板
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
# 导入消息类型
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage

# ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10000,  # 超时时间，单位毫秒，默认10000秒，10秒超时
)


# 创建提示词模板
template = """
你是一个{role}，你的任务是解答用户的问题：{question}
"""

# 创建提示词模板实例
prompt = PromptTemplate.from_template(
    template=template, # 提示词模板
)

# 调用模型客户端
response = client.invoke(
    prompt.format(role="数学老师", question="勾股定理是什么"), # prompt
    config=RunnableConfig(configurable={"enable_thinking": False}), # 关闭思考
)

# 输出响应内容
logger.info(response.content)






