from fake_useragent import UserAgent
from twisted.internet import reactor

from scrapy.crawler import CrawlerProcess
from multiprocessing import Process, Pipe

def run_spider(spider, **kwargs):
    def run_process(conn):
        try:
            process = CrawlerProcess({
                'USER_AGENT': UserAgent().random,
                'LEVEL_LOG': 'VERBOSE'
            })
            deferred = process.crawl(spider, **kwargs)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            conn.send(None)
        except Exception as e:
            conn.send(e)
        finally:
            conn.close()
    
    parent_conn, child_conn = Pipe()
    process = Process(target=run_process, args=(child_conn,))
    process.start()
    result = parent_conn.recv()
    process.join()
    
    if result is not None:
        raise result
