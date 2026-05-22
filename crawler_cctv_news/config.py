"""
配置模块：央视新闻爬虫相关参数集中管理
"""

BASE_URL = "https://news.cctv.com/"

LIST_URLS = [
    "https://news.cctv.com/china/",
    "https://news.cctv.com/world/",
    "https://news.cctv.com/society/",
]

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
    "Referer": "https://news.cctv.com/",
}

REQUEST_DELAY_MIN = 2
REQUEST_DELAY_MAX = 5

REQUEST_TIMEOUT = 15

MAX_RETRIES = 3

MAX_NEWS_COUNT = 20

OUTPUT_DIR = "output/crawler_cctv_news"

ENCODING = "utf-8"
