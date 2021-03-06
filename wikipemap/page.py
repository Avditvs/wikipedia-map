import urllib.parse as urlparse
import re
from wikipemap.perf_counter import PerformanceCounter
from enum import Enum

HTML_TAG_REGEX = re.compile(
    r"<a href=([\'\"])(\/wiki\/)([^:#]*?)\1", re.IGNORECASE
)


class State(Enum):
    NEW = 0
    ENQUEUED = 1
    FETCHING = 2
    FETCHED = 3
    PARSING = 4
    PARSED = 5
    COMPLETING = 6
    COMPLETED = 10


class Page:
    @PerformanceCounter.timed("add_page")
    def __init__(self, link, graph):
        self.link = link
        self.state = State.NEW
        self.locale = "fr"
        self.content = ""
        self.graph = graph
        self.vertex = graph.add_page(self)
        self.visited = False

    @PerformanceCounter.timed("get")
    def make_request(self, session):
        self.state = State.FETCHING
        self.content = session.get(self._make_request_url()).text
        self.state = State.FETCHED

    def _make_request_url(self):
        return "https://{}.wikipedia.org/wiki/{}".format(
            self.locale, self.link
        )

    @PerformanceCounter.timed("parse")
    def make_page_links(self):
        self.state = State.PARSING
        try:
            self.links = {
                urlparse.unquote(h[2])
                for h in HTML_TAG_REGEX.findall(self.content)
            }
        except TypeError:
            print(self.link)
            raise TypeError()
        self.content = None
        self.state = State.PARSED

    @PerformanceCounter.timed("process_links")
    def process_links(self):
        self.state = State.COMPLETING

        def target_generator():
            for link in self.links:
                v = self.graph.get_node(link)
                yield (
                    self.vertex,
                    v.vertex if v else Page(link, self.graph).vertex,
                )

        self.graph.add_links(target_generator())
        self.graph.page_explored(self.link)
        self.state = State.COMPLETED

    @PerformanceCounter.timed("get_neighbors")
    def get_neighbors(self, visited=False):
        return [
            self.graph.page_prop[n]
            for n in self.vertex.out_neighbors()
            if self.graph.page_prop[n].visited is visited
        ]

    def enqueued(self, queue):
        if self.state != State.ENQUEUED:
            self.state = State.ENQUEUED
            queue.put(self)
