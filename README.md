# Data Crawler

## Requirements

python 3.6.9

8.0.20 MySQL Community Server - GPL

other python packages in requirements.txt

## 项目结构

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
│       ├── acm_spider.py # ACM paper in search result crawler
│       ├── acm_paper_parser.py # 用于处理ACM paper页面的静态方法
│       ├── acm_proceeding_spider.py # ACM proceeding crawler
│       ├── ieee_spider.py # IEEE conferences crawler
│       ├── ieee_author_spider.py
│       ├── ieee_paper_spider.py # IEEE random paper crawler
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

## 运行爬虫

### ACM paper in search result crawler

```shell
scrapy crawl ACM_Search
```

爬取data_crawler/settings.py中ACM_URL中的所有页面。这里要求这些页面是ACM的搜索结果页面。爬虫会爬取搜索出的所有文章的相关信息保存于文件。

### IEEE crawler

#### command

```shell
scrapy crawl IEEE_Conferences_Journals
```

#### settings

/data_crawler/settings.py

```python
# IEEE
# IEEE conferences
IEEE_CONF_URLS = [
    'https://ieeexplore.ieee.org/xpl/conhome/1000064/all-proceedings'
]
# 需要的年份(including 'from' and 'to')
IEEE_YEAR = {
    'from': 2019,
    'to': 2019
}
# IEEE journal
# journal 主页的 url。事实上只需要 punumber
IEEE_JOURNAL_URLS = [
    # 'https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=32'
]
IEEE_JOURNAL_YEAR = {
    'from': 2020,
    'to': 2020
}
```

#### result

爬取 IEEE_CONF_URLS 中所有会议在 IEEE_YEAR 范围内的所有文章

爬取 IEEE_JOURNAL_URLS 中所有期刊在 IEEE_JOURNAL_YEAR 范围内的所有文章

### ACM crawler

#### command

```shell
scrapy crawl ACM_Proceedings_Journals
```

#### settings

/data_crawler/settings.py

```python
### ACM conference proceeding urls
ACM_PROCEEDING_URLS = [
    'https://dl.acm.org/doi/proceedings/10.1145/3238147'
]
### ACM journals
ACM_JOURNAL_URLS = [
    'https://dl.acm.org/loi/tosem'
]
### 需要的年份(including 'from' and 'to')
ACM_JOURNAL_YEAR = {
    'from': 2019,
    'to': 2019
}
```

可以是多个proceeding

#### result

爬取 ACM_PROCEEDING_URLS 中的所有文章

爬取 ACM_JOURNAL_URLS 中 journal 在 ACM_JOURNAL_YEAR 范围内的所有文章

### DEBUG crawler

为了节约时间，模拟spider向pipeline发送数据，用于对pipeline的debug。直接读取之前爬取的内容，然后作为item传给pipeline处理。

#### command

```shell
scrapy crawl debug
```

#### settings

在test_files/crawled_items_debug.json 中放入之前爬的 raw json 结果

#### result

等于不实际发送请求，而是把之前的结果再次发送给pipeline处理

## 结果查看

### Raw Json File

存储结果保存在 /test_files/crawled_items.json中。其中是没有经过处理的所有spider传回的item

### Database

存储于数据库data_processing表中。

#### setting

如要启动数据库保存，需要在/data_crawler/settings中设置:

1. 配置数据库用户名密码等

   ```python
   # Database
   MYSQL_HOST = 'localhost'
   MYSQL_DBNAME = 'data_processing'
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'root'
   MYSQL_PORT = 3306
   ```

2. 启动MysqlPipeline(确保'data_crawler.pipelines.MysqlPipeline': 889的最后这个数字不是None)

   ```python
   ITEM_PIPELINES = {
       'data_crawler.pipelines.RemoveEmptyItemPipeline': 500,
    	'data_crawler.pipelines.JsonWriterPipeline': 888 if not DEBUG else None,
       'data_crawler.pipelines.MysqlPipeline': 889,
   }
   ```
   

#### 数据库初始化

进入Mysql之后运行 source /absolute/path/data_processing.sql (或者在data_processing根目录下进入mysql，可以写相对路径)

