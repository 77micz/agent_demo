

# 导入langchain工具装饰器
from langchain_core.tools import tool










# 定义工具函数
@tool
def multiply(a: int, b: int) -> int:
    """
    两个整数的乘积
    :param a: 第一个整数
    :param b: 第二个整数
    :return: 两个整数的乘积
    """
    return a * b



# --------------------------- 测试
if __name__ == "__main__":
    # 打印schema
    print(multiply.args_schema.model_json_schema())














