# ----------------------------- 导入依赖 -----------------------------
# 导入langgraph
from langgraph.graph import StateGraph, START, END
# 导入TypeDict
from typing import TypedDict, Literal
# 导入大模型
from langchain_openai import ChatOpenAI
import os
# 导入消息
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# 导入json
import json
from loguru import logger

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

analyze_schema = {
    "has_issues": "True/False",
    "issues": ['issue1', 'issue2', 'issue3'],
    "level": ['low', 'medium', 'high'],
    "confidence": "0.0-1.0",
}
# 分析结果json格式
analyze_schema_json = json.dumps(analyze_schema, ensure_ascii=False)

decision_schema = {
    "decision": ['agree', 'reject', 'human_review'],
    "reason": "string",
}

# 决策结果json格式
decision_schema_json = json.dumps(decision_schema, ensure_ascii=False)


# ----------------------------- graph核心定义 -----------------------------

# 定义评论状态
class CommentState(TypedDict):
    content: str  # 评论内容
    analyze: str  # 分析内容
    decision: Literal["agree", "reject", "human_review"]  # 决策结果
    reason: str  # 决策原因
    confidence: float  # 置信度


# 定义分析节点
def analyze(state: CommentState) -> dict[str, str]:
    """
    分析评论内容
    :param state: 评论状态
    :return: 分析结果
    """

    messages = [
        SystemMessage(content=f"你是一个内容审核智能体，你的任务是分析评论内容，判断是否违规。"
                              f"检查是否包含违规内容，如不当语言(辱骂，脏话)、垃圾信息(广告，刷屏)、敏感话题(政治，暴力，色情)等"
                              f"以json格式返回响应，响应格式:{analyze_schema_json}"),
        HumanMessage(content=state["content"]),
    ]

    # 调用大模型分析评论
    response = client.invoke(
        input=messages,  # 输入任务
    )

    logger.info(f"大模型回复: {response.content}")

    # 解析响应
    content = json.loads(response.content)

    return {"analyze": response.content, "confidence": content["confidence"]}


# 定义决策节点
def decision(state: CommentState) -> dict[str, str]:
    """
    决策评论内容
    :param state: 评论状态
    :return: 决策结果
    """


    messages = [
        SystemMessage(content=f"你是一个决策智能体，你的任务是根据评论分析结果，判断是否过审。"
                              f"以json格式返回响应，响应格式:{decision_schema_json}"),
        HumanMessage(content=state["analyze"]),
    ]

    # 调用大模型分析评论
    response = client.invoke(
        input=messages,  # 输入任务
    )

    # 解析响应
    content = json.loads(response.content)

    return {"decision": content["decision"], "reason": content["reason"]}


# 定义路由节点
def route_by_decision(state: CommentState) -> Literal["decision", "human_review"]:
    """
    根据决策结果路由评论
    :param state: 评论状态
    :return: 路由结果
    """

    analyze_content = json.loads(state["analyze"])
    if analyze_content["level"] == "high":
        return "human_review"
    else:
        return "decision"



# 定义人工审核节点
def human_review(state: CommentState) -> str:
    """
    人工审核评论内容
    :param state: 评论状态
    :return: 人工审核结果
    """

    return "human_review"



# 定义图
graph = StateGraph(CommentState)
# 添加节点
graph.add_node("analyze", analyze)
graph.add_node("decision", decision)
graph.add_node("route", route_by_decision)
graph.add_node("human_review", human_review)

# 添加边
graph.add_edge(START, "analyze")
graph.add_conditional_edges(
    "analyze",
    route_by_decision,
    {
        "decision": "decision",
        "human_review": "human_review",
    },
)
for node in ["decision", "human_review"]:
    graph.add_edge(node, END)

# 编译图
graph_compile = graph.compile()


# 执行图
result = graph_compile.invoke({"content": "这是一条正常评论"})
print(result)
