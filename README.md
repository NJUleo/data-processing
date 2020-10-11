# Data Crawler

### 项目结构

```shell
.
├── data_crawler
│   ├── fake_agents.json
│   ├── __init__.py
│   ├── items.py # 用与定义所爬下数据的结构
│   ├── middlewares.py # 中间件
│   ├── pipelines.py # pipelines，用于数据的清理、保存
│   ├── settings.py # scrapy项目配置文件
│   └── spiders # 各爬虫
│       ├── acm_spider.py
│       ├── ieee_author_spider.py
│       ├── ieee_paper_spider.py
│       ├── __init__.py
│       └── utils.py # 爬虫所使用的工具
├── fake_agents.json
├── README.md
├── requirements.txt # 配置要求
├── scrapy.cfg
├── scrapy_logs
├── proxies.txt # http代理地址
└── test_files # 暂时存储爬取结果
```

### 运行爬虫

#### IEEE

```shell
scrapy crawl ieee
```

随机爬取5篇ieee论文（由于暂时未设置代理，为避免ip封锁，暂时只爬取五篇，如果需要修改，在ieee_paper_spider.py中修改）

由于暂时使用随机爬取，和proxy判断有冲突，如果进行，建议不使用proxy（将proxies.txt设置为空文件）

#### ACM

```shell
scrapy crawl ACM_Paper
```

爬取data_crawler/settings.py中ACM_URL中的所有页面。这里要求这些页面是ACM的搜索结果页面。爬虫会爬取搜索出的所有文章的相关信息保存于文件。

暂时未实现关键词爬取。

### 结果查看

存储结果保存在 /test_files/crawled_items.json中

### Log

log保存在 /scrapy_logs中

### Proxy

在proxies.txt中列出http代理的ip和端口号，自动随机切换代理。

格式为一行一个，ip:端口号

如果不需要代理则在settings中将rotating_proxies.middlewares.RotatingProxyMiddleware、rotating_proxies.middlewares.BanDetectionMiddleware两个中间件禁用