"""
HTML解析模块：使用BeautifulSoup解析央视新闻页面，提取热点新闻数据
"""

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler_cctv_news.config import BASE_URL, MAX_NEWS_COUNT

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """清理文本中的多余空白字符"""
    return re.sub(r"\s+", " ", text).strip()


def _is_valid_news_link(href: str) -> bool:
    """判断链接是否为有效的新闻详情页"""
    if not href:
        return False
    if not href.startswith("http"):
        href = urljoin(BASE_URL, href)
    return bool(re.search(r"news\.cctv\.com/\d{4}/\d{2}/\d{2}/", href)) or bool(
        re.search(r"tv\.cctv\.com/\d{4}/\d{2}/\d{2}/", href)
    )


def parse_homepage(html: str) -> list[dict]:
    """
    解析央视新闻首页，提取热点新闻标题和链接

    Args:
        html: 首页HTML文本

    Returns:
        新闻列表，每项包含title和url
    """
    if not html:
        logger.warning("HTML内容为空，跳过解析")
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_items = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        title = _clean_text(a_tag.get_text())

        if not title or len(title) < 6:
            continue
        if not _is_valid_news_link(href):
            continue

        full_url = urljoin(BASE_URL, href)
        url_key = full_url.split("?")[0]

        if url_key in seen_urls:
            continue

        seen_urls.add(url_key)
        news_items.append({"title": title, "url": full_url})

        if len(news_items) >= MAX_NEWS_COUNT:
            break

    logger.info("首页解析完成，提取到 %d 条新闻链接", len(news_items))
    return news_items


def parse_detail_page(html: str, url: str) -> dict:
    """
    解析新闻详情页，提取发布时间、摘要

    Args:
        html: 详情页HTML文本
        url: 详情页URL

    Returns:
        包含publish_time和summary的字典
    """
    result = {"publish_time": "", "summary": ""}

    if not html:
        return result

    soup = BeautifulSoup(html, "html.parser")

    time_tag = (
        soup.find("div", class_="info1")
        or soup.find("span", class_="time")
        or soup.find("div", class_="time")
        or soup.find("span", class_="info")
        or soup.find("div", class_="info")
    )
    if time_tag:
        time_text = _clean_text(time_tag.get_text())
        date_match = re.search(
            r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?\s*\d{0,2}[:时]?\d{0,2}",
            time_text,
        )
        if date_match:
            result["publish_time"] = date_match.group()

    content_area = (
        soup.find("div", class_="cnt_bd")
        or soup.find("div", class_="text_area")
        or soup.find("div", class_="article-content")
        or soup.find("div", id="content_area")
        or soup.find("div", class_="content")
        or soup.find("div", class_="cnt_bd")
    )

    if content_area:
        paragraphs = content_area.find_all("p")
        texts = []
        for p in paragraphs:
            text = _clean_text(p.get_text())
            if text and len(text) > 10:
                texts.append(text)
        if texts:
            result["summary"] = texts[0][:200]
        else:
            all_text = _clean_text(content_area.get_text())
            result["summary"] = all_text[:200] if all_text else ""

    if not result["summary"]:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            result["summary"] = meta_desc["content"][:200]

    if not result["summary"]:
        body = soup.find("body")
        if body:
            for tag in body.find_all(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            all_text = _clean_text(body.get_text())
            if all_text:
                result["summary"] = all_text[:200]

    return result
