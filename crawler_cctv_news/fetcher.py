"""
HTTP请求模块：负责向央视新闻发送请求，获取页面HTML内容

包含重试机制、请求延时、异常处理
"""

import logging
import random
import time

import requests

from crawler_cctv_news.config import (
    ENCODING,
    HEADERS,
    MAX_RETRIES,
    REQUEST_DELAY_MAX,
    REQUEST_DELAY_MIN,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


def _delay():
    """随机延时，规避高频访问限制"""
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    logger.debug("请求延时 %.2f 秒", delay)
    time.sleep(delay)


def fetch_page(url: str) -> str | None:
    """
    请求指定URL并返回HTML文本

    Args:
        url: 目标页面URL

    Returns:
        HTML文本内容，请求失败返回None
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if attempt > 1:
                _delay()
            logger.info("第 %d 次请求: %s", attempt, url)
            response = requests.get(
                url, headers=HEADERS, timeout=REQUEST_TIMEOUT
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
