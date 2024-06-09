from scrapy import Spider
from scrapy.responsetypes import Response

from envs import STOCKS_FILE
from FIIsScraping.items import StockScrapingItem, DividendItem, LastManagementReport

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

        cards_xpath = '//div[div[contains(@class, "_card-header") and div/span[@title="%s"]]]/div[@class="_card-body"]//span/text()'
        stock_item['status'] = response.xpath(self.replace_xpath(cards_xpath, 'VARIAÇÃO (12M)')).get()
        stock_item['current_price'] = response.xpath(self.replace_xpath(cards_xpath, 'Cotação')).get()
        stock_item['p_l'] = response.xpath(self.replace_xpath(cards_xpath, 'P/L')).get()
        stock_item['p_vp'] = response.xpath(self.replace_xpath(cards_xpath, 'P/VP')).get()
        stock_item['dividend_yield'] = response.xpath(self.replace_xpath(cards_xpath, 'DY')).get()

        indicator_xpath = '//div[@id="table-indicators"]/div[@class="cell" and span[text()="%s "]]/div[contains(@class, "value")]/span/text()'
        stock_item['roe'] = response.xpath(self.replace_xpath(indicator_xpath, 'ROE')).get()
        stock_item['net_debt_ebitda'] = response.xpath(self.replace_xpath(indicator_xpath, 'DÍVIDA LÍQUIDA / EBITDA')).get()
        stock_item['cagr'] = response.xpath(self.replace_xpath(indicator_xpath, 'CAGR LUCROS 5 ANOS')).get()

        about_xpath = '//div[@id="table-indicators-company"]//span[@class="title" and text()="%s"]/following-sibling::span//div[@class="simple-value"]/text()'
        stock_item['average_daily'] = response.xpath(self.replace_xpath(about_xpath, 'Liquidez Média Diária')).get()
        stock_item['net_worth'] = response.xpath(self.replace_xpath(about_xpath, 'Patrimônio Líquido')).get()
        stock_item['total_stock_paper'] = response.xpath(self.replace_xpath(about_xpath, 'Nº total de papeis')).get()

        xpath_code_sector = '//div[@id="table-indicators-company"]//a[span[@class="title" and text()="%s"]]//span[@class="value"]/text()'
        values = []
        values.append(response.xpath(self.replace_xpath(xpath_code_sector, 'Setor')).get())
        values.append(response.xpath(self.replace_xpath(xpath_code_sector, 'Segmento')).get())
        stock_item['operation_sector'] = ' - '.join(values)
        
        self.get_dividends_history(response, stock_item)
        
        report_url = f'https://www.fundamentus.com.br/resultados_trimestrais.php?papel={stock_item["code"]}'
        yield response.follow(report_url, callback=self.get_management_reports, meta={'stock_item': stock_item}, errback=self.error_handler)


    def get_dividends_history(self, response: Response, stock_item):
        dividend_history = []
        count = 0
        dividends_rows = response.css('#table-dividends-history tbody tr')
        for row in dividends_rows:
            if count >= 10:
                break
            values = []
            for cell in row.css('td'):
                values.append(cell.css('::text').get())
            count += 1

            dividend_item = DividendItem()

            dividend_item['type'] = values[0]
            dividend_item['data_com'] = values[1]
            dividend_item['pay_day'] = values[2]
            dividend_item['value'] = str(round(float(values[3].strip().replace(',', '.')), 4))
            
            dividend_history.append(dividend_item)

        stock_item['dividends_history'] = list(dividend_history)


    def get_management_reports(self, response: Response):
        stock_item = response.meta['stock_item']

        reports_table = response.css('table tbody tr:nth-child(1)')

        item = LastManagementReport()
        item['link'] = reports_table.css('td:nth-child(3) a::attr(href)').get()
        item['date'] = reports_table.css('td:nth-child(1) span::text').get()

        stock_item['last_management_report'] = item
        stock_item['reports_link'] = response.url
        yield stock_item


    def error_handler(self, failure):
        request = failure.request
        stock_item = request.meta['stock_item']

        self.logger.error(f"Error on {request.url}: {failure.value}")
        stock_item['reports_link'] = request.url
        yield stock_item


    def replace_xpath(self, xpath_code, value):
        return xpath_code.replace('%s', value)
