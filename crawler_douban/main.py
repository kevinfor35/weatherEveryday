"""
crawler_douban - 豆瓣影视热播榜单爬虫

功能：抓取豆瓣影视热播榜单，保存为CSV
仅做个人学习使用，不商用、不高频恶意请求
"""

import logging
import sys

from crawler_douban.config import CHART_URL, MAX_ITEMS
from crawler_douban.fetcher import _delay, build_mobile_url, fetch_page
from crawler_douban.parser import parse_chart_page, parse_detail_page
from crawler_douban.storage import save_data


def setup_logging():
    """配置日志输出，兼容本地和GitHub Actions环境"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def crawl_chart() -> list[dict]:
    """
    爬取豆瓣影视热播榜单

    先抓取桌面端榜单页面获取影片列表，
    再通过移动端详情页补充简介（桌面端有JS反爬验证）

    Returns:
        影片数据列表
    """
    logger = logging.getLogger(__name__)

    logger.info("开始获取豆瓣榜单页面: %s", CHART_URL)
    html = fetch_page(CHART_URL, use_mobile=False)
    if not html:
        logger.error("无法获取榜单页面")
        return []

    movies = parse_chart_page(html)
    if not movies:
        logger.error("榜单页面未解析到影片数据")
        return []

    logger.info("榜单解析完成，共 %d 部影片，开始获取移动端详情页补充简介", len(movies))

    for idx, movie in enumerate(movies, 1):
        if not movie["url"]:
            continue

        mobile_url = build_mobile_url(movie["url"])
        logger.info("[%d/%d] 获取详情: %s", idx, len(movies), movie["title"])

        detail_html = fetch_page(mobile_url, use_mobile=True)
        detail = parse_detail_page(detail_html, mobile_url)
        movie["summary"] = detail["summary"]

        _delay()

    logger.info("详情获取完成，共 %d 部影片", len(movies))
    return movies


def main():
    """主入口函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("crawler_douban 豆瓣影视热播榜单爬虫启动")
    logger.info("最大抓取数量: %d", MAX_ITEMS)

    all_data = crawl_chart()

    if not all_data:
        logger.error("未获取到任何榜单数据，程序退出")
        sys.exit(1)

    csv_path = save_data(all_data)
    logger.info("数据已保存: CSV=%s", csv_path)
    logger.info("crawler_douban 豆瓣影视热播榜单爬虫运行结束")


if __name__ == "__main__":
    main()
