
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, Any
from loguru import logger
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
import os
import json
import sqlite3







# ----------------------------- 全局配置 ----------------------------

# 创建大模型客户端
client = ChatOpenAI(
    model="deepseek-v4.1-flash",  # 使用的模型名称
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # your_api_key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # api路径
    timeout=120,  # 超时时间，单位秒，默认120秒，120秒超时
    max_retries=3,  # 最大重试次数，默认3次，3次重试
    model_kwargs={"response_format": {"type": "json_object"}},  # 响应格式为json_object
)


connection=sqlite3.connect("data/session_history/content_review.db",check_same_thread=False)




# ----------------------------- 定义状态 -----------------------------
class ContentReview(TypedDict):
    # 1.内容
    content: str # 审核内容
    content_id: str # 内容ID
    content_type: str # 内容类型
    # 2.审核指标
    toxicity: float # 毒性指标
    spam: float # 垃圾内容指标
    quality: float # 内容质量指标
    # 3.审核结果
    final_decision: str # 最终审核决策 approve/reject/flag
    review_records: Annotated[list,lambda old,new:old+new] # 审核记录



# ----------------------------- 定义节点 -----------------------------

def analyze_toxicity(state: ContentReview) -> dict[str, float]:
    """
    分析内容毒度指标
    :param state: 审核状态
    :return: 更新 state
    """

#     system_prompt = """
# 你是一个专业的内容审核助手，负责分析内容的毒度指标。
# 以JSON格式返回指标值。范围：0.0-1.0
# 响应格式:{
#     "toxicity": 0.5,
# }
#     """
#
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"请分析以下内容的毒度指标：{state.get('content')}"},
#     ]
#
#
#     # 调用大模型分析内容毒度指标
#     response = client.invoke(
#         input=messages,  # 输入任务
#     )
#
#     # 解析响应
#     content = json.loads(response.content)
#
#     logger.info(f"毒度指标：{content}")

    return {"toxicity": 0.4}


def analyze_spam(state: ContentReview) -> dict[str, float]:
    """
    分析垃圾内容指标
    :param state: 审核状态
    :return: 更新 state
    """

#     system_prompt = """
# 你是一个专业的内容审核助手，负责分析内容的垃圾内容指标。
# 以JSON格式返回指标值。范围：0.0-1.0
# 响应格式:{
#     "spam": 0.5,
# }
#     """
#
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"请分析以下内容的垃圾内容指标：{state.get('content')}"},
#     ]
#
#     # 调用大模型分析垃圾内容指标
#     response = client.invoke(
#         input=messages,  # 输入任务
#     )
#
#     # 解析响应
#     content = json.loads(response.content)
#
#     logger.info(f"垃圾内容指标：{content}")

    return {"spam": 0.4}


def analyze_quality(state: ContentReview) -> dict[str, float]:
    """
    分析内容质量指标
    :param state: 审核状态
    :return: 更新 state
    """

#     system_prompt = """
# 你是一个专业的内容审核助手，负责分析内容的质量指标。
# 以JSON格式返回指标值。范围：0.0-1.0
# 响应格式:{
#     "quality": 0.5,
# }
#     """
#
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"请分析以下内容的质量指标：{state.get('content')}"},
#     ]
#
#     # 调用大模型分析内容质量指标
#     response = client.invoke(
#         input=messages,  # 输入任务
#     )
#
#     # 解析响应
#     content = json.loads(response.content)
#
#     logger.info(f"质量分数：{content}")

    return {"quality": 0.7}


def llm_recommend(state: ContentReview) -> Literal["approve", "reject", "level1_review"]:
    """
    生成llm审核建议
    :param state: 审核状态
    :return: 更新 state
    """

    if state.get("toxicity") > 0.7 or state.get("spam") > 0.7:
        return "reject"
    elif state.get("quality") > 0.6 and state.get("spam") < 0.3 and state.get("toxicity") < 0.3:
        return "approve"
    else:
        return "level1_review"




def approve(state: ContentReview) -> dict[str, str]:
    """
    过审
    :param state:
    :return:
    """

    logger.info(f"\n内容：{state.get('content')} 已过审")

    return {"final_decision": "approve"}


def reject(state: ContentReview) -> dict[str, str]:
    """
    拒绝
    :param state:
    :return:
    """

    logger.info(f"\n内容：{state.get('content')} 已拒绝")

    return {"final_decision": "reject"}





