from typing import List, Tuple

from model.lib_graph.abstractgraph import AbstractGraph, Vertex, Edge


class GraphList(AbstractGraph):
    def __init__(self, name: str, vertices: List[Vertex], directed: bool = False):
        AbstractGraph.__init__(self, name, vertices, directed)
        self.successors_list = [[] for i in range(self.order)]

    def predecessors(self, v: int) -> List[int]:
        if not self.directed:
            print("Don't use predecessors() in a non directed graph")
            return
        return [u for u, successors in enumerate(self.successors_list) if v in successors]

    def successors(self, v: int) -> List[int]:
        return self.successors_list[v]

    def degree(self, v: int, _in: bool = False, out: bool = False) -> int:
        if self.directed:
            if _in:
                return len(self.predecessors(v))
            if out:
                return len(self.successors(v))
            return len(self.successors(v)) + len(self.predecessors(v))
        else:
            return len(self.successors(v))

    def add_vertex(self, v: Vertex) -> None:
        self.order += 1
        self.vertices.append(v)
        self.successors_list.append([])

    def remove_vertex(self, v: int) -> None:
        self.vertices.pop(v)
        self.order -= 1
        del self.successors_list[v]
        for u, successors in enumerate(self.successors_list):
            if v in successors:
                successors.remove(v)
            self.successors_list[u] = [s if s < v else s-1 for s in successors]

    def v_index(self, name: str) -> int:
        for i, v in enumerate(self.vertices):
            if v.name == name:
                return i

    def add_edge(self, e: Edge) -> None:
        if e in self.edges:
            return
        self.edges_index[(e.u, e.v)] = len(self.edges)
        self.edges.append(e)
        if self.directed:
            self.successors_list[e.u].append(e.v)
        else:
            self.successors_list[e.u].append(e.v)
            self.successors_list[e.v].append(e.u)

    def add_edges(self, edges: List[Tuple[str, str]]) -> None:
        for e in edges:
            u, v = e
            self.add_edge(Edge(self.v_index(u), self.v_index(v)))

    def remove_edge(self, e: Edge) -> None:
        self.edges.remove(e)
        self.successors_list[e.u].remove(e.v)
        if not self.directed:
            self.successors_list[e.v].remove(e.u)

    def has_edge(self, v1: int, v2: int) -> bool:
        if v2 in self.successors(v1):
            return True
        if not self.directed:
            if v1 in self.successors(v2):
                return True
        return False

    def print(self) -> None:
        print(self.name)
        for v, successors in enumerate(self.successors_list):
            v_name = self.vertices[v].name
            successors_name = [self.vertices[i].name for i in successors]
            print(v_name, " : ", successors_name)
        print()
