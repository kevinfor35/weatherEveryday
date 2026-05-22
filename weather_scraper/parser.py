"""
HTML解析模块：使用BeautifulSoup解析中国天气网页面，提取天气数据

解析7天预报页面，提取当日天气和未来3日预报
"""

import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """清理文本中的多余空白字符"""
    return re.sub(r"\s+", "", text).strip()


def _parse_temperature(tem_tag) -> dict:
    """
    解析温度标签

    页面结构：<p class="tem"><span>21</span><i>17℃</i></p>
    span为最高温，i为最低温；部分天气可能缺少最高温（如夜间）

    Args:
        tem_tag: BeautifulSoup标签对象

    Returns:
        包含high和low温度的字典
    """
    result = {"high": "", "low": ""}
    if tem_tag is None:
        return result

    span = tem_tag.find("span")
    i_tag = tem_tag.find("i")

    if span:
        result["high"] = _clean_text(span.get_text())
    if i_tag:
        low_text = _clean_text(i_tag.get_text()).replace("℃", "")
        result["low"] = low_text

    if not span and i_tag:
        result["high"] = result["low"]
        result["low"] = ""

    return result


def _parse_wind(win_tag) -> dict:
    """
    解析风力风向标签

    页面结构：<p class="win"><em><span title="东北风">...</span></em><i><3级</i></p>

    Args:
        win_tag: BeautifulSoup标签对象

    Returns:
        包含direction和level的字典
    """
    result = {"direction": "", "level": ""}
    if win_tag is None:
        return result

    em_tag = win_tag.find("em")
    if em_tag:
        spans = em_tag.find_all("span")
        if spans:
            directions = []
            for span in spans:
                title = span.get("title", "")
                if title:
                    directions.append(title)
            if directions:
                result["direction"] = "转".join(directions)

    i_tag = win_tag.find("i")
    if i_tag:
        result["level"] = _clean_text(i_tag.get_text())

    return result


def parse_7d_forecast(html: str, city_name: str) -> dict | None:
    """
    解析7天预报页面HTML，提取当日天气和未来3日预报

    Args:
        html: 页面HTML文本
        city_name: 城市名称

    Returns:
        解析后的天气数据字典，失败返回None
    """
    if not html:
        logger.warning("HTML内容为空，跳过解析: %s", city_name)
        return None

    soup = BeautifulSoup(html, "html.parser")

    div_7d = soup.find("div", id="7d")
    if not div_7d:
        logger.warning("未找到7天预报区域: %s", city_name)
        return None

    ul = div_7d.find("ul", class_="t clearfix")
    if not ul:
        logger.warning("未找到预报列表: %s", city_name)
        return None

    li_items = ul.find_all("li")
    if not li_items:
        logger.warning("预报列表为空: %s", city_name)
        return None

    today_date = datetime.now().strftime("%Y-%m-%d")
    forecast_days = []

    for idx, li in enumerate(li_items):
        if idx >= 4:
            break

        h1 = li.find("h1")
        date_text = _clean_text(h1.get_text()) if h1 else ""

        wea_tag = li.find("p", class_="wea")
        weather = _clean_text(wea_tag.get_text()) if wea_tag else ""

        tem_tag = li.find("p", class_="tem")
        temps = _parse_temperature(tem_tag)

        win_tag = li.find("p", class_="win")
        wind = _parse_wind(win_tag)

        day_data = {
            "date_label": date_text,
            "weather": weather,
            "temp_high": temps["high"],
            "temp_low": temps["low"],
            "wind_direction": wind["direction"],
            "wind_level": wind["level"],
        }
        forecast_days.append(day_data)

    if not forecast_days:
        logger.warning("未能解析出任何天气数据: %s", city_name)
        return None

    today = forecast_days[0]
    future_3d = forecast_days[1:4] if len(forecast_days) > 1 else []

    result = {
        "city": city_name,
        "crawl_date": today_date,
        "today": {
            "weather": today["weather"],
            "temp_high": today["temp_high"],
            "temp_low": today["temp_low"],
            "wind_direction": today["wind_direction"],
            "wind_level": today["wind_level"],
        },
        "forecast_3d": [
            {
                "date_label": day["date_label"],
                "weather": day["weather"],
                "temp_high": day["temp_high"],
                "temp_low": day["temp_low"],
                "wind_direction": day["wind_direction"],
                "wind_level": day["wind_level"],
            }
            for day in future_3d
        ],
    }

    logger.info("解析成功: %s - 今日天气: %s", city_name, today["weather"])
    return result
