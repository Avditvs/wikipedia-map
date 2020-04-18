from wikipemap.page import Page
from collections import deque

DEPTH = 1
RING = 0


def explore(wmap, page, depth=10, duplicate=False):
    if page.visited is False:
        page.make_request()
        page.make_page_links()
        page.process_links()
        page.visited = True
        if depth > 0:
            for neighbor in page.get_neighbors(visited=False):
                explore(
                    wmap, neighbor, depth=depth - 1,
                )


def explore_ring(queue, page, n_sites, duplicate=False):
    n = 1
    while len(queue) > 0 and n < n_sites:
        link = queue.pop()
        if link.visited is False:
            link.make_request()
            link.make_page_links()
            n += 1
            link.process_links()
            link.visited = True
            for neighbor in link.get_neighbors(visited=False):
                neighbor.enqueued(queue)


def start_exploring(graph, page_name, depth=3, method=DEPTH, n_sites=200):
    page = Page(page_name, graph)
    if method == DEPTH:
        explore(graph, page, depth=depth)
    elif method == RING:
        queue = deque()
        page = Page(page_name, graph)
        page.make_request()
        page.make_page_links()
        page.process_links()
        page.visited = True
        for neighbor in page.get_neighbors(visited=False):
            queue.append(neighbor)
        explore_ring(queue, page, n_sites)