def level1_review(state: ContentReview) -> dict[str, list[dict[str, str | Any]]]:
    """
    一级审核
    :param state:
    :return:
    """

    decision = interrupt(
        {
            "content": state.get("content"),
            "toxicity": state.get("toxicity"),
            "spam": state.get("spam"),
            "quality": state.get("quality"),
            "level": "1",
            "option": "approve/reject/level2_review",
        }
    )

    logger.info(f"\n内容：{state.get('content')} 一级审核完毕")

    return {"review_records": [{"level": "1", "decision": decision}]}


def level2_review(state: ContentReview) -> dict[str, list[dict[str, str | Any]]]:
    """
    二级审核
    :param state:
    :return:
    """

    decision = interrupt(
        {
            "content": state.get("content"),
            "toxicity": state.get("toxicity"),
            "spam": state.get("spam"),
            "quality": state.get("quality"),
            "level": "2",
            "option": "approve/reject/flag",
        }
    )

    logger.info(f"\n内容：{state.get('content')} 二级审核完毕")

    return {"review_records": [{"level": "2", "decision": decision}]}



def flag(state: ContentReview) -> dict[str, str]:
    """
    标记
    :param state:
    :return:
    """

    logger.info(f"\n内容：{state.get('content')} 已标记")

    return {"final_decision": "flag"}







# ----------------------------- 路由函数 -----------------------------


def route_after_level1(state: ContentReview) -> Literal["approve", "reject", "level2_review"]:
    """
    一级审核后的路由
    :param state:
    :return:
    """

    decision = state.get("review_records")[0].get("decision")

    if decision == "reject":
        return "reject"
    elif decision == "approve":
        return "approve"
    else:
        return "level2_review"


def route_after_level2(state: ContentReview) -> Literal["approve", "reject", "flag"]:
    """
    二级审核后的路由
    :param state:
    :return:
    """

    decision = state.get("review_records")[1].get("decision")

    if decision == "reject":
        return "reject"
    elif decision == "approve":
        return "approve"
    else:
        return "flag"




# ----------------------------- 定义图 -----------------------------

graph = StateGraph(ContentReview)


graph.add_node("level1_review", level1_review)
graph.add_node("level2_review", level2_review)
graph.add_node("approve", approve)
graph.add_node("reject", reject)
graph.add_node("flag", flag)
graph.add_node("analyze_quality", analyze_quality)
graph.add_node("analyze_spam", analyze_spam)
graph.add_node("analyze_toxicity", analyze_toxicity)



graph.add_edge(START, "analyze_toxicity")
graph.add_edge("analyze_toxicity","analyze_spam")
graph.add_edge("analyze_spam","analyze_quality",)
graph.add_conditional_edges(
    "analyze_quality",
    llm_recommend,
    {
        "approve": "approve",
        "reject": "reject",
        "level1_review": "level1_review",
    }
)

graph.add_conditional_edges(
    "level1_review",
    route_after_level1,
    {
        "reject": "reject",
        "level2_review": "level2_review",
        "approve": "approve",
    }
)

graph.add_conditional_edges(
    "level2_review",
    route_after_level2,
    {
        "reject": "reject",
        "flag": "flag",
        "approve": "approve",
    }
)

for node in ["approve", "reject", "flag"]:
    graph.add_edge(node, END)



saver=SqliteSaver(conn=connection)


graph_compile = graph.compile(checkpointer=saver)

# ----------------------------- 执行 -----------------------------

config={"configurable": {"thread_id": "content_review"}}

# 执行流式输出
input_data = {"content": "这是一条需要人工审核的内容"}

while True:
    # 每次启动 stream，遇到中断会暂停
    interrupted = False
    for chunk in graph_compile.stream(input_data, config=config, stream_mode="updates"):
        if "__interrupt__" in chunk:
            interrupted = True
            # 获取中断信息
            message = chunk["__interrupt__"][0].value
            logger.info(f"\n中断信息：{message}")
            # 获取用户输入
            decision = input("\n请输入中断决策：")
            # ✅ 用 Command(resume=...) 恢复执行，作为下一次 stream 的输入
            input_data = Command(resume=decision)
            break  # 跳出当前 stream，带着 Command 重新开始

    # 如果没有遇到中断，说明图执行完毕
    if not interrupted:
        logger.info(f"\n最终结果：{graph_compile.get_state(config=config).values}")
        break
