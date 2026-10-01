# 导入api请求库
import requests
from pathlib import Path
# 导入pandas
import pandas as pd
from loguru import logger
from langchain_core.tools import tool
import json

# 城市编码文件路径
file_path = Path(__file__).resolve().parent / "data/天气预报查询_国内城市_3387站 - Sheet1.csv"

# 使用pd读取.csv文件
city_df = pd.read_csv(file_path, encoding="utf-8")


## 天气查询
@tool(description="根据城市名称查询城市的天气")
def get_weather(city: str) -> str:
    """
    根据城市名称查询城市的天气
    :param city: 城市名称
    :return: 天气信息
    """
    url = "https://eolink.o.apispace.com/456456/weather/v001/now"

    # 获取城市编码
    city_code = get_city_code(city)
    payload = {"areacode": city_code}

    headers = {
        "X-APISpace-Token": "vdliyekjl67sokjrjg9iumlyvzz1gw37"
    }

    response = requests.get(url, params=payload, headers=headers)
    # 提取温度和天气信息，返回json
    data = {}
    json_response = response.json()
    data["temp"]=json_response.get("result").get("realtime").get("temp")
    data["weather"]=json_response.get("result").get("realtime").get("text")

    # 转为json字符串
    return json.dumps(data, ensure_ascii=False)


# 获取城市id
def get_city_code(city: str) -> str:
    """
    根据城市名称获取城市的编码
    优先精确查询district列，再city列，最后province列；
    精确未找到则进行模糊匹配（数据列包含输入的城市名）；
    都没找到默认返回北京的编码。
    :param city: 城市名称
    :return: 城市编码
    """
    # 定义查询列顺序
    columns = ["district", "city", "province"]

    for col in columns:
        # 1. 精确匹配
        exact_match = city_df[city_df[col] == city]
        if not exact_match.empty:
            code = exact_match["areacode/城市ID"].values[0]
            logger.info(f"根据{col}列精确查询到城市编码：{code}")
            return code

        # 2. 模糊匹配：数据列包含输入的城市名
        # na=False 忽略空值，避免报错
        fuzzy_match = city_df[city_df[col].str.contains(city, na=False)]
        if not fuzzy_match.empty:
            code = fuzzy_match["areacode/城市ID"].values[0]
            matched_name = fuzzy_match[col].values[0]
            logger.info(f"根据{col}列模糊查询到城市编码：{code}（匹配到：{matched_name}）")
            return code

    # 3. 都没找到，返回默认北京编码
    logger.warning(f"未找到城市 {city} 的编码，返回默认北京编码：101010100")
    return "101010100"







