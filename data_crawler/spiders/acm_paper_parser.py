import scrapy
from data_crawler.items import ACMPaperItem

from data_crawler.spiders.utils import remove_prefix, NoPrefixException

def parse_acm_paper(spider, response):
    def parse_index_tree(selector):
        """传入一个树的select，返回树的json
        """
        # 前置条件：根节点存在（selector.get() != None）。对根结点没关系
        result = {}
        result['title'] = selector.xpath('./div/p/a/text()').get() or selector.xpath('./h6/text()').get()
        result['url'] = 'https://dl.acm.org/' + selector.xpath('./div/p/a/@href').get()
        child = []
        for child_html in selector.xpath('./ol[contains(@class, hasNodes)]/li').getall():
            child.append(parse_index_tree(scrapy.Selector(text=child_html).xpath('./body/li')))
        result['child'] = child
        return result

    # 结果的对象
    result = ACMPaperItem()
    paper = response.xpath('//article')

    result['title'] = paper.xpath('.//div[@class="citation"]//h1[@class="citation__title"]/text()').get()

    # authors
    result['authors'] = []
    authors = paper.xpath('.//div[@class="citation"]//div[@id="sb-1"]/ul/li[@class="loa__item"]')
    for author in authors:
        result_author = {
            'author_name': author.xpath('.//span[@class="loa__author-name"]/span/text()').get(),
            'author_profile': author.xpath('//div[@class="author-info"]//div[@class="author-info__body"]/a/@href').get(),
            'affiliation': author.xpath('.//div[@class="author-info__body"]/p/text()').getall()
        }
        result['authors'].append(result_author)

    # 获得发表的相关信息
    publication = paper.xpath('.//div[@class="issue-item__detail"]')

    # 会议名和会议doi
    try:
        conference = {
            'conference_title': publication.xpath('./a/@title').get(), 
            'conference_doi': remove_prefix(publication.xpath('./a/@href').get(), '/doi/proceedings/')
        }
    except NoPrefixException as e:
        # conference的doi如果不包含这个前缀的话，全部保存并发出warning。
        spider.logger.warning('conference doi without prefix \'/doi/proceedings/\', got %s, saved as doi instead' % e.args[0])
        conference = {
            'conference_title': publication.xpath('./a/@title').get(), 
            'conference_doi': publication.xpath('./a/@href').get()
        }
    result['conference'] = conference

    # paper发表年月
    result['month_year'] = publication.xpath('.//span[@class="epub-section__date"]/text()').get()

    # paper doi
    try:
        result['doi'] = remove_prefix(publication.xpath('.//a[@class="issue-item__doi"]/@href').get(), 'https://doi.org/')
    except NoPrefixException as e:
        spider.logger.warning('paper doi without prefix \'/doi/proceedings/\', got %s, saved as doi instead' % e.args[0])
        result['doi'] = publication.xpath('.//a[@class="issue-item__doi"]/@href').get()

    # paper abstract
    result['abstract'] = paper.xpath('.//div[@class="abstractSection abstractInFull"]/p/text()').get()
    
    # paper references
    references_selectors = paper.xpath('.//div[contains(@class, "article__references")]/ol[contains(@class, "references__list")]/li/span[@class="references__note"]')
    result['references'] = [
        {
            'reference_citation': reference.xpath('./text()').get(),
            'reference_links': [{
                    'link_type': link.xpath('./span[@class="visibility-hidden"]/text()').get(),
                    'link_url': link.xpath('./@href').get()
                }
                for link in reference.xpath('./span[@class="references__suffix"]/a')
            ]
        } for reference in references_selectors
    ]

    # index term
    root_selector = response.xpath('.//ol[@class="rlist organizational-chart"]/li')
    result['index_term_tree'] = {
        'title': root_selector.xpath('./h6/text()').get(),
        'url': None,
        'child': [parse_index_tree(scrapy.Selector(text=tree_html).xpath('./body/li')) for tree_html in root_selector.xpath('./ol/li').getall()]
    }

    # metric citation number
    result['citation'] = response.xpath('//span[@class="citation"]/span/text()').get()

    spider.logger.info("paper crawled, doi: {}".format(result['doi']))
    return result
    