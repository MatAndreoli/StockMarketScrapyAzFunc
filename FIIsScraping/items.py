from scrapy import Item, Field


class RendDistribution(Item):
    future_pay_day = Field()
    dividend = Field()
    income_percentage = Field()
    data_com = Field()


class LastManagementReport(Item):
    link = Field()
    date = Field()


class FiisScrapingItem(Item):
    url = Field()
    name = Field()
    fii_type = Field()
    code = Field()
    status = Field()
    current_price = Field()
    average_daily = Field()
    last_dividend = Field()
    dividend_yield = Field()
    last_dividend_yield = Field()
    net_worth = Field()
    p_vp = Field()
    last_dividend_table = Field()
    rend_distribution = Field()
    last_management_report = Field()
    reports_link = Field()


class DividendItem(Item):
    type = Field()
    data_com = Field()
    pay_day = Field()
    value = Field()


class StockScrapingItem(Item):
    url = Field()
    name = Field()
    operation_sector = Field()
    code = Field()
    status = Field() # last 12 months
    current_price = Field()
    average_daily = Field()
    dividend_yield = Field()
    net_worth = Field()
    p_vp = Field()
    p_l = Field()
    net_debt_ebitda = Field() # dívida líquida / ebitda
    cagr = Field()
    roe = Field()
    total_stock_paper = Field()
    dividends_history = Field()
    last_management_report = Field()
    reports_link = Field()
