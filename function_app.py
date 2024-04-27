import json
import scrapy.crawler as crawler
import azure.functions as func
from twisted.internet import reactor
from multiprocessing import Process, Queue

from envs import FILE_PATH
from FIIsScraping.spiders.fiis_scraper import FiisScraperSpider


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="fiis")
def get_fiis(req: func.HttpRequest) -> func.HttpResponse:
    try:
        fiis = req.params.get('fiis')
        if fiis:
            run_spider(FiisScraperSpider, fiis)
            with open(FILE_PATH) as fiis_file:
                fiis_result = json.load(fiis_file)

            return func.HttpResponse(json.dumps(fiis_result), mimetype="application/json")
        return func.HttpResponse('Pass a valid fiis param', status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Some error occurred: {e}", status_code=500)


def run_spider(spider, fiis):
    def run_process(queue):
        try:
            runner = crawler.CrawlerRunner()
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
