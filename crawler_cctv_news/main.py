"""
crawler_cctv_news - 央视新闻热点爬虫

功能：抓取央视新闻首页热点新闻，保存为JSON
仅做个人学习使用，不商用、不高频恶意请求
"""

import logging
import sys

from crawler_cctv_news.config import BASE_URL, LIST_URLS, MAX_NEWS_COUNT
from crawler_cctv_news.fetcher import _delay, fetch_page
from crawler_cctv_news.parser import parse_detail_page, parse_homepage
from crawler_cctv_news.storage import save_data


def setup_logging():
    """配置日志输出，兼容本地和GitHub Actions环境"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def crawl_news() -> list[dict]:
    """
    爬取央视新闻热点新闻

    先抓取首页，再补充各频道列表页，去重后逐条获取详情

    Returns:
        新闻数据列表
    """
    logger = logging.getLogger(__name__)
    seen_urls = set()
    news_list = []

    logger.info("开始获取央视新闻首页: %s", BASE_URL)
    html = fetch_page(BASE_URL)
    if html:
        items = parse_homepage(html)
        for item in items:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                news_list.append(item)
        logger.info("首页提取 %d 条新闻", len(items))

    _delay()

    for list_url in LIST_URLS:
        if len(news_list) >= MAX_NEWS_COUNT:
            break

        logger.info("获取频道列表页: %s", list_url)
        list_html = fetch_page(list_url)
        if list_html:
            items = parse_homepage(list_html)
            new_count = 0
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    news_list.append(item)
                    new_count += 1
            logger.info("频道页提取 %d 条新新闻", new_count)

        _delay()

    news_list = news_list[:MAX_NEWS_COUNT]

    if not news_list:
        logger.error("未解析到任何新闻")
        return []

    logger.info("共发现 %d 条新闻，开始逐条获取详情", len(news_list))

    all_data = []
    for idx, item in enumerate(news_list, 1):
        logger.info("[%d/%d] 获取详情: %s", idx, len(news_list), item["title"][:30])

        detail_html = fetch_page(item["url"])
        detail = parse_detail_page(detail_html, item["url"])

        news_data = {
            "title": item["title"],
            "url": item["url"],
            "publish_time": detail["publish_time"],
            "summary": detail["summary"],
        }
        all_data.append(news_data)

        _delay()

    logger.info("详情获取完成，共 %d 条新闻", len(all_data))
    return all_data


def main():
    """主入口函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("crawler_cctv_news 央视新闻爬虫启动")
    logger.info("最大抓取数量: %d", MAX_NEWS_COUNT)

    all_data = crawl_news()

    if not all_data:
        logger.error("未获取到任何新闻数据，程序退出")
        sys.exit(1)

    json_path = save_data(all_data)
    logger.info("数据已保存: JSON=%s", json_path)
    logger.info("crawler_cctv_news 央视新闻爬虫运行结束")


if __name__ == "__main__":
    main()
