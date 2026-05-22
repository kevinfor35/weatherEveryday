"""
HTML解析模块：使用BeautifulSoup解析豆瓣影视榜单页面，提取影片数据
"""

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler_douban.config import CHART_URL, MAX_ITEMS

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """清理文本中的多余空白字符"""
    return re.sub(r"\s+", " ", text).strip()


def parse_chart_page(html: str) -> list[dict]:
    """
    解析豆瓣榜单页面，提取影片信息

    采用多级降级策略：先找tr.item，再找div.pl2

    Args:
        html: 榜单页面HTML文本

    Returns:
        影片列表，每项包含rank、title、url、rating、rating_count、release_info
    """
    if not html:
        logger.warning("HTML内容为空，跳过解析")
        return []

    soup = BeautifulSoup(html, "html.parser")
    movies = []

    items = soup.find_all("tr", class_="item")

    if not items:
        items = soup.select("div.indent table tr")

    if items:
        for idx, item in enumerate(items, 1):
            movie = _parse_movie_item(item, idx)
            if movie:
                movies.append(movie)
    else:
        pl2_divs = soup.find_all("div", class_="pl2")
        for idx, div in enumerate(pl2_divs, 1):
            movie = _extract_movie_from_pl2(div, idx)
            if movie:
                movies.append(movie)
        logger.info("榜单解析完成（pl2降级），提取到 %d 部影片", len(movies))
        return movies[:MAX_ITEMS]

    logger.info("榜单解析完成，提取到 %d 部影片", len(movies))
    return movies[:MAX_ITEMS]


def _parse_movie_item(item, rank: int) -> dict | None:
    """
    解析单个影片条目（tr.item）

    Args:
        item: BeautifulSoup标签对象
        rank: 排名

    Returns:
        影片信息字典，解析失败返回None
    """
    pl2 = item.find("div", class_="pl2")
    if not pl2:
        return None

    return _extract_movie_from_pl2(pl2, rank)


def _extract_movie_from_pl2(pl2, rank: int) -> dict | None:
    """
    从div.pl2提取影片核心信息

    Args:
        pl2: BeautifulSoup标签对象
        rank: 排名

    Returns:
        影片信息字典，解析失败返回None
    """
    title_link = pl2.find("a")
    if not title_link:
        return None

    raw_title = _clean_text(title_link.get_text())
    title = raw_title.split(" / ")[0].strip()

    href = title_link.get("href", "")
    url = urljoin(CHART_URL, href) if href else ""

    rating = ""
    rating_nums = pl2.find("span", class_="rating_nums")
    if rating_nums:
        rating = _clean_text(rating_nums.get_text())

    rating_count = ""
    pl_span = pl2.find("span", class_="pl")
    if pl_span:
        count_text = _clean_text(pl_span.get_text())
        count_match = re.search(r"(\d+人评价)", count_text)
        if count_match:
            rating_count = count_match.group(1)

    release_info = ""
    info_p = pl2.find("p", class_="pl")
    if not info_p:
        info_p = pl2.find("p")
    if info_p:
        release_info = _clean_text(info_p.get_text())

    return {
        "rank": rank,
        "title": title,
        "url": url,
        "rating": rating,
        "rating_count": rating_count,
        "release_info": release_info,
        "summary": "",
    }


def parse_detail_page(html: str, url: str) -> dict:
    """
    解析移动端影片详情页，提取简介

    移动端页面无JS验证，可直接获取简介内容
    采用多级降级策略：h2剧情简介兄弟节点 → meta标签description

    Args:
        html: 详情页HTML文本
        url: 详情页URL

    Returns:
        包含summary的字典
    """
    result = {"summary": ""}

    if not html:
        return result

    soup = BeautifulSoup(html, "html.parser")

    for h2 in soup.find_all("h2"):
        if "剧情简介" in h2.get_text():
            next_div = h2.find_next_sibling("div")
            if next_div:
                summary = _clean_text(next_div.get_text())
                if summary:
                    result["summary"] = summary
                    return result

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        content = _clean_text(meta_desc["content"])
        match = re.search(r"简介[：:](.+)", content)
        if match:
            result["summary"] = match.group(1)[:300]
        else:
            result["summary"] = content[:300]

    return result
