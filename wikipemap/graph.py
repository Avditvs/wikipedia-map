from IPython.display import display, clear_output
from wikipemap.perf_counter import PerformanceCounter
import graph_tool as gt


class WikipediaMap:
    def __init__(self, name, verbose=True, use_lookup=True):
        self.graph = gt.Graph(directed=True)
        self.page_prop = self.graph.new_vertex_property("object")
        self.name = name
        self.explored_pages = 0
        self.verbose = verbose
        self.use_lookup = use_lookup
        self.lookup_table = {}

    @property
    def created_links(self):
        return self.graph.num_edges()

    @property
    def registered_pages(self):
        return self.graph.num_vertices()

    def page_explored(self, page_name):
        self.explored_pages += 1
        if self.explored_pages % 100 == 0 and self.verbose is True:
            clear_output()
            display(
                "Explored pages :{}, Registered pages :{}, Last : {}".format(
                    self.explored_pages, self.registered_pages, page_name
                )
            )

    def add_page(self, page):
        res = self.graph.add_vertex()
        self.page_prop[res] = page
        self.lookup_table[page.link] = page
        return res

    def add_link(self, source_page, target_page):
        return self.graph.add_edge(source_page, target_page)

    @PerformanceCounter.timed("add_links")
    def add_links(self, es):
        return self.graph.add_edge_list(es)

    @PerformanceCounter.timed("get_node")
    def get_node(self, name):
        try:
            page = self.lookup_table[name]
        except KeyError:
            page = None
        return page

    def __str__(self):
        return str(self.graph)
