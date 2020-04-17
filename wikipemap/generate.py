import wikipemap.page as page
import requests
from wikipemap.perf_counter import PerformanceCounter
from lxml import html
from collections import deque

DEPTH = 1
RING = 0


def explore(wmap, page_name, page_vertex, depth=10, duplicate=False):
    if page_vertex["visited"] is False:
        html_page = request_page(page_name)
        PerformanceCounter.start_metric("parse")
        parser = html.fromstring(html_page)
        links = page.get_page_links(parser, duplicate)
        PerformanceCounter.end_metric("parse")
        wmap.set_visited(page_vertex)
        process_links(wmap, links, page_name, page_vertex)
        if depth > 0:
            for neighbor in wmap.get_neighbors(page_vertex, visited=False):
                explore(
                    wmap, neighbor["name"], neighbor, depth=depth - 1,
                )


def explore_ring(wmap, queue, page_vertex, n_sites, duplicate=False):
    n = 1
    while len(queue) > 0 and n < n_sites:
        link = queue.pop()
        vertex = wmap.get_node(link)
        if vertex['visited'] is False:
            page_html = request_page(link)
            PerformanceCounter.start_metric("parse")
            parser = html.fromstring(page_html)
            links = page.get_page_links(parser, duplicate)
            PerformanceCounter.end_metric("parse")
            n += 1
            wmap.set_visited(vertex)
            process_links(wmap, links, link, vertex)
            for neighbor in wmap.get_neighbors(vertex, visited=False):
                queue.append(neighbor["name"])


def request_page(page_name):
    PerformanceCounter.start_metric("get")
    url = page.make_request_url(page_name, "fr")
    html_page = requests.get(url).content
    PerformanceCounter.end_metric("get")
    return html_page


def process_links(wmap, links, current_page_name, page_vertex):
    PerformanceCounter.start_metric("process_links")
    for link in links:
        link_vertex = wmap.get_node(link)
        if not link_vertex:
            link_vertex = wmap.add_page(link)
        wmap.add_link(page_vertex, link_vertex)
    wmap.page_explored(current_page_name)
    PerformanceCounter.end_metric("process_links")


def start_exploring(graph, page_name, depth=3, method=DEPTH, n_sites=200):
    page_vertex = graph.add_page(page_name)
    if method == DEPTH:
        explore(graph, page_name, page_vertex, depth=depth)
    elif method == RING:
        queue = deque()
        vertex = graph.get_node(page_name)
        page_html = request_page(page_name)
        PerformanceCounter.start_metric("parse")
        parser = html.fromstring(page_html)
        links = page.get_page_links(parser, False)
        PerformanceCounter.end_metric("parse")
        graph.set_visited(vertex)
        process_links(graph, links, page_name, vertex)
        for neighbor in graph.get_neighbors(vertex, visited=False):
            queue.append(neighbor["name"])
        explore_ring(graph, queue, vertex, n_sites)
