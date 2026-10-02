

# 导入langgraph
from langgraph.graph import StateGraph,START,END
# 导入TypeDict
from typing import TypedDict,Literal



# 定义状态
class WeatherState(TypedDict):
    temp: int # 温度
    recommend: str # 推荐的活动


# 定义节点
def check_temp(state:WeatherState) -> dict[str, int]:
    """
    查询温度
    :param state: 状态
    :return:
    """
    # 查询温度
    return {"temp": 25}


def route_by_temp(state:WeatherState) -> Literal["cold","warm","hot"]:
    """
    根据温度推荐活动
    :param state: 状态
    :return:
    """
    temp = state["temp"]
    if temp < 18:
        return "cold"
    elif temp < 25:
        return "warm"
    else:
        return "hot"


def cold(state:WeatherState) -> dict[str, str]:
    """
    冷天推荐活动
    :param state: 状态
    :return:
    """
    return {"recommend": "运动"}


def warm(state:WeatherState) -> dict[str, str]:

    """
    温天推荐活动
    :param state: 状态
    :return:
    """
    return {"recommend": "健身"}




def hot(state:WeatherState) -> dict[str, str]:
    """
    热天推荐活动
    :param state: 状态
    :return:
    """
    return {"recommend": "休息"}


# 定义图
graph = StateGraph(WeatherState)
# 添加节点
graph.add_node("check_temp",check_temp)
graph.add_node("route_by_temp",route_by_temp)
graph.add_node("cold",cold)
graph.add_node("warm",warm)
graph.add_node("hot",hot)
# 添加边
graph.add_edge(START,"check_temp")
# 添加条件分支
graph.add_conditional_edges(
    "check_temp",
    route_by_temp,
    {
        "cold": "cold",
        "warm": "warm",
        "hot": "hot"
    }
)

for node in ["cold","warm","hot"]:
    graph.add_edge(node,END)


# 编译图
graph_compile = graph.compile()


# 执行图
result = graph_compile.invoke({})
print(result)










