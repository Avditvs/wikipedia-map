import urllib.parse as urlparse
import re
import requests
from lxml import html
from enum import Enum


class State(Enum):
    NEW = 0
    FETCHING = 1
    FETCHED = 2
    PARSING = 3
    PARSED = 4
    COMPLETING = 5
    COMPLETED = 10


class Page:
    def __init__(self, link, graph):
        self.link = link
        self.state = State.NEW
        self.locale = "fr"
        self.content = ""
        self.graph = graph
        self.vertex = graph.add_page(self)

    def make_request(self):
        self.state = State.FETCHING
        self.content = requests.get(self._make_request_url()).content
        self.state = State.FETCHED

    def _make_request_url(self):
        return "https://{}.wikipedia.org/wiki/{}".format(
            self.locale, self.link
        )

    def make_page_links(self):
        parser = html.fromstring(self.content)
        self.state = State.PARSING
        self.links = set()
        for h in parser.xpath(
            "//div[@id = '{}']//a/@href".format("mw-content-text")
        ):
            h = urlparse.unquote(h)
            if "#" not in h and ":" not in h and re.match("^/wiki/.*", h):
                self.links.add(h.split("/")[2])
        self.state = State.PARSED

    def process_links(self):
        self.state = State.COMPLETING
        for link in self.links:
            target_page = self.graph.get_node(link)
            if not target_page:
                target_page = Page(link, self.graph)
            self.graph.add_link(self.vertex, target_page.vertex)
        self.graph.page_explored(self.link)
