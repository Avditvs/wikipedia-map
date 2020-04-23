from threading import Thread
from wikipemap.page import State, Page
from queue import Queue
import time


class HTTPRequestsWorker(Thread):
    def __init__(self, download_queue, process_queue, num_requests=100):
        super(HTTPRequestsWorker, self).__init__()
        self.download_queue = download_queue
        self.process_queue = process_queue
        self.num_requests = num_requests
        self.n = 0
        print("HTTPRequestsWorker started")

    def run(self):
        while not self.download_queue.empty() and self.n < self.num_requests:
            link = self.download_queue.get()
            if link.state == State.ENQUEUED:
                self.n += 1
                link.make_request()
                self.process_queue.put(link)


class LinksProcessingWorker(Thread):
    def __init__(self, process_queue, download_queue):
        super(LinksProcessingWorker, self).__init__()
        self.process_queue = process_queue
        self.download_queue = download_queue
        print("LinksProcessingWorker started")

    def run(self):

        while True:
            link = self.process_queue.get()
            link.make_page_links()
            link.process_links()
            link.visited = True
            for neighbor in link.get_neighbors(visited=False):
                neighbor.enqueued(self.download_queue)


def start_exploring(
    graph, page_name, n_sites=300, n_download_threads=5, n_processing_threads=1
):
    download_queue = Queue()
    process_queue = Queue()

    page = Page(page_name, graph)
    page.make_request()
    page.make_page_links()
    page.process_links()
    page.visited = True
    for neighbor in page.get_neighbors(visited=False):
        neighbor.enqueued(download_queue)

    download_threads = [
        HTTPRequestsWorker(
            download_queue,
            process_queue,
            num_requests=n_sites // n_download_threads,
        )
        for i in range(n_download_threads)
    ]

    time.sleep(2)
    process_threads = [
        LinksProcessingWorker(process_queue, download_queue)
        for i in range(n_processing_threads)
    ]

    for t in download_threads:
        t.start()

    for t in process_threads:
        t.start()
