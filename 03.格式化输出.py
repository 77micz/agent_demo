
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
from pydantic import BaseModel,Field


# ----------------------------- 初始化 -----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=10000,  # 超时时间，单位毫秒，默认10000秒，10秒超时
)

# 创建数据模型
class Data(BaseModel):
    name:str = Field(description="姓名")
    age:int = Field(description="年龄")

# 提示词模板
template = """
你是一个数据提取助手，你的任务是从用户的问题中提取数据。
用户问题：{input}
{data_structure}
"""

# 解析器实例
output_parser = PydanticOutputParser(
    pydantic_object=Data, # 解析器输出的模型
)


# 创建提示词模板实例
prompt = PromptTemplate(
    template=template, # 提示词模板
    input_variables=["input"], # 输入变量
    partial_variables={"data_structure":output_parser.get_format_instructions() if output_parser else ""}, # 部分变量
)



# 调用模型客户端
response = client.invoke(
    prompt.format(input="小王今年20岁，住在上海"), # prompt
    config=RunnableConfig(configurable={"enable_thinking": False}), # 关闭思考
)


# 解析响应
data = output_parser.parse(response.content)
# 输出解析结果
logger.info(data)







