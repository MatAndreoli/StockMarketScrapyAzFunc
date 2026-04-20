import json

from FIIsScraping.spiders.fiis_scraper import FiisScraperSpider
from FIIsScraping.spiders.stock_scraper import StockScraperSpider
from FIIsScraping.run_spiders import run_spider
from envs import FIIS_FILE, STOCKS_FILE


class HandlerResponse:
    """Platform-agnostic response object."""

    def __init__(self, body: str, status_code: int = 200, content_type: str = "application/json"):
        self.body = body
        self.status_code = status_code
        self.content_type = content_type


def handle_fiis(fiis_param: str | None) -> HandlerResponse:
    """Core logic for the /fiis endpoint."""
    if not fiis_param:
        return HandlerResponse("Pass a valid fiis param", status_code=400, content_type="text/plain")
    try:
        run_spider(FiisScraperSpider, fiis=fiis_param)
        with open(FIIS_FILE) as f:
            result = json.load(f)
        return HandlerResponse(json.dumps(result))
    except Exception as e:
        import traceback
        import logging
        logging.error(traceback.format_exc())
        return HandlerResponse(f"Some error occurred: {e}", status_code=500, content_type="text/plain")


def handle_stocks(stocks_param: str | None) -> HandlerResponse:
    """Core logic for the /stocks endpoint."""
    if not stocks_param:
        return HandlerResponse("Pass a valid stocks param", status_code=400, content_type="text/plain")
    try:
        run_spider(StockScraperSpider, stocks=stocks_param)
        with open(STOCKS_FILE) as f:
            result = json.load(f)
        return HandlerResponse(json.dumps(result))
    except Exception as e:
        return HandlerResponse(f"Some error occurred: {e}", status_code=500, content_type="text/plain")
