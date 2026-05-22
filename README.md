# weatherEveryday

中国天气网天气预报爬虫，自动爬取指定城市的当日天气及未来三日预报数据，保存为 CSV 和 JSON 格式。

**⚠️ 仅作个人学习使用，不商用、不高频恶意请求**

## 功能特点

- 📍 支持多城市天气抓取（默认配置 10 个热门城市）
- 📊 数据保存为 CSV 和 JSON 双格式
- 🔄 集成请求重试机制和随机延时，规避访问限制
- ☁️ 适配 GitHub Actions 定时运行
- 📝 代码结构模块化，注释清晰

## 技术栈

- Python 3.12+
- requests - HTTP 请求
- beautifulsoup4 - HTML 解析
- uv - Python 包管理工具

## 项目结构

```
weatherEveryday/
├── .github/workflows/
│   └── weather.yml          # GitHub Actions 定时任务配置
├── weather_scraper/
│   ├── __init__.py           # 包初始化
│   ├── config.py             # 配置文件（城市编码、请求头、延时参数）
│   ├── fetcher.py            # HTTP 请求模块
│   ├── parser.py             # HTML 解析模块
│   └── storage.py            # 数据存储模块
├── output/                   # 输出目录（运行时自动创建）
├── main.py                   # 程序入口
└── pyproject.toml            # 项目配置
```

## 安装与运行

### 本地运行

```bash
# 安装依赖
uv sync

# 运行爬虫
uv run python main.py

# 查看结果
# output/weather_YYYYMMDD.csv   - 表格格式
# output/weather_YYYYMMDD.json  - JSON 格式
```

### 配置城市

编辑 `weather_scraper/config.py` 中的 `CITIES` 字典：

```python
CITIES = {
    "北京": "101010100",
    "上海": "101020100",
    # 添加更多城市...
}
```

城市编码可在中国天气网 URL 中找到，例如北京的 URL 为 `https://www.weather.com.cn/weather/101010100.shtml`，其中 `101010100` 即为城市编码。

## GitHub Actions 配置

### 定时任务

工作流默认配置为每天 **北京时间 09:00** 自动运行（UTC 01:00），可在 `.github/workflows/weather.yml` 中修改 cron 表达式：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

### 手动触发

在 GitHub 仓库的 **Actions** 标签页中，选择 `Daily Weather Crawl`，点击 **Run workflow** 即可手动触发。

### 数据提交

工作流会自动将爬取的天气数据提交到仓库的 `output/` 目录。

## 反限制措施

- ✅ 请求头伪装（模拟浏览器）
- ✅ 随机延时 2-5 秒
- ✅ 最多 3 次请求重试
- ✅ 遵循 robots.txt 规则

## 输出格式示例

### CSV 格式

| 城市 | 爬取日期 | 今日天气 | 今日最高温(℃) | 今日最低温(℃) | ... |
|------|----------|----------|---------------|---------------|-----|
| 北京 | 2026-05-22 | 小雨转阴 | 21 | 17 | ... |
| 上海 | 2026-05-22 | 阴转小雨 | 27 | 21 | ... |

### JSON 格式

```json
{
  "city": "北京",
  "crawl_date": "2026-05-22",
  "today": {
    "weather": "小雨转阴",
    "temp_high": "21",
    "temp_low": "17",
    "wind_direction": "东风转东南风",
    "wind_level": "<3级"
  },
  "forecast_3d": [
    {"date_label": "23日（明天）", "weather": "多云", ...},
    {"date_label": "24日（后天）", "weather": "多云转阴", ...},
    {"date_label": "25日（周一）", "weather": "阴", ...}
  ]
}
```

## 注意事项

1. 本项目仅作学习研究使用，请勿用于商业用途
2. 请遵守中国天气网的网站规则，避免高频请求
3. 数据来源为中国天气网公开信息
4. GitHub Actions 运行需要仓库有 `contents: write` 权限

## License

MIT License