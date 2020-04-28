from threading import Thread, Event
from wikipemap.page import State, Page
from queue import Queue, Empty
import time
from requests import Session


class HTTPRequestsWorker(Thread):
    def __init__(self, download_queue, process_queue, num_requests=100):
        super(HTTPRequestsWorker, self).__init__()
        self.session = Session()
        self.download_queue = download_queue
        self.process_queue = process_queue
        self.num_requests = num_requests
        self.n = 0
        print("HTTPRequestsWorker started")

    def run(self):
        self.refill = True
        while not self.download_queue.empty() and self.n <= self.num_requests:
            link = self.download_queue.get()
            if link.state == State.ENQUEUED:
                self.n += 1
                link.make_request(self.session)
                self.process_queue.put(link)
        self.session.close()


class LinksProcessingWorker(Thread):
    def __init__(self, process_queue, download_queue):
        super(LinksProcessingWorker, self).__init__()
        self.process_queue = process_queue
        self.download_queue = download_queue
        self.stop_event = Event()
        print("LinksProcessingWorker started")

    def stop(self):
        self.stop_event.set()

    def run(self):
        try:
            while not self.stop_event.isSet():
                link = self.process_queue.get(timeout=1)
                link.make_page_links()
                link.process_links()
                link.visited = True
                for neighbor in link.get_neighbors(visited=False):
                    neighbor.enqueued(self.download_queue)
        except Empty:
            pass


def start_exploring(
    graph,
    page_name,
    n_sites=300,
    n_download_threads=5,
    n_processing_threads=1,
    buffer_size=100,
):
    download_queue = Queue()
    process_queue = Queue(buffer_size)
    session = Session()

    page = Page(page_name, graph)
    page.make_request(session)
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

    for t in download_threads:
        t.join()

    for t in process_threads:
        t.stop()
        t.join()
