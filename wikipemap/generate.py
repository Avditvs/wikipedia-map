from wikipemap.page import Page
from collections import deque

DEPTH = 1
RING = 0


def explore(wmap, page, depth=10, duplicate=False):
    if page.vertex["visited"] is False:
        page.make_request()
        page.make_page_links()
        page.set_visited()
        page.process_links()
        if depth > 0:
            for neighbor in wmap.get_neighbors(page, visited=False):
                explore(
                    wmap, neighbor["page"], depth=depth - 1,
                )


def explore_ring(queue, page, n_sites, duplicate=False):
    n = 1
    while len(queue) > 0 and n < n_sites:
        link = queue.pop()
        if link.vertex["visited"] is False:
            link.make_request()
            link.make_page_links()
            n += 1
            link.set_visited()
            link.process_links()
            for neighbor in link.graph.get_neighbors(link, visited=False):
                page = neighbor["page"]
                page.enqueued(queue)


def start_exploring(graph, page_name, depth=3, method=DEPTH, n_sites=200):
    page = Page(page_name, graph)
    if method == DEPTH:
        explore(graph, page, depth=depth)
    elif method == RING:
        queue = deque()
        page = Page(page_name, graph)
        page.make_request()
        page.make_page_links()
        page.set_visited()
        page.process_links()
        for neighbor in graph.get_neighbors(page, visited=False):
            queue.append(neighbor["page"])
        explore_ring(queue, page, n_sites)
