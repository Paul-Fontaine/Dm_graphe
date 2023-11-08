class Edge:
    def __init__(self, u: int, v: int, weight: int | float, u_name: str = "u", v_name: str = "v"):
        if u > v:
            u, v = v, u
            u_name, v_name = v_name, u_name
        self.u = u
        self.u_name = u_name
        self.v = v
        self.v_name = v_name
        self.weight = weight

    def __eq__(self, other):
        if isinstance(other, Edge):
            if other.u != self.u:
                return False
            if other.v != self.v:
                return False
            if other.weight != self.weight:
                return False
            return True
        else:
            return False

    def is_connected_to(self, vertex: int) -> bool:
        return self.u == vertex or self.v == vertex

    def new_vertex(self, graph):
        if self.u_name not in graph.vertices_names:
            return self.u
        if self.v_name not in graph.vertices_names:
            return self.v
        return False
