---
name: "add-crawler"
description: "Adds a new crawler module to the multi-crawler project. Invoke when user wants to create/add a new crawler to the existing multi-crawler project structure."
---

# Add New Crawler to Multi-Crawler Project

向 multi-crawler 项目添加新爬虫的标准流程。项目根目录为当前工作目录，所有爬虫共享 `pyproject.toml` 中的依赖。

## 项目结构约定

```
multi-crawler/
├── .github/workflows/
│   └── crawler_xxx.yml          # 新爬虫的 workflow
├── crawler_xxx/                 # 新爬虫目录
│   ├── __init__.py              # 包初始化，含 __version__
│   ├── config.py                # 配置：URL、请求头、延时、输出目录
│   ├── fetcher.py               # HTTP请求：重试、延时、异常处理
│   ├── parser.py                # HTML解析：BeautifulSoup提取数据
│   ├── storage.py               # 数据存储：JSON/CSV保存
│   └── main.py                  # 入口：setup_logging + main()
├── main.py                      # 统一入口（需注册新爬虫）
├── pyproject.toml               # 共享依赖
└── README.md                    # 需更新爬虫列表
```

## 标准添加流程

### 第一步：研究目标网站

1. **用 WebFetch 抓取目标页面**，观察页面结构（静态HTML vs JS动态渲染）
2. **检查 robots.txt**（`WebFetch` 目标站 `/robots.txt`），确认爬取合规
3. **确定数据源URL**：
   - 优先选择服务端渲染（SSR）的页面，纯 requests 可获取
   - 若首页为JS动态渲染，寻找频道列表页、分页URL等静态数据源
   - 避免使用无头浏览器，保持技术栈统一（requests + BeautifulSoup）
4. **记录页面结构**：标题、时间、摘要等数据在HTML中的标签和class

### 第二步：创建爬虫目录和模块

按以下模板创建 `crawler_xxx/` 目录下的6个文件：

#### `__init__.py`
```python
"""
crawler_xxx - 目标网站爬虫简介

仅做个人学习使用，不商用、不高频恶意请求
"""

__version__ = "0.1.0"
```

#### `config.py`
```python
"""
配置模块：爬虫相关参数集中管理
"""

BASE_URL = "https://example.com/"

LIST_URLS = [  # 可选：多数据源页面
    "https://example.com/channel1/",
    "https://example.com/channel2/",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "https://example.com/",
}

REQUEST_DELAY_MIN = 2
REQUEST_DELAY_MAX = 5
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
MAX_ITEMS = 20
OUTPUT_DIR = "output/crawler_xxx"
ENCODING = "utf-8"
```

#### `fetcher.py`
复制已有爬虫的 fetcher.py，修改 import 路径即可（`from crawler_xxx.config import ...`）。

核心逻辑：
- `_delay()`: 随机延时 2-5 秒
- `fetch_page(url)`: 重试3次，返回 HTML 或 None

#### `parser.py`
根据目标网站HTML结构编写解析逻辑，核心原则：
- **多级降级策略**：先找精确class，找不到则用通用选择器，最后用meta标签兜底
- **文本清理**：`re.sub(r"\s+", " ", text).strip()` 统一清理空白
- **链接去重**：用 `set()` 记录已见URL，`urljoin()` 补全相对路径
- **摘要提取**：优先从正文段落提取，兜底用 `<meta name="description">`

#### `storage.py`
- 输出目录：`output/crawler_xxx/`
- 文件命名：`xxx_YYYYMMDD.json` 或 `xxx_YYYYMMDD.csv`
- JSON 使用 `ensure_ascii=False, indent=2` 保留中文可读性
- CSV 使用 `utf-8-sig` 编码，Excel 可直接打开

#### `main.py`
```python
"""
crawler_xxx - 爬虫简介
"""

import logging
import sys

from crawler_xxx.config import BASE_URL, MAX_ITEMS
from crawler_xxx.fetcher import _delay, fetch_page
from crawler_xxx.parser import parse_homepage, parse_detail_page
from crawler_xxx.storage import save_data


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("crawler_xxx 爬虫启动")
    # ... 爬取逻辑 ...
    if not all_data:
        logger.error("未获取到数据，程序退出")
        sys.exit(1)
    save_data(all_data)
    logger.info("crawler_xxx 爬虫运行结束")


if __name__ == "__main__":
    main()
```

### 第三步：注册到统一入口

编辑根目录 `main.py`，在 `CRAWLERS` 字典中添加：

```python
CRAWLERS = {
    "crawler_weather": "中国天气网天气预报爬虫",
    "crawler_cctv_news": "央视新闻热点爬虫",
    "crawler_xxx": "新爬虫描述",  # 新增
}
```

### 第四步：创建 GitHub Actions workflow

创建 `.github/workflows/crawler_xxx.yml`：

```yaml
name: Crawler Xxx

on:
  schedule:
    - cron: '0 3 * * *'   # UTC时间，北京时间需+8
  workflow_dispatch:

permissions:
  contents: write

jobs:
  crawl-xxx:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync

      - name: Run crawler
        run: uv run python -m crawler_xxx.main

      - name: Commit and push data
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add -f output/ || true
          git diff --staged --quiet || git commit -m "chore: update xxx data $(date +%Y-%m-%d)"
          git push
```

### 第五步：更新 README

在 README 的爬虫列表表格中添加新行。

### 第六步：本地测试

```bash
uv run python main.py crawler_xxx
```

验证：
- 数据正确保存到 `output/crawler_xxx/`
- JSON/CSV 内容完整（标题、时间、摘要等字段不为空）
- 无报错退出

## 踩坑记录与注意事项

### 1. JS动态渲染页面

**问题**：很多新闻/资讯网站首页大量内容通过JavaScript动态加载，纯 `requests.get()` 只能获取到少量静态HTML中的链接。