**注意此操作会将原名为data_processing的数据库删库**

#### 数据库基本结构

##### 1. affiliation

TODO: 目前来看，ieee没有affliation的页面，因此也似乎没有内部id，怎么处理暂时不清楚。暂时用name来作为IEEE affiliation的id

| 序号 |     名称      |                描述                 |     类型      |  键  | 为空 | 额外 | 默认值 |
| :--: | :-----------: | :---------------------------------: | :-----------: | :--: | :--: | :--: | :----: |
|  1   |     `id`      | ACM_{ACM内部id}或IEEE__{IEEE内部id} | varchar(255)  | PRI  |  NO  |      |        |
|  2   |    `name`     |                                     | varchar(255)  |      |  NO  |      |        |
|  3   | `description` |                                     | varchar(4095) |      | YES  |      |        |

##### 2. domain

| 序号 |  名称  |        描述        |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :----: | :----------------: | :----------: | :--: | :--: | :--: | :----: |
|  1   |  `id`  |                  | varchar(255) | PRI  |  NO  |      |        |
|  2   |  `name`  |  | varchar(255) |   |  NO  |      |        |
|  3   | `url` | 如果是ACM则有url | varchar(255) |      | YES |      |        |

##### 3. paper

| 序号 |        名称        |        描述        |     类型      |  键  | 为空 | 额外 | 默认值 |
| :--: | :----------------: | :----------------: | :-----------: | :--: | :--: | :--: | :----: |
|  1   |        `id`        | 事实上是一个十六进制数, 是将 doi 取其 utf-8 编码的十六进制数字符串 | varchar(255)  | PRI  |  NO  |      |        |
|  2   |      `title`       |                    | varchar(255)  |      |  NO  |      |        |
|  3   |       `abs`        |      abstract      | varchar(4095) |      |  NO  |      |        |
|  4   |  `publication_id`  |  发表的会议的id  | varchar(255)  |      |  NO  |      |        |
|  5   | `publication_date` | 发表年份，事实上和 publication表冗余，但是为了方便还是直接存了 | varchar(255)  |      |  NO  |      |        |
|  6   |       `link`       | 事实上是 doi.org/{paper_doi} | varchar(255)  |      |  NO  |      |        |
|  7  |       `citation`       | 被引量 | int(11) |      |  NO  |      |        |


##### 4. researcher

| 序号 |  名称  |                             描述                             |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :----: | :----------------------------------------------------------: | :----------: | :--: | :--: | :--: | :----: |
|  1   |  `id`  | ACM_{ACM内部id}或IEEE__{IEEE内部id}，如IEEE_37085628262，说明其主页是https://ieeexplore.ieee.org/author/37085628262 | varchar(255) | PRI  |  NO  |      |        |
|  2   | `name` |                                                              | varchar(255) |      |  NO  |      |        |

##### 5. publication

| 序号 |        名称        |                 描述                  |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :----------------: | :-----------------------------------: | :----------: | :--: | :--: | :--: | :----: |
|  1   |        `id`        |        使用对应数据库的内部 id        | varchar(255) | PRI  |  NO  |      |        |
|  2   |       `name`       |                                       | varchar(255) |      |  NO  |      |        |
|  3   | `publication_date` |              发表的年份               | varchar(255) |      |  NO  |      |        |
|  4   |      `impact`      | 影响力因子（TODO:目前不知道怎么获得） | varchar(255) |      |  NO  |      |        |


##### 6. paper_reference

注意，这里的reference是所有能够获得doi的文章，其他的reference被忽略；另外很可能这个doi不在爬取的范围内，既在paper表中没有这个rid。

| 序号 | 名称  |                             描述                             |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :---: | :----------------------------------------------------------: | :----------: | :--: | :--: | :--: | :----: |
|  1   | `pid` |                           paper id                           | varchar(255) | PRI  |  NO  |      |        |
|  2   | `rid` | reference paper id ( doi 对应的编号, 这个id可能不在 paper 表中 )/ | varchar(255) | PRI  |  NO  |      |        |

