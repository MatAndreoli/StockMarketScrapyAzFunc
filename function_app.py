import json

from scrapy.crawler import CrawlerRunner
from azure.functions import HttpResponse, HttpRequest, FunctionApp, AuthLevel
from twisted.internet import reactor
from multiprocessing import Process, Queue

from envs import FILE_PATH
from FIIsScraping.spiders.fiis_scraper import FiisScraperSpider


app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)

@app.route(route="fiis")
def get_fiis(req: HttpRequest) -> HttpResponse:
    try:
        fiis = req.params.get('fiis')
        if fiis:
            run_spider(FiisScraperSpider, fiis)
            with open(FILE_PATH) as fiis_file:
                fiis_result = json.load(fiis_file)

            return HttpResponse(json.dumps(fiis_result), mimetype="application/json")
        return HttpResponse('Pass a valid fiis param', status_code=400)
    except Exception as e:
        return HttpResponse(f"Some error occurred: {e}", status_code=500)


def run_spider(spider, fiis):
    def run_process(queue):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider, fiis=fiis)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            queue.put(None)
        except Exception as e:
            queue.put(e)

    queue = Queue()
    process = Process(target=run_process, args=(queue,))
    process.start()
    result = queue.get()
    process.join()

    if result is not None:
        raise result
