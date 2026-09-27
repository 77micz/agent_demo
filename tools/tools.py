
# 导入json
import inspect
import json
from typing import Callable, Any, get_type_hints, get_origin, get_args
import typing
from loguru import logger



__all__ = [
    "cal_int",
    "person_list",
    "get_tool_schema",
    "get_all",
    "TOOLS",
]








# ----------------------------- 工具函数 -----------------------------



def cal_int(a: int, b: int) -> int:
    """
    计算两个整数的和
    :param a: 整数a
    :param b: 整数b
    :return: a+b
    """
    return int(a) + int(b)



def person_list(name: str) -> str:
    """
    获取城市的人员列表
    :param name: 姓名
    :return: 人员列表
    """
    fake_person = {
        "小明": "23岁，住在上海",
        "小红": "22岁，住在北京",
        "小绿": "21岁，住在广州",
        "小蓝": "20岁，住在深圳",
    }

    return fake_person.get(name, "未知")


# ----------------------------- 全局变量 -----------------------------
TOOLS:list[Callable] = [
    cal_int,
    person_list,
]


def get_tool_schema(function: Callable) -> str:
    """
    获取工具的schema
    :param function: 工具函数
    :return: 工具的schema
    """
    # 获取函数的参数以及类型
    sig = inspect.signature(function)
    logger.info(sig)
    # 获取函数的参数类型提示
    hints = get_type_hints(function)
    logger.info(hints)

    param_types = {}
    for name, p in sig.parameters.items():
        tp = hints.get(name, str)
        json_type = {int: "integer", float: "number", str: "string",
                     bool: "boolean", list: "array", dict: "object"}.get(tp, "string")
        param_types[name] = {"type": json_type}

    schema = {
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": function.__doc__,
            "parameters": {
                "type": "object",
                "properties": param_types,
                "required": [n for n, p in sig.parameters.items()
                             if p.default is inspect.Parameter.empty],
            },
        },
    }
    return json.dumps(schema, ensure_ascii=False)



def get_all():
    """
    获取所有工具的schema
    :return: 所有工具的schema
    """

    schema = [get_tool_schema(tool) for tool in TOOLS]
    return json.dumps(schema, ensure_ascii=False)



# ---------------------------- 测试 ----------------------------
if __name__ == "__main__":
    get_tool_schema(cal_int)




