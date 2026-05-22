"""
HTTP请求模块：负责向豆瓣发送请求，获取页面HTML内容

包含重试机制、请求延时、异常处理、随机bid cookie
桌面端榜单页 + 移动端详情页双通道请求
"""

import logging
import random
import string
import time

import requests

from crawler_douban.config import (
    ENCODING,
    HEADERS,
    MAX_RETRIES,
    MOBILE_HEADERS,
    REQUEST_DELAY_MAX,
    REQUEST_DELAY_MIN,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


def _generate_bid() -> str:
    """生成随机bid cookie值，豆瓣用此标识访客"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=11))


def _delay():
    """随机延时，规避高频访问限制"""
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    logger.debug("请求延时 %.2f 秒", delay)
    time.sleep(delay)


def fetch_page(url: str, use_mobile: bool = False) -> str | None:
    """
    请求指定URL并返回HTML文本

    采用重试机制，最多重试 MAX_RETRIES 次
    每次请求携带随机bid cookie，避免被豆瓣拦截

    Args:
        url: 目标页面URL
        use_mobile: 是否使用移动端请求头（详情页需用移动端绕过JS验证）

    Returns:
        HTML文本内容，请求失败返回None
    """
    base_headers = MOBILE_HEADERS if use_mobile else HEADERS
    headers = base_headers.copy()
    headers["Cookie"] = f"bid={_generate_bid()}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if attempt > 1:
                _delay()
            logger.info("第 %d 次请求: %s", attempt, url)
            response = requests.get(
                url, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            response.encoding = ENCODING
            logger.info("请求成功: %s (状态码 %d)", url, response.status_code)
            return response.text
        except requests.RequestException as e:
            logger.warning("第 %d 次请求失败: %s - %s", attempt, url, e)
            if attempt == MAX_RETRIES:
                logger.error("已达最大重试次数，放弃请求: %s", url)
                return None
    return None


def build_mobile_url(desktop_url: str) -> str:
    """
    将桌面端豆瓣电影URL转换为移动端URL

    桌面端详情页有JS反爬验证，移动端可直接访问

    Args:
        desktop_url: 桌面端URL，如 https://movie.douban.com/subject/xxx/

    Returns:
        移动端URL，如 https://m.douban.com/movie/subject/xxx/
    """
    return desktop_url.replace(
        "https://movie.douban.com/", "https://m.douban.com/movie/"
    )
