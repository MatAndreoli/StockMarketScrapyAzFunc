from scrapy import Spider
from scrapy.responsetypes import Response

from envs import STOCKS_FILE
from FIIsScraping.items import StockScrapingItem

class StockScraperSpider(Spider):
    name = "stock-scraper"
    
    format_file = 'json'
    custom_settings = {
        'FEEDS':{
            STOCKS_FILE: { 'format': format_file, 'overwrite': True}
        },
        'ITEM_PIPELINES': {
            "FIIsScraping.pipelines.StocksScrapingPipeline": 300,
        }
    }

    def __init__(self, stocks='', *args, **kwargs):
        super(StockScraperSpider, self).__init__(*args, **kwargs)
        self.stocks = stocks

        self.start_urls = ["https://investidor10.com.br"]

    def parse(self, response: Response):
        for stock in self.stocks.split(','):
            url = f"https://investidor10.com.br/acoes/{stock}/"
            yield response.follow(url, callback=self.getStockData)

    def getStockData(self, response: Response):
        stock_item = StockScrapingItem()

        stock_item['url'] = response.url
        stock_item['name'] = response.css('#header_action .name-ticker h2::text').get()
        stock_item['code'] = stock_item.get('url').split('/')[-2].upper()

        cards_ticker = response.css('.container #cards-ticker')
        stock_item['status'] = cards_ticker.css('.pl ._card-body div span::text').get()
        stock_item['current_price'] = cards_ticker.css('.cotacao ._card-body div .value::text').get()
        stock_item['p_l'] = cards_ticker.css('.val ._card-body span::text').get()
        stock_item['p_vp'] = cards_ticker.css('.vp ._card-body span::text').get()
        stock_item['dividend_yield'] = cards_ticker.css('.dy ._card-body span::text').get()

        indicators_table = response.css('.content #container-multi-medias  #table-indicators ')
        stock_item['roe'] = indicators_table.css('.cell:nth-child(20) > div.value span::text').get()
        stock_item['net_debt_ebitda'] = indicators_table.css('.cell:nth-child(24) > div.value span::text').get()
        stock_item['cagr'] = indicators_table.css('.cell:nth-child(31) > div.value span::text').get()

        xpath_code = '//span[@class="title" and text()="%s"]/following-sibling::span//div[@class="simple-value"]/text()'
        about_company_table = response.css('.container #about-company #info_about .content #table-indicators-company')
        stock_item['average_daily'] = about_company_table.xpath(xpath_code.replace('%s', 'Liquidez Média Diária')).get()
        stock_item['net_worth'] = about_company_table.xpath(xpath_code.replace('%s', 'Patrimônio Líquido')).get()
        stock_item['total_stock_paper'] = about_company_table.xpath(xpath_code.replace('%s', 'Nº total de papeis')).get()

        xpath_code_sector = '//a[span[@class="title" and text()="%s"]]//span[@class="value"]/text()'
        values = []
        values.append(about_company_table.xpath(xpath_code_sector.replace('%s', 'Setor')).get())
        values.append(about_company_table.xpath(xpath_code_sector.replace('%s', 'Segmento')).get())
        stock_item['operation_sector'] = ' - '.join(values)

        yield stock_item
