"""
数据存储模块：将爬取的天气数据保存为CSV和JSON格式
"""

import csv
import json
import logging
import os
from datetime import datetime

from crawler_weather.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _ensure_output_dir() -> str:
    """确保输出目录存在，返回目录路径"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def _flatten_weather_data(all_data: list[dict]) -> list[dict]:
    """
    将嵌套的天气数据展平为适合CSV存储的扁平结构

    Args:
        all_data: 原始天气数据列表

    Returns:
        展平后的数据列表
    """
    rows = []
    for item in all_data:
        row = {
            "城市": item["city"],
            "爬取日期": item["crawl_date"],
            "今日天气": item["today"]["weather"],
            "今日最高温(℃)": item["today"]["temp_high"],
            "今日最低温(℃)": item["today"]["temp_low"],
            "今日风向": item["today"]["wind_direction"],
            "今日风力": item["today"]["wind_level"],
        }
        for i, day in enumerate(item.get("forecast_3d", []), 1):
            row[f"第{i}日日期"] = day["date_label"]
            row[f"第{i}日天气"] = day["weather"]
            row[f"第{i}日最高温(℃)"] = day["temp_high"]
            row[f"第{i}日最低温(℃)"] = day["temp_low"]
            row[f"第{i}日风向"] = day["wind_direction"]
            row[f"第{i}日风力"] = day["wind_level"]
        rows.append(row)
    return rows


def save_as_csv(all_data: list[dict]) -> str:
    """
    将天气数据保存为CSV文件

    Args:
        all_data: 天气数据列表

    Returns:
        保存的文件路径
    """
    output_dir = _ensure_output_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    filepath = os.path.join(output_dir, f"weather_{date_str}.csv")

    rows = _flatten_weather_data(all_data)
    if not rows:
        logger.warning("无数据可保存为CSV")
        return ""

    fieldnames = list(rows[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("CSV文件已保存: %s (%d 条记录)", filepath, len(rows))
    return filepath


def save_as_json(all_data: list[dict]) -> str:
    """
    将天气数据保存为JSON文件

    Args:
        all_data: 天气数据列表

    Returns:
        保存的文件路径
    """
    output_dir = _ensure_output_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    filepath = os.path.join(output_dir, f"weather_{date_str}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    logger.info("JSON文件已保存: %s (%d 条记录)", filepath, len(all_data))
    return filepath


def save_data(all_data: list[dict]) -> tuple[str, str]:
    """
    同时保存为CSV和JSON格式

    Args:
        all_data: 天气数据列表

    Returns:
        (csv_path, json_path) 元组
    """
    csv_path = save_as_csv(all_data)
    json_path = save_as_json(all_data)
    return csv_path, json_path
