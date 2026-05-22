"""
配置模块：城市编码、请求头、延时参数等集中管理
"""

CITIES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "成都": "101270101",
    "杭州": "101210101",
    "武汉": "101200101",
    "南京": "101190101",
    "重庆": "101040100",
    "西安": "101110101",
}

BASE_URL_7D = "https://www.weather.com.cn/weather/{city_code}.shtml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.weather.com.cn/",
}

REQUEST_DELAY_MIN = 2
REQUEST_DELAY_MAX = 5

REQUEST_TIMEOUT = 15

MAX_RETRIES = 3

OUTPUT_DIR = "output"

ENCODING = "utf-8"
