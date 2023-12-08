import queue
from typing import List, Tuple
from abc import ABC, abstractmethod

from lib_graph.edge import Edge
from lib_graph.vertex import Vertex

number = int | float


class AbstractGraph(ABC):
    def __init__(self, name: str, vertices: List[Vertex], directed: bool):
        ABC.__init__(self)
        self.name = name
        self.directed = directed
        self.order = len(vertices)
        self.vertices = vertices
        self.edges = []

    # methods for vertices

    @abstractmethod
    def predecessors(self, v: int) -> List[int]:
        pass

    @abstractmethod
    def successors(self, v: int) -> List[int]:
        pass

    @abstractmethod
    def degree(self, v: int) -> int:
        pass

    @abstractmethod
    def add_vertex(self, v: Vertex) -> None:
        pass

    @abstractmethod
    def remove_vertex(self, v: int) -> None:
        pass

    @abstractmethod
    def v_index(self, name: str) -> int:
        pass

    # methods for edges

    @abstractmethod
    def add_edge(self, e: Edge) -> None:
        pass

    @abstractmethod
    def remove_edge(self, e: Edge) -> None:
        pass

    @abstractmethod
    def has_edge(self, v1: int, v2: int) -> bool:
        pass

    @abstractmethod
    def print(self) -> int:
        pass

    def weight(self):
        return sum([e.weight for e in self.edges])

    def DFS(self, s0: int = 0) -> List[int]:
        pile = queue.LifoQueue()
        marquage = [0] * self.order  # 0: white, 1: grey, 2: black
        pred = [None] * self.order

        def DFS_inner(s: int) -> None:
            marquage[s] = 1
            pile.put(s)
            while not pile.empty():
                u = pile.get()
                for v in self.successors(u):
                    if marquage[v] == 0:
                        pile.put(v)
                        pred[v] = u
                        marquage[v] = 1
                marquage[u] = 2

        DFS_inner(s0)
        for i, color in enumerate(marquage):
            if color == 0:
                DFS_inner(i)

        return pred

    def BFS(self, s0: int = 0) -> List[int]:
        file = queue.Queue()
        marquage = [0] * self.order  # 0: white, 1: grey, 2: noir
        pred = [None] * self.order

        def BFS_inner(s: int) -> None:
            marquage[s] = 1
            file.put(s)
            while not file.empty():
                u = file.get()
                for v in self.successors(u):
                    if marquage[v] == 0:
                        file.put(v)
                        pred[v] = u
                        marquage[v] = 1
                marquage[u] = 2

        BFS_inner(s0)
        for i, color in enumerate(marquage):
            if color == 0:
                BFS_inner(i)

        return pred

    def BFS_truncate(self, s0: int = 0, max_layer: int = 2) -> List[int]:
        file = queue.Queue()
        marquage = [0] * self.order  # 0: white, 1: grey, 2: black
        pred = [None] * self.order

    def topological_sort(self, s0: int = 0) -> List[int]:
        start = [None] * self.order
        end = [None] * self.order
        t = 0
        marquage = [0] * self.order  # 0: white ; 1: grey ; 2: black

        def t_s_inner(u: int):
            nonlocal t
            marquage[u] = 1
            t += 1
            start[u] = t
            for v in self.successors(u):
                if marquage[v] == 0:
                    t_s_inner(v)
            marquage[u] = 2
            t += 1
            end[u] = t

        t_s_inner(s0)
        for i, color in enumerate(marquage):
            if color == 0:
                t_s_inner(i)

        indexed_list = list(enumerate(end))  # List[s, fin(s)] with s a vertex
        indexed_list.sort(key=lambda tuple_: tuple_[1], reverse=True)  # sort the vertices by their end time
        indexes_sorted = [tuple_[0] for tuple_ in indexed_list]  # keep only the vertices

        return indexes_sorted

    def shortest_path(self, start: int, end: int) -> list[int]:
        pred = self.BFS(start)
        path = [end]
        current_vertex = end
        while current_vertex != start:
            path.insert(0, pred[current_vertex])
            current_vertex = pred[current_vertex]

        return path

    def is_connex(self):
        return self.BFS().count(None) <= 1

    def has_cycle(self) -> bool:
        pile = queue.LifoQueue()
        marquage = [0] * self.order  # 0: white, 1: grey, 2: black

        def DFS_find_cycle(s: int) -> bool:
            marquage[s] = 1
            pile.put(s)
            while not pile.empty():
                u = pile.get()
                for v in self.successors(u):
                    if marquage[v] == 0:
                        pile.put(v)
                        marquage[v] = 1
                    elif marquage[v] == 1:
                        # Cycle detected, we have already visited this vertex that is in the successors of u
                        return True
                marquage[u] = 2
            # no cycle has been detected
            return False

        # for each connex component : check if there is a cycle
        for i, color in enumerate(marquage):
            if color == 0:
                if DFS_find_cycle(i):
                    return True  # Graph has a cycle

        return False  # No cycle found

    @classmethod
    def kruskal_naif(cls, g: '"AbstractGraph"') -> '"AbstractGraph"':
        kraph = cls("kruskal naif", g.vertices)
        edges = sorted(g.edges, key=lambda e: e.weight)
        for e in edges:
            kraph.add_edge(e)
            if kraph.has_cycle():
                kraph.remove_edge(e)
        return kraph

    @classmethod
    def kruskal_Union_Find(cls, g: '"AbstractGraph"') -> '"AbstractGraph"':
        def Find(v: int) -> int:
            if parent[v] is None:
                return v
            return Find(parent[v])

        def Union(u: int, v: int) -> None:
            u_root = Find(u)
            v_root = Find(v)
            if u_root != v_root:
                parent[u_root] = v_root

        parent = [None] * g.order
        kraph = cls("kruskal Union Find", g.vertices)
        edges = sorted(g.edges, key=lambda e: e.weight)
        for e in edges:
            if Find(e.u) != Find(e.v):
                kraph.add_edge(e)
                Union(e.u, e.v)

        return kraph

    @classmethod
    def arpm(cls, g: '"AbstractGraph"') -> '"AbstractGraph"':
        return cls.kruskal_Union_Find(g)

    # @classmethod
    # def prim(cls, g: '"AbstractGraph"', s0: int = 0) -> '"AbstractGraph"':
    #     prim = cls("prim", [g.vertices[s0]], g.directed)
    #     edges = sorted(g.edges, key=lambda e: e.weight)
    #     available_edges = {e for e in edges if e.is_connected_to(s0)}
    #     already_used_edges = set()
    #
    #     def new_vertex(e: Edge) -> Tuple[Vertex, Vertex]:
    #         if g.vertices[e.u] in prim.vertices:
    #             return g.vertices[e.u], g.vertices[e.v]
    #         return g.vertices[e.v], g.vertices[e.u]
    #
    #     while prim.order != g.order:
    #         # edge with the minimal weight with u in prim.vertices and edge in g.edges
    #         min_e = min(available_edges, key=lambda e: e.weight)
    #         print(min_e)
    #         # find the new vertex (v)
    #         u, v = new_vertex(min_e)
    #         # add v to prim
    #         prim.add_vertex(v)
    #         u_i, v_i = prim.vertices.index(u), prim.vertices.index(v)
    #         prim.add_edge(Edge(u_i, v_i, min_e.weight))
    #
    #         already_used_edges.add(min_e)
    #         # update the availables edges
    #         for e in edges:
    #             for v in prim.vertices:
    #                 v_i = g.vertices.index(v)
    #                 u_i = e.other(v_i)
    #                 if e.is_connected_to(v_i) and g.vertices[u_i] not in prim.vertices:
    #                     available_edges.add(e)
    #         available_edges -= already_used_edges
    #
    #     return prim

    @staticmethod
    def path(pred: List[int], s0: int, s1: int) -> List[int]:
        path = []
        pred_ = s1
        while pred_ != s0:
            path.append(pred_)
            pred_ = pred[pred_]
            if pred_ is None:
                print('no path found')
                return False
        path.append(s0)
        path.reverse()
        return path

    def getEdge(self, u: int, v: int):
        for e in self.edges:
            if {u, v} == {e.u, e.v}:
                return e

    def relacher(self, si: int, sj: int, dist: List[number], pred: List[int]) -> None:
        e = self.getEdge(si, sj)
        if dist[sj] > dist[si] + e.weight:
            dist[sj] = dist[si] + e.weight
            pred[sj] = si

    def dijkstra(self, s0: int = 0, s1: int = None) -> (List[int], List[number]):
        dist = [float('inf')] * self.order
        dist[s0] = 0
        pred = [None] * self.order
        F = list(range(self.order))

        while F:
            si = min(F, key=lambda elt: dist[elt])
            F.remove(si)
            for sj in self.successors(si):
                self.relacher(si, sj, dist, pred)
            if s1 is not None and si == s1:
                return AbstractGraph.path(pred, s0, s1), dist[s1]

        return pred, dist

    def BellmanFord(self, s0: int | str = 0):
        dist = [float('inf')] * self.order
        dist[s0] = 0
        pred = [None] * self.order
        F = list(range(self.order))

        for i in range(1, self.order-1):
            for e in self.edges:
                self.relacher(e.u, e.v, dist, pred)

        for e in self.edges:
            if dist[e.v] > dist[e.u] + self.getEdge(e.u, e.v).weight:
                print("circuit absorbant")
                break

        return pred, dist

    def FloydWarshall(self):
        dist = [[float('inf')] * self.order] * self.order
        pred = [[None] * self.order] * self.order

        for k in range(self.order):
            for i in range(self.order):
                for j in range(self.order):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]

        return dist, pred
