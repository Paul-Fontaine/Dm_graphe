import enum
from typing import List


class Edge:
    def __init__(self, u: int, v: int, weight: float = 1):
        self.u = u
        self.v = v
        self.weight = weight

    def __str__(self):
        return f"{self.u} - {self.v} : {self.weight}"

    def __hash__(self):
        return hash((self.u, self.v))

    def __eq__(self, other):
        if isinstance(other, Edge):
            if (self.u, self.v) == (other.u, other.v) and self.weight == other.weight:
                return True
            return False

    def is_connected_to(self, v: int) -> bool:
        if v in {self.u, self.v}:
            return True
        return False

    def other(self, s: int) -> int:
        if s == self.u:
            return self.v
        return self.u
