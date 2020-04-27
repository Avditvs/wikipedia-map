import urllib.parse as urlparse
import re
from wikipemap.perf_counter import PerformanceCounter
from enum import Enum
from igraph import OUT

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
        self.links = set()
        self.links = {
            urlparse.unquote(h[2])
            for h in HTML_TAG_REGEX.findall(self.content)
        }
        self.content = None
        self.state = State.PARSED

    @PerformanceCounter.timed("process_links")
    def process_links(self):
        self.state = State.COMPLETING

        def target_generator():
            for link in self.links:
                yield (
                    self.vertex,
                    self.graph.get_node(link).vertex
                    if self.graph.get_node(link)
                    else Page(link, self.graph).vertex,
                )

        self.graph.add_links(len(self.links), target_generator())
        self.graph.page_explored(self.link)
        self.state = State.COMPLETED

    @PerformanceCounter.timed("get_neighbors")
    def get_neighbors(self, visited=False):
        return [
            n["page"]
            for n in self.vertex.neighbors(mode=OUT)
            if n["page"].visited is visited
        ]

    def enqueued(self, queue):
        if self.state != State.ENQUEUED:
            self.state = State.ENQUEUED
            queue.put(self)
