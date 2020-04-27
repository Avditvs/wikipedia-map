from igraph import Graph
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
        if self.explored_pages % 100 == 0 and self.verbose is True:
            clear_output()
            display(
                "Explored pages :{}, Registered pages :{}, Last : {}".format(
                    self.explored_pages, self.registered_pages, page_name
                )
            )

    def add_page(self, page):
        res = self.graph.add_vertex(page=page)
        self.registered_pages += 1
        self.lookup_table[page.link] = page
        return res

    def add_link(self, source_page, target_page):
        self.created_links += 1
        return self.graph.add_edge(source_page, target_page)

    def add_links(self, gen_len, es):
        self.created_links += gen_len
        return self.graph.add_edges(es)

    @PerformanceCounter.timed("get_node")
    def get_node(self, name):
        try:
            page = self.lookup_table[name]
        except KeyError:
            page = None
        return page

    def __str__(self):
        return str(self.graph)
