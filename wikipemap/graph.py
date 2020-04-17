from igraph import Graph, OUT
from IPython.display import display, clear_output
from wikipemap.perf_counter import PerformanceCounter


class WikipediaMap:
    def __init__(self, name, verbose=True, use_lookup=True):
        self.graph = Graph(directed=True)
        self.name = name
        self.graph["name"] = name
        self.explored_pages = 0
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
                    self.explored_pages, len(self.graph.vs), page_name
                )
            )

    def add_page(self, page):
        PerformanceCounter.start_metric("add_page")
        res = self.graph.add_vertex(page, visited=False)
        if self.use_lookup is True:
            self.lookup_table[page] = res
        PerformanceCounter.end_metric("add_page")
        return res

    def add_link(self, source_vertex, target_vertex):
        self.created_links += 1
        return self.graph.add_edge(source_vertex, target_vertex)

    def get_node(self, name):
        PerformanceCounter.start_metric("get_node")
        if self.use_lookup is True:
            if name in self.lookup_table:
                vertex = self.lookup_table[name]
            else:
                vertex = None
        else:
            try:
                vertex = self.graph.vs.find(name=name)
            except ValueError:
                vertex = None
        PerformanceCounter.end_metric("get_node")
        return vertex

    def get_neighbors(self, vertex, visited=False):
        PerformanceCounter.start_metric("get_neighbors")
        neighbors = vertex.neighbors(mode=OUT)
        neighbors = [n for n in neighbors if n["visited"] is visited]
        PerformanceCounter.end_metric("get_neighbors")
        return neighbors

    def set_visited(self, vertex):
        vertex["visited"] = True

    def __str__(self):
        return str(self.graph)
