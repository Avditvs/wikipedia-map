import wikipemap.page as page
import requests
from bs4 import BeautifulSoup
from wikipemap.perf_counter import PerformanceCounter


def explore(wmap, page_name, page_vertex, depth=10):
    PerformanceCounter.start_metric("get")
    url = page.make_request_url(page_name, "fr")
    html_page = requests.get(url).content
    parser = BeautifulSoup(html_page, "html.parser")
    wmap.set_visited(page_vertex)
    links = page.get_page_links(parser)
    PerformanceCounter.end_metric("get")
    for link in links:
        link_vertex = wmap.get_node(link)
        if not link_vertex:
            link_vertex = wmap.add_page(link)
        wmap.add_link(page_vertex, link_vertex)
    wmap.page_explored()
    if depth > 0:
        for neighbor in wmap.get_neighbors(page_vertex, visited=False):
            explore(
                wmap, neighbor["name"], neighbor, depth=depth - 1,
            )


def start_exploring(graph, page_name, depth=3):
    page_vertex = graph.add_page(page_name)
    explore(graph, page_name, page_vertex, depth=depth)
