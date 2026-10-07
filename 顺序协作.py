
# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal,Annotated
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver





# ----------------------------- 定义状态 -----------------------------
class DocumentState(TypedDict):
    raw_text: str
    cleaned_content: str
    summary: str
    keywords: Annotated[list[str], lambda old,new:old+new]


# ----------------------------- 定义节点 -----------------------------

def clean(state: DocumentState) -> dict[str, str]:
    """
    清理文档内容
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行清理文档内容")
    return {"cleaned_content": state.get("raw_text", "")}


def summary(state: DocumentState) -> dict[str, str]:
    """
    生成文档摘要
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行生成文档摘要")
    return {"summary": state.get("cleaned_content", "")}


def get_keywords(state: DocumentState) -> dict[str, list[str]]:
    """
    获取文档关键词
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("执行获取文档关键词")
    return {"keywords": ["keyword1", "keyword2", "keyword3"]}

# ----------------------------- 定义图 -----------------------------

graph = StateGraph(DocumentState)

graph.add_node("clean", clean)
graph.add_node("summary", summary)
graph.add_node("keywords", get_keywords)


graph.add_edge(START, "clean")
graph.add_edge("clean", "summary")
graph.add_edge("summary", "keywords")
graph.add_edge("keywords", END)



graph_compile = graph.compile()

# ----------------------------- 执行 -----------------------------

result = graph_compile.invoke({"raw_text": "这是一个测试文档"})
print(f"最终结果：{result}")








