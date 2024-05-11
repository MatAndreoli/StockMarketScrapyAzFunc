import tempfile
from scrapy import Spider, Request
from scrapy.responsetypes import Response

from envs import FILE_PATH
from FIIsScraping.items import FiisscrapingItem, RendDistribution, LastManagementReport


class FiisScraperSpider(Spider):
    name = "fiis-scraper"

    format_file = 'json'
    custom_settings = {
        'FEEDS':{
            FILE_PATH: { 'format': format_file, 'overwrite': True}
        },
        'ITEM_PIPELINES': {
            "FIIsScraping.pipelines.FiisscrapingPipeline": 300,
        }
    }

    def __init__(self, fiis='', *args, **kwargs):
        super(FiisScraperSpider, self).__init__(*args, **kwargs)
        self.fiis = fiis

        self.start_urls = ["https://www.fundsexplorer.com.br/funds"]


    def parse(self, response: Response):
        for fii in self.fiis.split(','):

            url = f'https://www.fundsexplorer.com.br/funds/{fii}'
            type_css = f'.link-tickers-container[onclick="location.href=\'{url}\';"] span::text'
            fii_type = response.css(type_css).get()

            yield response.follow(url, callback=self.getFiiData, meta={'fii_type': fii_type})


    def getFiiData(self, response: Response):
        fii_type = response.meta['fii_type']

        fii_item = FiisscrapingItem()
        rend_distribution = RendDistribution()
        last_management_report = LastManagementReport()

        fii_item['url'] = response.url
        fii_item['fii_type'] = fii_type

        fii_item['name'] = response.css('.headerTicker__content__name::text').get()
        fii_item['code'] = response.css('.headerTicker__content__title::text').get()
        fii_item['status'] = response.css('.headerTicker__content__price span::text').get()
        fii_item['current_price'] = response.css('.headerTicker__content__price p::text').get()
        
        fii_data = response.css('.indicators:nth-child(1)')
        fii_item['average_daily'] = fii_data.css('.indicators__box:nth-child(1) p b::text').get()
        fii_item['last_dividend'] = fii_data.css('.indicators__box:nth-child(2) p b::text').get()
        fii_item['dividend_yield'] = fii_data.css('.indicators__box:nth-child(3) p b::text').get()
        fii_item['net_worth'] = fii_data.css('.indicators__box:nth-child(4) p:nth-child(2) b').get()
        fii_item['p_vp'] = fii_data.css('.indicators__box:nth-child(7) p b::text').get()
        
        fii_historic_data = response.css('.historic')
        fii_item['last_dividend_yield'] = fii_historic_data.css('div:nth-child(2) p:nth-child(2) b::text').get()

        last_rend_distribution = response.css('.communicated .communicated__grid .communicated__grid__rend') or None
        
        if last_rend_distribution is not None:
            rend_distribution['dividend'] = last_rend_distribution[0].css('p::text').get()
            rend_distribution['future_pay_day'] = last_rend_distribution[0].css('p::text').get()
            rend_distribution['income_percentage'] = last_rend_distribution[0].css('ul li:nth-child(3) b::text').get()
            rend_distribution['data_com'] = last_rend_distribution[0].css('ul li:nth-child(1) b::text').get()
            fii_item['rend_distribution'] = dict(rend_distribution)

        last_management_report_el = response.xpath("//div[contains(@class, 'communicated__grid__row') and contains(a/@href, 'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=') and contains(a/text(), 'Gerencial')]") or None

        if last_management_report_el is not None:
            last_management_report['link'] = last_management_report_el[0].css('a::attr(href)').get()
            last_management_report['date'] = last_management_report_el[0].css('p::text').get()
            fii_item['last_management_report'] = dict(last_management_report)
        else:
            yield response.follow(f"https://statusinvest.com.br/fiagros/{fii_item['code']}", callback=self.managementReportAbsent, meta={'fii_item': fii_item})
            return

        yield fii_item

    def managementReportAbsent(self, response: Response):
        fii_item = response.meta['fii_item']
        last_management_report = LastManagementReport()

        last_management_report_el = response.xpath("//div[contains(@class, 'align-items-center d-flex flex-wrap justify-between') and contains(div/text(), 'Gerencial')]") or None

        if last_management_report_el is not None:
            last_management_report['link'] = last_management_report_el[0].css('a::attr(href)').get()
            last_management_report['date'] = last_management_report_el[0].css('.w-lg-10.fw-700::text').get()
            fii_item['last_management_report'] = dict(last_management_report)

        yield fii_item
