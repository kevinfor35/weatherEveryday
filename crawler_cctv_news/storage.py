"""
数据存储模块：将爬取的新闻数据保存为JSON格式
"""

import json
import logging
import os
from datetime import datetime

from crawler_cctv_news.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _ensure_output_dir() -> str:
    """确保输出目录存在，返回目录路径"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def save_as_json(all_data: list[dict]) -> str:
    """
    将新闻数据保存为JSON文件

    Args:
        all_data: 新闻数据列表

    Returns:
        保存的文件路径
    """
    output_dir = _ensure_output_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    filepath = os.path.join(output_dir, f"cctv_news_{date_str}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    logger.info("JSON文件已保存: %s (%d 条记录)", filepath, len(all_data))
    return filepath


def save_data(all_data: list[dict]) -> str:
    """
    保存新闻数据

    Args:
        all_data: 新闻数据列表

    Returns:
        保存的文件路径
    """
    return save_as_json(all_data)
