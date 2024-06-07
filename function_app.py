import json

from azure.functions import HttpResponse, HttpRequest, FunctionApp, AuthLevel

from envs import FIIS_FILE, STOCKS_FILE
from FIIsScraping.spiders.fiis_scraper import FiisScraperSpider
from FIIsScraping.spiders.stock_scraper import StockScraperSpider
from FIIsScraping.run_spiders import run_spider

app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)


@app.route(route="fiis")
def get_fiis(req: HttpRequest) -> HttpResponse:
    try:
        fiis = req.params.get('fiis')
        if fiis:
            run_spider(FiisScraperSpider, fiis=fiis)
            with open(FIIS_FILE) as fiis_file:
                fiis_result = json.load(fiis_file)

            return HttpResponse(json.dumps(fiis_result), mimetype="application/json")
        return HttpResponse('Pass a valid fiis param', status_code=400)
    except Exception as e:
        return HttpResponse(f"Some error occurred: {e}", status_code=500)


@app.route(route="stocks")
def get_stocks(req: HttpRequest) -> HttpResponse:
    try:
        stocks = req.params.get('stocks')
        if stocks:
            run_spider(StockScraperSpider, stocks=stocks)
            with open(STOCKS_FILE) as stocks_file:
                stocks_result = json.load(stocks_file)

            return HttpResponse(json.dumps(stocks_result), mimetype="application/json")
        return HttpResponse('Pass a valid stocks param', status_code=400)
    except Exception as e:
        return HttpResponse(f"Some error occurred: {e}", status_code=500)