##### 7. paper_researcher

| 序号 |  名称   |     描述      |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :-----: | :-----------: | :----------: | :--: | :--: | :--: | :----: |
|  1   |  `pid`  |   paper id    | varchar(255) | PRI  |  NO  |      |        |
|  2   |  `rid`  | researcher id | varchar(255) | PRI  |  NO  |      |        |
|  3   | `order` |   第几作者    | varchar(255) |      |  NO  |      |        |

##### 8. paper_domain

| 序号 | 名称  |   描述    |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :---: | :-------: | :----------: | :--: | :--: | :--: | :----: |
|  1   | `pid` | paper id  | varchar(255) | PRI  |  NO  |      |        |
|  2   | `did` | domain id | varchar(255) | PRI  |  NO  |      |        |

##### 9. researcher_affiliation

代表某学者在某年在某机构发表了文章

| 序号 |  名称  |       描述       |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :----: | :--------------: | :----------: | :--: | :--: | :--: | :----: |
|  1   | `rid`  |  researcher id   | varchar(255) | PRI  |  NO  |      |        |
|  2   | `aid`  |  affiliation id  | varchar(255) | PRI  |  NO  |      |        |
|  3   | `year` | 在某年发表了文章 | varchar(255) | PRI  |  NO  |      |        |

##### *10. researcher_domain **弃用***

由于 researcher domain 就是某研究者的所有文章的 domain 的集合，故不在数据爬取时就进行保存这种冗余数据表。

| 序号 |  名称   |     描述      |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :-----: | :-----------: | :----------: | :--: | :--: | :--: | :----: |
|  1   |  `rid`  | researcher id | varchar(255) | PRI  |  NO  |      |        |
|  2   | `dname` |  domain name  | varchar(255) | PRI  |  NO  |      |        |

#####  11. paper_reference_citation

存储暂时只能获得citation的reference，用于之后的进一步爬取

| 序号 |         名称         |                          描述                           |     类型      |  键  | 为空 |      额外      | 默认值 |
| :--: | :------------------: | :-----------------------------------------------------: | :-----------: | :--: | :--: | :------------: | :----: |
|  1   |         `id`         | 自增id，没什么意义，只是由于citation比较长，无法作为key |      int      | PRI  |  NO  | auto_increment |        |
|  2   |        `pid`         |                                                         | varchar(255)  |      |  NO  |                |        |
|  3   | `reference_citation` |                                                         | varchar(4095) |      |  NO  |                |        |

##### 12.  paper_reference_title

存储暂时只能获得title的reference（存titile主要是因为IEEE给出的citation很奇怪，还不如title），用于之后的进一步爬取

| 序号 |       名称        |                         描述                         |     类型      |  键  | 为空 |      额外      | 默认值 |
| :--: | :---------------: | :--------------------------------------------------: | :-----------: | :--: | :--: | :------------: | :----: |
|  1   |       `id`        | 自增id，没什么意义，只是由于title比较长，无法作为key |      int      | PRI  |  NO  | auto_increment |        |
|  2   |       `pid`       |                                                      | varchar(255)  |      |  NO  |                |        |
|  3   | `reference_title` |                                                      | varchar(4095) |      |  NO  |                |        |

##### 13. paper_ieee_reference_document

存储暂时只能获得IEEE内部编号的reference，用于之后的进一步爬取

| 序号 |      名称       | 描述 |     类型     |  键  | 为空 | 额外 | 默认值 |
| :--: | :-------------: | :--: | :----------: | :--: | :--: | :--: | :----: |
|  1   |      `pid`      |      | varchar(255) | PRI  |  NO  |      |        |
|  2   | `ieee_document` |      | varchar(255) | PRI  |  NO  |      |        |

## 其他设置

### Log

log保存在 /scrapy_logs中

### Proxy

在proxies.txt中列出http代理的ip和端口号，自动随机切换代理。

格式为一行一个，ip:端口号

如果不需要代理则在settings中将rotating_proxies.middlewares.RotatingProxyMiddleware、rotating_proxies.middlewares.BanDetectionMiddleware两个中间件禁用

