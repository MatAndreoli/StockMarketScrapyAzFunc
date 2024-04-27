from scrapy import Item, Field


class RendDistribution(Item):
    future_pay_day = Field()
    dividend = Field()
    income_percentage = Field()
    data_com = Field()


class LastManagementReport(Item):
    link = Field()
    date = Field()


class FiisscrapingItem(Item):
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

