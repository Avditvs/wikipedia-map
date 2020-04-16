from igraph import Graph, OUT
from IPython.display import display, clear_output


class WikipediaMap:
    def __init__(self, name, verbose=True):
        self.graph = Graph(directed=True)
        self.name = name
        self.graph["name"] = name
        self.explored_pages = 0
        self.verbose = verbose
        self.created_links = 0

    def page_explored(self):
        self.explored_pages += 1

    def add_page(self, page):
        if self.verbose is True:
            clear_output()
            display(
                "Explored pages : "
                + str(self.explored_pages)
                + " ; "
                + str(len(self.graph.vs))
                + " : "
                + page,
            )
        return self.graph.add_vertex(page, visited=False)

    def add_link(self, source_vertex, target_vertex):
        self.created_links += 1
        return self.graph.add_edge(source_vertex, target_vertex)

    def get_node(self, name):
        try:
            vertex = self.graph.vs.find(name=name)
            return vertex
        except ValueError:
            return None

    def get_neighbors(self, vertex, visited=False):
        neighbors = vertex.neighbors(mode=OUT)
        return [n for n in neighbors if n["visited"] is visited]

    def set_visited(self, vertex):
        vertex["visited"] = True

    def __str__(self):
        return str(self.graph)
