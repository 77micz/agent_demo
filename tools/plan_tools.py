# 导入json
import inspect
import json
from typing import Callable, Any, get_type_hints, get_origin, get_args
import typing
from loguru import logger

__all__ = [
    "get_weather",
    "get_tool_schema",
    "get_all",
    "TOOLS",
]


# ----------------------------- 工具函数 -----------------------------


def get_weather(name: str) -> str:
    """
    获取城市的天气
    :param name: 城市名称
    :return: 天气
    """

    fake_weather = {
        "东京": "气温30摄氏度，晴朗",
        "北京": "气温24摄氏度，阴云",
        "广州": "气温31摄氏度，晴朗",
        "深圳": "气温29摄氏度，晴朗",
    }
    return f"{name}的天气是{fake_weather.get(name, '未知')}"


# ----------------------------- 全局变量 -----------------------------
TOOLS: list[Callable] = [
    get_weather,
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


