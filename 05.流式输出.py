
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
你是一个{role}，你的任务是解答问题:{question}
"""


# 创建提示词模板实例
prompt = PromptTemplate(
    template=template,  # 提示词模板
    input_variables=["role", "question"],  # 输入变量
)

# 链式调用
chain = prompt | client

# 流式输出
response = chain.stream(
    {"role": "数学老师", "question": "矩阵的四个基本子空间有什么关系"},
    config=RunnableConfig(configurable={"enable_thinking": False}), # 关闭思考
)

# 存储结果
res=""

for chunk in response:
    res+=chunk.content
    print(
        res,
        end="",  # 不换行
        flush=True,  # 刷新缓冲区，确保立即输出
    )
    # 清空输出缓冲区
    res=""