**解决方案**：
- 不要只依赖首页，补充频道列表页（如 `/china/`、`/world/`）作为额外数据源
- 在 `config.py` 中配置 `LIST_URLS` 列表，多页面聚合后去重
- 列表页通常比首页有更多静态渲染的链接

### 2. 详情页解析不稳定

**问题**：不同频道的详情页HTML结构可能不同，单一选择器容易失败。

**解决方案**：
- 使用多级降级策略：`soup.find("div", class_="cnt_bd") or soup.find("div", class_="text_area") or ...`
- 摘要兜底：先尝试正文段落 → 再尝试 `<meta name="description">` → 最后尝试 body 全文截取
- 时间提取用正则：`re.search(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}", text)` 适配多种格式

### 3. URL去重

**问题**：同一新闻在首页和频道页重复出现，或URL带不同查询参数。

**解决方案**：
- 去重时使用 `url.split("?")[0]` 去除查询参数
- 用 `set()` 维护已见URL集合

### 4. GitHub Actions 注意事项

- **Action版本**：使用 `actions/checkout@v5` 和 `astral-sh/setup-uv@v7`（支持Node.js 24，无弃用警告）
- **不要用** `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` 环境变量，直接用新版Action
- **git add -f**：`output/` 在 `.gitignore` 中，需要 `-f` 强制添加
- **日志输出**：`logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])`，Actions只捕获stdout
- **退出码**：失败时 `sys.exit(1)`，让Actions正确标记失败
- **cron时区**：GitHub Actions cron使用UTC时间，北京时间 = UTC + 8

### 5. 编码问题

- 请求后设置 `response.encoding = "utf-8"`，避免乱码
- CSV保存用 `utf-8-sig` 编码（带BOM），Excel可直接打开不乱码
- JSON保存用 `ensure_ascii=False`，保留中文原样

### 6. 请求限制规避

- User-Agent伪装完整（Chrome版本号、Accept、Accept-Language、Referer）
- 随机延时 2-5 秒，不要固定间隔
- 最多3次重试，失败跳过不中断整个流程
- 遵循 robots.txt

### 7. import路径

每个爬虫模块内部互相引用时，使用 `from crawler_xxx.config import ...` 格式（以爬虫目录名为包名），不要用相对路径 `from .config import ...`，确保 `python -m crawler_xxx.main` 和 `python main.py crawler_xxx` 两种运行方式都能正常工作。

### 8. Accept-Encoding 不要包含 br（brotli）

**问题**：`requests` 库默认不支持 brotli（`br`）解压缩。如果在 `Accept-Encoding` 中声明了 `br`，服务器可能返回 brotli 压缩的响应，但 `requests` 无法解压，导致 `response.text` 为乱码或空字符串。

**解决方案**：
- `Accept-Encoding` 只写 `"gzip, deflate"`，不要加 `br`
- `requests` 原生支持 gzip 和 deflate 自动解压
- 如需 brotli 支持，需额外安装 `brotli` 或 `brotlicffi` 包

**示例**：
```python
# 错误 - 可能导致乱码
"Accept-Encoding": "gzip, deflate, br"

# 正确
"Accept-Encoding": "gzip, deflate"
```

### 9. 桌面端详情页有JS反爬验证时，使用移动端页面

**问题**：部分网站（如豆瓣）的桌面端详情页有 JavaScript 反爬验证（如 SHA-512 proof-of-work 挑战），纯 `requests` 无法通过验证，返回的是"载入中..."挑战页面而非真实内容。

**解决方案**：
- 尝试访问移动端页面（如 `m.douban.com` 代替 `movie.douban.com`），移动端通常没有JS验证
- 在 `config.py` 中配置 `MOBILE_HEADERS`（使用移动端 User-Agent）
- 在 `fetcher.py` 中添加 `build_mobile_url()` 函数，将桌面端URL转换为移动端URL
- `fetch_page()` 增加 `use_mobile` 参数，按需切换请求头

**示例**：
```python
# config.py
MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ...",
    "Referer": "https://m.douban.com/",
}

# fetcher.py
def build_mobile_url(desktop_url: str) -> str:
    return desktop_url.replace(
        "https://movie.douban.com/", "https://m.douban.com/movie/"
    )

def fetch_page(url: str, use_mobile: bool = False) -> str | None:
    base_headers = MOBILE_HEADERS if use_mobile else HEADERS
    ...

# main.py
mobile_url = build_mobile_url(movie["url"])
detail_html = fetch_page(mobile_url, use_mobile=True)
```

### 10. HTML标签class属性可能与预期不符

**问题**：根据经验假设的HTML标签class属性可能与实际页面不符。例如豆瓣榜单页的影片信息在 `<p>` 标签中，但该 `<p>` 标签没有 `class="pl"` 属性，而评分人数的 `<span>` 才有 `class="pl"`。

**解决方案**：
- **先用脚本抓取实际HTML并分析结构**，不要凭经验假设
- 使用多级降级策略查找标签：先按精确class查找，找不到则按标签名查找
- 解析结果为0时，第一时间保存HTML到文件检查实际结构

**示例**：
```python
# 降级查找 <p> 标签
info_p = pl2.find("p", class_="pl")  # 先找有class的
if not info_p:
    info_p = pl2.find("p")           # 找不到则找任意 <p>
```

### 11. 随机bid cookie

**问题**：豆瓣等网站使用 `bid` cookie 标识访客，没有该cookie可能被拦截。

**解决方案**：
- 在 `fetcher.py` 中生成随机11位字母数字组合作为 `bid`
- 每次请求都携带随机 `bid`，避免被关联追踪
- 通过 `headers["Cookie"] = f"bid={_generate_bid()}"` 设置
