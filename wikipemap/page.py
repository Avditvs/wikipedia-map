import urllib.parse as urlparse
import re
import requests
from lxml import html
from wikipemap.perf_counter import PerformanceCounter
from enum import Enum
from igraph import OUT


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

    @property
    def visited(self):
        return self.vertex["visited"]

    @visited.setter
    def visited(self, visited):
        self.vertex["visited"] = visited

    @PerformanceCounter.timed("get")
    def make_request(self):
        self.state = State.FETCHING
        self.content = requests.get(self._make_request_url()).content
        self.state = State.FETCHED

    def _make_request_url(self):
        return "https://{}.wikipedia.org/wiki/{}".format(
            self.locale, self.link
        )

    @PerformanceCounter.timed("parse")
    def make_page_links(self):
        self.state = State.PARSING
        parser = html.fromstring(self.content)
        self.links = set()
        for h in parser.xpath(
            "//div[@id = '{}']//a/@href".format("mw-content-text")
        ):
            h = urlparse.unquote(h)
            if "#" not in h and ":" not in h and re.match("^/wiki/.*", h):
                self.links.add(h.split("/")[2])
        self.state = State.PARSED

    @PerformanceCounter.timed("process_links")
    def process_links(self):
        self.state = State.COMPLETING
        for link in self.links:
            target_page = self.graph.get_node(link)
            if not target_page:
                target_page = Page(link, self.graph)
            self.graph.add_link(self.vertex, target_page.vertex)
        self.graph.page_explored(self.link)
        self.state = State.COMPLETED

    @PerformanceCounter.timed("get_neighbors")
    def get_neighbors(self, visited=False):
        neighbors = self.vertex.neighbors(mode=OUT)
        neighbors = [n["page"] for n in neighbors if n["visited"] is visited]
        return neighbors

    def enqueued(self, queue):
        if self.state != State.ENQUEUED:
            self.state = State.ENQUEUED
            queue.put(self)
