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
└── test_files # 暂时存储爬取结果
```

### 运行爬虫

```shell
scrapy crawl ieee
```

随机爬取5篇ieee论文（由于暂时未设置代理，为避免ip封锁，暂时只爬取五篇，如果需要修改，在ieee_paper_spider.py中修改）

### 结果查看

存储结果保存在 /test_files/crawled_items.json中

### Log

log保存在 /scrapy_logs中