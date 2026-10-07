
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal,Annotated
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class AnalyzeState(TypedDict):
    content: str
    topic_analysis: str
    semantic_analysis: str
    entity_analysis: str
    summary: str


# ----------------------------- 定义节点 -----------------------------

def analyze_topic(state: AnalyzeState) -> dict[str, str]:
    """
    分析文档主题
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行分析文档主题")
    return {"topic_analysis": "主题分析结果"}


def analyze_semantic(state: AnalyzeState) -> dict[str, str]:
    """
    分析文档语义
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行分析文档语义")
    return {"semantic_analysis": "语义分析结果"}


def analyze_entity(state: AnalyzeState) -> dict[str, str]:
    """
    分析文档实体
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行分析文档实体")
    return {"entity_analysis": "实体分析结果"}


def summary(state: AnalyzeState) -> dict[str, str]:
    """
    生成文档摘要
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("执行生成文档摘要")
    return {"summary": "摘要结果"}



# ----------------------------- 定义图 -----------------------------

graph = StateGraph(AnalyzeState)

graph.add_node("analyze_topic", analyze_topic)
graph.add_node("analyze_semantic", analyze_semantic)
graph.add_node("analyze_entity", analyze_entity)
graph.add_node("summary", summary)


graph.add_edge(START, "analyze_topic")
graph.add_edge(START, "analyze_semantic")
graph.add_edge(START, "analyze_entity")
graph.add_edge("analyze_topic", "summary")
graph.add_edge("analyze_semantic", "summary")
graph.add_edge("analyze_entity", "summary")
graph.add_edge("summary", END)



graph_compile = graph.compile()

# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({"raw_text": "这是一个测试文档"})
print(f"最终结果：{result}")








