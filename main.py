"""
weatherEveryday - 中国天气网天气预报爬虫

功能：抓取指定城市的当日天气及未来三日预报，保存为CSV和JSON
仅做个人学习使用，不商用、不高频恶意请求
"""

import logging
import sys

from weather_scraper.config import CITIES
from weather_scraper.fetcher import _delay, fetch_city_weather
from weather_scraper.parser import parse_7d_forecast
from weather_scraper.storage import save_data


def setup_logging():
    """配置日志输出，兼容本地和GitHub Actions环境"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def crawl_all_cities() -> list[dict]:
    """
    爬取所有配置城市的天气数据

    Returns:
        天气数据列表
    """
    logger = logging.getLogger(__name__)
    all_data = []

    for city_name, city_code in CITIES.items():
        logger.info("=" * 50)
        logger.info("开始爬取: %s (编码: %s)", city_name, city_code)

        html = fetch_city_weather(city_code)
        if html is None:
            logger.error("获取页面失败，跳过: %s", city_name)
            continue

        data = parse_7d_forecast(html, city_name)
        if data is None:
            logger.error("解析页面失败，跳过: %s", city_name)
            continue

        all_data.append(data)

        _delay()

    logger.info("=" * 50)
    logger.info("爬取完成，共获取 %d / %d 个城市数据", len(all_data), len(CITIES))
    return all_data


def main():
    """主入口函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("weatherEveryday 爬虫启动")
    logger.info("目标城市: %s", "、".join(CITIES.keys()))

    all_data = crawl_all_cities()

    if not all_data:
        logger.error("未获取到任何天气数据，程序退出")
        sys.exit(1)

    csv_path, json_path = save_data(all_data)
    logger.info("数据已保存: CSV=%s, JSON=%s", csv_path, json_path)
    logger.info("weatherEveryday 爬虫运行结束")


if __name__ == "__main__":
    main()
