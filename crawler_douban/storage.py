"""
数据存储模块：将爬取的豆瓣榜单数据保存为CSV文件
"""

import csv
import logging
import os
from datetime import datetime

from crawler_douban.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _ensure_output_dir() -> str:
    """确保输出目录存在，返回目录路径"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def save_as_csv(all_data: list[dict]) -> str:
    """
    将榜单数据保存为CSV文件

    使用utf-8-sig编码，Excel可直接打开不乱码

    Args:
        all_data: 影片数据列表

    Returns:
        保存的文件路径
    """
    output_dir = _ensure_output_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    filepath = os.path.join(output_dir, f"douban_chart_{date_str}.csv")

    fieldnames = [
        "rank",
        "title",
        "rating",
        "rating_count",
        "release_info",
        "summary",
        "url",
    ]

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    logger.info("CSV文件已保存: %s (%d 条记录)", filepath, len(all_data))
    return filepath


def save_data(all_data: list[dict]) -> str:
    """
    保存榜单数据

    Args:
        all_data: 影片数据列表

    Returns:
        保存的文件路径
    """
    return save_as_csv(all_data)
