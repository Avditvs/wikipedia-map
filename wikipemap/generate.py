import wikipemap.page as page
import requests
from bs4 import BeautifulSoup
from wikipemap.perf_counter import PerformanceCounter


def explore(wmap, page_name, page_vertex, depth=10):
    if page_vertex['visited'] is False:
        PerformanceCounter.start_metric("get")
        url = page.make_request_url(page_name, "fr")
        html_page = requests.get(url).content
        PerformanceCounter.end_metric("get")
        PerformanceCounter.start_metric("parse")
        parser = BeautifulSoup(html_page, "html.parser")
        PerformanceCounter.end_metric("parse")
        wmap.set_visited(page_vertex)
        links = page.get_page_links(parser)
        for link in links:
            link_vertex = wmap.get_node(link)
            if not link_vertex:
                link_vertex = wmap.add_page(link)
            wmap.add_link(page_vertex, link_vertex)
        wmap.page_explored(page_name)
        if depth > 0:
            for neighbor in wmap.get_neighbors(page_vertex, visited=False):
                explore(
                    wmap, neighbor["name"], neighbor, depth=depth - 1,
                )


def start_exploring(graph, page_name, depth=3):
    page_vertex = graph.add_page(page_name)
    explore(graph, page_name, page_vertex, depth=depth)
