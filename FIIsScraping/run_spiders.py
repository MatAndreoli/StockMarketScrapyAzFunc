from fake_useragent import UserAgent
from twisted.internet import reactor

from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Queue

def run_spider(spider, **kwargs):
    def run_process(queue):
        try:
            process = CrawlerProcess({
                'USER_AGENT': UserAgent().random,
                'LEVEL_LOG': 'VERBOSE'
            })
            deferred = process.crawl(spider, **kwargs)
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
