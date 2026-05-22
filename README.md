# multi-crawler

多爬虫项目 - 多个爬虫共享一套 uv/Python 依赖，独立运行。

**⚠️ 仅作个人学习使用，不商用、不高频恶意请求**

## 项目结构

```
multi-crawler/
├── .github/workflows/              # GitHub Actions 工作流
│   ├── crawler_weather.yml         # 天气爬虫（每天 09:00）
│   ├── crawler_cctv_news.yml       # 央视新闻爬虫（每天 10:00）
│   └── crawler_douban.yml          # 豆瓣榜单爬虫（每天 11:00）
├── crawler_weather/                # 天气爬虫
│   ├── __init__.py
│   ├── config.py                   # 城市编码、请求头、延时参数
│   ├── fetcher.py                  # HTTP 请求模块
│   ├── parser.py                   # HTML 解析模块
│   ├── storage.py                  # CSV/JSON 存储
│   └── main.py                     # 入口
├── crawler_cctv_news/              # 央视新闻爬虫
│   ├── __init__.py
│   ├── config.py                   # 请求头、延时参数
│   ├── fetcher.py                  # HTTP 请求模块
│   ├── parser.py                   # HTML 解析模块
│   ├── storage.py                  # JSON 存储
│   └── main.py                     # 入口
├── crawler_douban/                 # 豆瓣榜单爬虫
│   ├── __init__.py
│   ├── config.py                   # 榜单URL、请求头、延时参数
│   ├── fetcher.py                  # HTTP 请求模块（含随机bid cookie）
│   ├── parser.py                   # HTML 解析模块
│   ├── storage.py                  # CSV 存储
│   └── main.py                     # 入口
├── output/                         # 输出目录（运行时自动创建）
│   ├── crawler_weather/
│   ├── crawler_cctv_news/
│   └── crawler_douban/
├── main.py                         # 统一入口
├── pyproject.toml                  # 共享依赖配置
└── README.md
```

## 现有爬虫

| 爬虫名称 | 说明 | 数据来源 | 输出格式 | 定时执行 |
|---|---|---|---|---|
| `crawler_weather` | 天气预报爬虫 | 中国天气网 | CSV + JSON | 每天 09:00 |
| `crawler_cctv_news` | 央视新闻热点爬虫 | 央视新闻 | JSON | 每天 10:00 |
| `crawler_douban` | 豆瓣影视热播榜单爬虫 | 豆瓣电影 | CSV | 每天 11:00 |

## 安装与运行

```bash
# 安装共享依赖
uv sync

# 查看可用爬虫
python main.py --help

# 运行指定爬虫
python main.py crawler_weather
python main.py crawler_cctv_news
python main.py crawler_douban

# 或直接运行模块
uv run python -m crawler_weather.main
uv run python -m crawler_cctv_news.main
uv run python -m crawler_douban.main
```

## 添加新爬虫

1. 创建爬虫目录 `crawler_xxx/`
2. 创建 `main.py` 并实现 `main()` 函数
3. 在 `main.py` 的 `CRAWLERS` 字典中注册
4. 在 `.github/workflows/` 创建 `crawler_xxx.yml`
5. 如需新依赖，添加到根目录 `pyproject.toml`

## 依赖管理

所有爬虫共享根目录 `pyproject.toml` 中的依赖：

```toml
dependencies = [
    "requests>=2.32.0",
    "beautifulsoup4>=4.12.0",
]
```

新增爬虫如需额外依赖，统一添加到 `pyproject.toml` 后执行 `uv sync`。

## GitHub Actions 配置

每个爬虫独立配置 workflow，互不影响：

| 工作流 | cron (UTC) | 北京时间 | 说明 |
|---|---|---|---|
| `crawler_weather.yml` | `0 1 * * *` | 09:00 | 天气预报 |
| `crawler_cctv_news.yml` | `0 2 * * *` | 10:00 | 央视新闻 |
| `crawler_douban.yml` | `0 3 * * *` | 11:00 | 豆瓣榜单 |

所有工作流均支持 `workflow_dispatch` 手动触发。

### 部署步骤

1. 在 GitHub 创建仓库
2. 推送代码到仓库
3. 进入 **Settings → Actions → General**，确保 Actions 权限为 **Read and write**
4. 进入 **Actions** 标签页，手动触发一次验证

### 修改执行时间

编辑对应 workflow 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 2 * * *'  # UTC 时间，北京时间需 +8
```

## 反限制措施

- ✅ 请求头伪装（模拟浏览器 User-Agent）
- ✅ 随机延时 2-5 秒
- ✅ 最多 3 次请求重试
- ✅ 遵循网站 robots.txt 规则

## 注意事项

1. 本项目仅作学习研究使用，请勿用于商业用途
2. 请遵守目标网站的使用协议，避免高频请求
3. 数据来源为公开信息，请注意数据使用权限

## License

MIT License