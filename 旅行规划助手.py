# ----------------------------- 导入依赖 -----------------------------
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver



# ----------------------------- 主图 -----------------------------
class TravelState(TypedDict):
    # 旅行规划状态
    destination: str
    source: str
    begin_date: str
    end_date: str
    number_of_people: int
    budget: float

    # 中间结果
    flight_plan: dict
    hotel_plan: dict
    activity_plan: dict

    # 结果
    final_plan: str
    final_cost: float


# ----------------------------- 子图 -----------------------------


class FlightState(TypedDict):
    destination: str
    source: str
    begin_date: str
    end_date: str
    number_of_people: int
    budget: float
    plan_list: Annotated[list, lambda old, new: old + new]
    flight_plan: dict


class HotelState(TypedDict):
    destination: str
    source: str
    begin_date: str
    end_date: str
    number_of_people: int
    budget: float
    plan_list: Annotated[list, lambda old, new: old + new]
    hotel_plan: dict


class ActivityState(TypedDict):
    destination: str
    source: str
    begin_date: str
    end_date: str
    number_of_people: int
    budget: float
    plan_list: Annotated[list, lambda old, new: old + new]
    activity_plan: dict


# ----------------------------- 子图节点 -----------------------------

def search_flight(state: FlightState) -> dict[str, list[str]]:
    """
    搜索航班
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("正在搜索航班")
    return {"plan_list": ["根据条件搜索到的航班计划1", "根据条件搜索到的航班计划2"]}


def search_hotel(state: HotelState) -> dict[str, list[str]]:
    """
    搜索酒店
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("正在搜索酒店")
    return {"plan_list": ["根据条件搜索到的酒店计划1", "根据条件搜索到的酒店计划2"]}


def search_activity(state: ActivityState) -> dict[str, list[str]]:
    """
    搜索活动
    :param state: 文档状态
    :return: 更新 state
    """
    logger.info("正在搜索活动")
    return {"plan_list": ["根据条件搜索到的活动计划1", "根据条件搜索到的活动计划2"]}


def recommend_flight(state: FlightState) -> dict[str, str]:
    """
    推荐航班计划
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("agent推荐航班计划")
    return {"flight_plan": "根据推荐的航班计划1"}


def recommend_hotel(state: HotelState) -> dict[str, str]:
    """
    推荐酒店计划
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("agent推荐酒店计划")
    return {"hotel_plan": "根据推荐的酒店计划1"}


def recommend_activity(state: ActivityState) -> dict[str, str]:
    """
    推荐活动计划
    :param state: 文档状态
    :return: 更新 state
    """

    logger.info("agent推荐活动计划")
    return {"activity_plan": "根据推荐的活动计划1"}


# ----------------------------- 编译子图 -----------------------------

flight_graph = StateGraph(FlightState)

flight_graph.add_node("search_flight", search_flight)
flight_graph.add_node("recommend_flight", recommend_flight)

flight_graph.add_edge(START, "search_flight")
flight_graph.add_edge("search_flight", "recommend_flight")
flight_graph.add_edge("recommend_flight", END)

flight_config = {
    "configurable": {
        "thread_id": "flight",
    }
}
flight_saver = MemorySaver()
flight_graph_compile = flight_graph.compile(checkpointer=flight_saver)

hotel_graph = StateGraph(HotelState)

hotel_graph.add_node("search_hotel", search_hotel)
hotel_graph.add_node("recommend_hotel", recommend_hotel)

hotel_graph.add_edge(START, "search_hotel")
hotel_graph.add_edge("search_hotel", "recommend_hotel")
hotel_graph.add_edge("recommend_hotel", END)

hotel_config = {
    "configurable": {
        "thread_id": "hotel",
    }
}
hotel_saver = MemorySaver()
hotel_graph_compile = hotel_graph.compile(checkpointer=hotel_saver)

activity_graph = StateGraph(ActivityState)

activity_graph.add_node("search_activity", search_activity)
activity_graph.add_node("recommend_activity", recommend_activity)

activity_graph.add_edge(START, "search_activity")
activity_graph.add_edge("search_activity", "recommend_activity")
activity_graph.add_edge("recommend_activity", END)

activity_config = {
    "configurable": {
        "thread_id": "activity",
    }
}
activity_saver = MemorySaver()
activity_graph_compile = activity_graph.compile(checkpointer=activity_saver)


# ----------------------------- 主图节点 -----------------------------


def call_flight(state: TravelState) -> dict[str, list[str]]:
    """
    调用航班计划
    :param state: 航班状态
    :return: 更新 state
    """

    logger.info("正在调用航班计划")
    result = flight_graph_compile.invoke(
        {
            "destination": state["destination"],
            "source": state["source"],
            "begin_date": state["begin_date"],
            "end_date": state["end_date"],
            "number_of_people": state["number_of_people"],
            "budget": state["budget"],
        },
        config=flight_config
    )

    return {"flight_plan": result}


def call_hotel(state: TravelState) -> dict[str, list[str]]:
    """
    调用酒店计划
    :param state: 酒店状态
    :return: 更新 state
    """

    logger.info("正在调用酒店计划")
    result = hotel_graph_compile.invoke(
        {
            "destination": state["destination"],
            "source": state["source"],
            "begin_date": state["begin_date"],
            "end_date": state["end_date"],
            "number_of_people": state["number_of_people"],
            "budget": state["budget"],
        },
        config=hotel_config
    )

    return {"hotel_plan": result}


def call_activity(state: TravelState) -> dict[str, list[str]]:
    """
    调用活动计划
    :param state: 活动状态
    :return: 更新 state
    """

    logger.info("正在调用活动计划")
    result = activity_graph_compile.invoke(
        {
            "destination": state["destination"],
            "source": state["source"],
            "begin_date": state["begin_date"],
            "end_date": state["end_date"],
            "number_of_people": state["number_of_people"],
            "budget": state["budget"],
        },
        config=activity_config
    )

    return {"activity_plan": result}


def generate_plan(state: TravelState) -> dict[str, str | int]:
    """
    生成旅行计划
    :param state: 旅行状态
    :return: 更新 state
    """

    logger.info("agent根据推荐的航班、酒店、活动计划生成旅行计划")
    return {"final_plan": "根据推荐的航班、酒店、活动计划生成旅行计划", "final_cost": 2}


# ----------------------------- 编译主图 -----------------------------

main_graph = StateGraph(TravelState)

main_graph.add_node("call_flight", call_flight)
main_graph.add_node("call_hotel", call_hotel)
main_graph.add_node("call_activity", call_activity)
main_graph.add_node("generate_plan", generate_plan)

main_graph.add_edge(START, "call_flight")
main_graph.add_edge(START, "call_hotel")
main_graph.add_edge(START, "call_activity")
main_graph.add_edge("call_flight", "generate_plan")
main_graph.add_edge("call_hotel", "generate_plan")
main_graph.add_edge("call_activity", "generate_plan")
main_graph.add_edge("generate_plan", END)

main_config = {
    "configurable": {
        "thread_id": "main",
    }
}
main_saver = MemorySaver()
main_graph_compile = main_graph.compile(checkpointer=main_saver)

# ----------------------------- 执行 -----------------------------

result = main_graph_compile.invoke(
    {
        "destination": "北京",
        "source": "上海",
        "begin_date": "2023-01-01",
        "end_date": "2023-01-05",
        "number_of_people": 2,
        "budget": 1000,
    },
    config=main_config
)

logger.info(f"旅行规划：{result}")
