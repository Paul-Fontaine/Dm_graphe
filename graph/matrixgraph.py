import queue
from typing import List
from graph.abstractgraph import AbstractGraph
from graph.edge import Edge


class MatrixGraph(AbstractGraph):
    def __init__(self, name: str, vertices_names: List[str], directed: bool = False):
        AbstractGraph.__init__(self, name, vertices_names, directed)
        self.matrix = [[0 for _ in range(self.order)] for _ in range(self.order)]

    def succ(self, vertex: int | str, return_str: bool = False) -> List[str] | List[int]:
        i = self.vertex_index(vertex) if type(vertex) == str else vertex
        indexes_succ = [i for i, element in enumerate(self.matrix[i]) if element > 0]
        if return_str:
            return [name for i, name in enumerate(self.vertices_names) if i in indexes_succ]
        return indexes_succ

    def pred(self, vertex: int | str, return_str: bool = False) -> List[str] | List[int]:
        i = self.vertex_index(vertex) if type(vertex) == str else vertex
        col = [row[i] for row in self.matrix]
        indexes_pred = [i for i, element in enumerate(col) if element > 0]
        if return_str:
            return [name for i, name in enumerate(self.vertices_names) if i in indexes_pred]
        return indexes_pred

    def adja(self, vertex: int | str, return_str: bool = False) -> List[str] | List[int]:
        i = self.vertex_index(vertex) if type(vertex) == str else vertex
        if self.directed:
            result = self.pred(i) + self.succ(i)
        else:
            result = self.succ(i)
        if return_str:
            return [name for i, name in enumerate(self.vertices_names) if i in result]
        return result

    def degree(self, vertex: int | str, mode: int = 0) -> int:
        """ :param vertex: the name of a vertex
            :type vertex: str
            :param mode: 0 : in-degree, 1 : out-degree, 2 : both. by default, it's the in-degree that works as the basic degree for non-directed graphs
            :type mode: int
            :return: the chosen degree of the vertex
            :rtype: int
        """

        i = self.vertex_index(vertex) if type(vertex) == str else vertex
        col = [row[i] for row in self.matrix]
        in_degree = sum(col)
        out_degree = sum(self.matrix[i])

        if mode == 0:
            return in_degree
        if mode == 1:
            return out_degree
        if mode == 2:
            return in_degree + out_degree

    def add_vertex(self, name: str) -> None:
        self.vertices_names.append(name)
        self.order += 1
        # update the size of the matrix. create a new one and copy the older one in it
        new_matrix = [[0 for _ in range(self.order)] for _ in range(self.order)]
        for i in range(self.order - 1):
            for j in range(self.order - 1):
                new_matrix[i][j] = self.matrix[i][j]
        self.matrix = new_matrix

    def add_edge(self, vertex1: int | str, vertex2: int | str, weight: int | float = 1) -> None:
        vertex1 = self.vertex_index(vertex1) if type(vertex1) == str else vertex1
        vertex2 = self.vertex_index(vertex2) if type(vertex2) == str else vertex2
        self.matrix[vertex1][vertex2] += weight
        if not self.directed:
            self.matrix[vertex2][vertex1] += weight

    def add_Edge(self, edge: Edge) -> None:
        self.add_edge(edge.u, edge.v, edge.weight)

    def remove_vertex(self, vertex: int | str) -> None:
        index2remove = self.vertex_index(vertex) if type(vertex) == str else vertex
        # remove the line of the vertex
        self.matrix.pop(index2remove)
        # remove the column of the vertex
        new_matrix = []
        for row in self.matrix:
            new_row = [element for index, element in enumerate(row) if index != index2remove]
            new_matrix.append(new_row)
        self.matrix = new_matrix
        # remove the name of the vertex
        self.vertices_names.remove(vertex)

    def remove_edge(self, vertex1: int | str, vertex2: int | str, all_edges: bool = False) -> None:
        # get indexes from name of vertices
        vertex1 = self.vertex_index(vertex1) if type(vertex1) == str else vertex1
        vertex2 = self.vertex_index(vertex2) if type(vertex2) == str else vertex2

        if all_edges:
            self.matrix[vertex1][vertex2] = 0
            self.matrix[vertex2][vertex1] = 0
            return

        if self.matrix[vertex1][vertex2] > 0:  # check if there is an edge to remove
            self.matrix[vertex1][vertex2] -= 1
        if not self.directed:  # do the same operation on the symetric if the graph is not directed
            if self.matrix[vertex2][vertex1] > 0:
                self.matrix[vertex2][vertex1] -= 1

    def has_edge(self, vertex1: int | str, vertex2: int | str) -> bool:
        vertex1 = self.vertex_index(vertex1) if type(vertex1) == str else vertex1
        vertex2 = self.vertex_index(vertex2) if type(vertex2) == str else vertex2
        if self.matrix[vertex1][vertex2] != 0:
            return True
        return False

    def DFS_rec(self, src: int | str = 0) -> List[int]:
        """
        utilise des tableaux accessibles depuis la fonction inner
        :param src: le sommet de départ
        :return: la liste PRED
        """
        src = self.vertex_index(src) if type(src) == str else src  # convertit le nom d'un sommet en son indice
        pred = [None] * self.order
        marquage = [0] * self.order  # 0 : blanc ; 1 : gris ; 2 : noir

        def DFS_inner(v: int):
            marquage[v] = 1
            for s in self.succ(v):
                if marquage[s] == 0:
                    pred[s] = v
                    DFS_inner(s)
            marquage[v] = 2

        DFS_inner(src)  # premier passage
        for i, color in enumerate(marquage):  # repars des sommets des autres composantes connexes
            if color == 0:
                DFS_inner(i)

        return pred

    def topological_sort(self, src: int | str = 0, return_str: bool = False) -> List[int] | List[str]:
        src = self.vertex_index(src) if type(src) == str else src
        deb = [None] * self.order
        fin = [None] * self.order
        t = 0
        marquage = [0] * self.order  # 0 : blanc ; 1 : gris ; 2 : noir

        def t_s_inner(v: int):
            nonlocal t
            marquage[v] = 1
            t += 1
            deb[v] = t
            for s in self.succ(v):
                if marquage[s] == 0:
                    t_s_inner(s)
            marquage[v] = 2
            t += 1
            fin[v] = t

        t_s_inner(src)
        for i, color in enumerate(marquage):
            if color == 0:
                t_s_inner(i)

        indexed_list = list(enumerate(fin))
        indexed_list.sort(key=lambda tuple_: tuple_[1],
                          reverse=True)  # renvoie la liste des indices triés en fonction de leur valeur de fin
        indexes_sorted = [tuple_[0] for tuple_ in indexed_list]

        if return_str:
            return [self.vertices_names[i] for i in indexes_sorted]
        return indexes_sorted

    def BFS_ite(self, src: int | str = 0) -> List[int]:
        src = self.vertex_index(src) if type(src) == str else src
        file = queue.Queue()
        marquage = [0] * self.order
        pred = [None] * self.order

        def BFS_inner(s: int) -> None:
            marquage[s] = 1
            file.put(s)
            while not file.empty():
                u = file.get()
                for v in self.succ(u):
                    if marquage[v] == 0:
                        file.put(v)
                        pred[v] = u
                        marquage[v] = 1
                marquage[u] = 2

        BFS_inner(src)
        for i, color in enumerate(marquage):
            if color == 0:
                BFS_inner(i)

        return pred

    def pcc(self, start: int | str, end: int | str, return_str: bool = False) -> list[int] | list[str]:
        start = self.vertex_index(start) if type(start) == str else start
        end = self.vertex_index(end) if type(end) == str else end
        pred = self.BFS_ite(start)
        chemin = [end]
        while end != start:
            chemin.insert(0, pred[end])
            end = pred[end]

        if return_str:
            return [self.vertices_names[i] for i in chemin]
        return chemin

    def is_connex(self):
        return self.BFS_ite().count(None) <= 1

    @staticmethod
    def sort_edges_list(edges_list: List[Edge]) -> List[Edge]:
        return sorted(edges_list, key=lambda e: e.weight)

    def edges(self, sort: bool = False) -> List[Edge]:
        edges_list = []
        for i in range(self.order):
            for j in range(self.order):
                w = self.matrix[i][j]
                if not w == 0:
                    edge = Edge(i, j, w, self.vertices_names[i], self.vertices_names[j])
                    if edge not in edges_list:
                        edges_list.append(edge)

        if sort:
            return self.sort_edges_list(edges_list)
        return edges_list

    def has_cycle(self) -> bool:
        visited = [False] * self.order

        def dfs_find_cycle(vertice: int, parent: int):
            visited[vertice] = True

            for s in self.succ(vertice):
                if not visited[s]:
                    dfs_find_cycle(s, vertice)
                elif not s == parent:
                    return True

            return False

        return dfs_find_cycle(0, -1)  # -1 : first vertice has no parent

    @classmethod
    def kruskal_naif(cls, graph):
        kraph = cls("kruskal naif", graph.vertices_names)

        for edge in graph.edges(True):
            kraph.add_Edge(edge)
            if kraph.has_cycle():
                kraph.remove_edge(edge.u, edge.v, True)

        return kraph

    @classmethod
    def prim(cls, graph):
        prim = cls("prim", [graph.vertices_names[0]])
        edges = graph.edges(sort=True)
        available_edges = [edge for edge in edges if edge.is_connected_to(0)]
        previous_vertex = 0

        while prim.order != graph.order:
            add_edge: Edge = available_edges.pop(0)
            if not add_edge.new_vertex(prim):
                continue
            new_vertex = add_edge.new_vertex(prim)
            prim.add_vertex(graph.vertices_names[new_vertex])
            prim.add_edge(add_edge.u_name, add_edge.v_name, add_edge.weight)
            available_edges += [edge for edge in edges if edge.is_connected_to(new_vertex) and edge not in available_edges and edge != add_edge]
            available_edges = MatrixGraph.sort_edges_list(available_edges)
            previous_vertex = new_vertex

        return prim

    def weight(self) -> int | float:
        sum = 0
        for i in range(self.order):
            for j in range(self.order):
                sum += self.matrix[i][j]
        return sum/2

    def print(self):
        print(self.name)
        # print the name of vertices on the first row
        print(" ", end="\t")
        for name in self.vertices_names:
            print(name, end="\t")
        print()
        i = 0
        for row in self.matrix:
            # print the name of vertices on the first column
            print(self.vertices_names[i], end="\t")
            for element in row:
                print(element, end="\t")  # Use '\t' for tab-separated columns
            print()  # Move to the next row
            i += 1

        print()
