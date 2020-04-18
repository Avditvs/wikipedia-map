from igraph import Graph, OUT
from IPython.display import display, clear_output
from wikipemap.perf_counter import PerformanceCounter


class WikipediaMap:
    def __init__(self, name, verbose=True, use_lookup=True):
        self.graph = Graph(directed=True)
        self.name = name
        self.graph["name"] = name
        self.explored_pages = 0
        self.registered_pages = 0
        self.verbose = verbose
        self.created_links = 0
        self.use_lookup = use_lookup
        self.lookup_table = {}

    def page_explored(self, page_name):
        self.explored_pages += 1
        if self.verbose is True:
            clear_output()
            display(
                "Explored pages :{}, Registered pages :{}, Last : {}".format(
                    self.explored_pages, self.registered_pages, page_name
                )
            )

    def add_page(self, page):
        res = self.graph.add_vertex(page.link, page=page, visited=False)
        self.registered_pages += 1
        self.lookup_table[page.link] = page
        return res

    def add_link(self, source_page, target_page):
        self.created_links += 1
        return self.graph.add_edge(source_page, target_page)

    @PerformanceCounter.timed('get_node')
    def get_node(self, name):
        try:
            page = self.lookup_table[name]
        except KeyError:
            page = None
        return page

    @PerformanceCounter.timed('get_neighbors')
    def get_neighbors(self, page, visited=False):
        neighbors = page.vertex.neighbors(mode=OUT)
        neighbors = [n for n in neighbors if n["visited"] is visited]
        return neighbors

    def __str__(self):
        return str(self.graph)
