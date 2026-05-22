#!/usr/bin/env python3
"""
multi-crawler - 多爬虫项目入口

使用方式:
  python main.py crawler_weather    # 运行天气爬虫
  python main.py crawler_cctv_news  # 运行央视新闻爬虫
  python main.py crawler_douban     # 运行豆瓣榜单爬虫
"""

import sys
import importlib

CRAWLERS = {
    "crawler_weather": "中国天气网天气预报爬虫",
    "crawler_cctv_news": "央视新闻热点爬虫",
    "crawler_douban": "豆瓣影视热播榜单爬虫",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("multi-crawler - 多爬虫项目")
        print("")
        print("使用方式:")
        print("  python main.py <crawler_name>")
        print("")
        print("可用爬虫:")
        for name, desc in CRAWLERS.items():
            print(f"  {name:20s} - {desc}")
        sys.exit(0 if sys.argv[-1] in ("-h", "--help") else 1)

    crawler_name = sys.argv[1]

    if crawler_name not in CRAWLERS:
        print(f"错误: 未找到爬虫 '{crawler_name}'")
        print(f"可用爬虫: {', '.join(CRAWLERS.keys())}")
        sys.exit(1)

    try:
        module = importlib.import_module(f"{crawler_name}.main")
        module.main()
    except Exception as e:
        print(f"运行爬虫时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
