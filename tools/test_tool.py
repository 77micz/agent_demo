# 导入json
import inspect
import json
from typing import Callable, Any, get_type_hints, get_origin, get_args
import typing
from loguru import logger
import uuid
import os
from pathlib import Path
import re
import tempfile
import subprocess
import importlib.util

__all__ = [
    "test_code",
    "get_tool_schema",
    "get_all",
    "TOOLS",
    "compile_to_functions",
    "save_llm_code",
    "remove_function_def_from_params",
]


# ----------------------------- 工具函数 -----------------------------


def compile_to_functions(code_str: str) -> dict:
    """编译代码,返回 {函数名: 函数对象};临时文件自动清理"""
    # 去除python标识
    code_str = re.sub(r"```python(.*)```", r"\1", code_str, flags=re.DOTALL)

    with tempfile.TemporaryDirectory() as d:
        module_name = f"llm_code_{uuid.uuid4().hex[:8]}"
        py_path = Path(d) / f"{module_name}.py"
        py_path.write_text(code_str, encoding="utf-8")

        spec = importlib.util.spec_from_file_location(module_name, py_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        funcs = {
            name: obj
            for name, obj in inspect.getmembers(module, inspect.isfunction)
            if obj.__module__ == module_name
        }
        logger.info(f"编译函数成功：{funcs}")
    # 出 with,目录自动删;函数对象已经在内存里了,调用不受影响
    return funcs


def test_code(code: Callable[[str], str]) -> dict[str, Any]:
    """
    反转字符串测试函数
    :param code: 反转字符串函数
    :return: 测试结果
    """

    # 测试用例

    try:
        assert code("hello") == "olleh", "测试用例'hello'失败"
        assert code("w") == "w", "测试用例'w'失败"
        assert code("") == "", "测试用例''失败"
        assert code("123") == "321", "测试用例'123'失败"
        logger.info("测试通过")

        return {"result": "success", "message": "测试通过"}
    except Exception as e:
        logger.error(e)
        return {"result": "error", "message": str(e)}


def save_llm_code(code: str) -> None:
    """
    保存大模型输出的代码块到文件
    :param code: 大模型输出的代码块
    :return: 保存结果
    """

    # 检查代码目录是否存在，不存在创建
    # 在项目根目录下创建code目录
    root = Path(__file__).resolve().parent.parent
    code_path = root / "llm_code"
    os.makedirs(code_path, exist_ok=True)
    code_file = code_path / f"{uuid.uuid4().hex}.py"

    # 保存代码到文件
    logger.info(f"把代码保存到文件: {code_file}")

    # 去除python标识
    code = re.sub(r"```python(.*)```", r"\1", code, flags=re.DOTALL)

    with open(code_file, "w", encoding="utf-8") as f:
        f.write(code)
    f.write("\n")


def remove_function_def(func: str) -> str:
    """
    从代码中移除函数定义
    :param func: 函数定义
    :return: 移除函数定义后的代码
    """

    # 检查是否有函数定义部分
    if not re.search(r"def \w+\(.*?\).*", func, flags=re.DOTALL):
        return func

    return re.sub(r"def (\w+)\(.*?\).*", r"\1", func, flags=re.DOTALL)


def remove_function_def_from_params(params: dict[str, Any], funcs: dict[str, Any]) -> dict[str, Any]:
    """
    从参数字典中移除所有函数定义
    :param params: 参数字典
    :param funcs: 函数字典
    :return: 移除所有函数定义后的参数字典
    """
    # 返回一个新的字典，不修改原字典
    params_use_callable = {}

    # 遍历参数字典，移除所有函数定义
    for key, value in params.items():
        # 如果是字符串，移除函数定义
        if isinstance(value, str):
            func_name = remove_function_def(value)
            if func_name in funcs:
                # 是函数，修改类型为callable对象
                params_use_callable[key] = funcs[func_name]
            else:
                # 不是函数，保持原本类型
                params_use_callable[key] = value
        # 其他类型直接赋值
        else:
            params_use_callable[key] = value
    return params_use_callable


# ----------------------------- 全局变量 -----------------------------
TOOLS: list[Callable] = [
    test_code,
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
