from typing import List
from abc import ABC, abstractmethod
import queue


class AbstractGraph(ABC):
    def __init__(self, name: str, vertices_names: List[str], directed: bool = False):
        self.name = name
        self.directed = directed
        self.order = len(vertices_names)
        self.vertices_names = vertices_names

    def vertex_index(self, vertex_name: str) -> int:
        return self.vertices_names.index(vertex_name)

    @abstractmethod
    def adja(self, vertex: str, return_str: bool = False) -> List[str] | List[int]:
        pass

    @abstractmethod
    def pred(self, vertex: str, return_str: bool = False) -> List[str] | List[int]:
        pass

    @abstractmethod
    def succ(self, vertex: str, return_str: bool = False) -> List[str] | List[int]:
        pass

    @abstractmethod
    def degree(self, vertex: int) -> int:
        pass

    @abstractmethod
    def add_vertex(self, name: str) -> None:
        pass

    @abstractmethod
    def add_edge(self, vertex1: int, vertex2: int) -> None:
        pass

    @abstractmethod
    def remove_vertex(self, vertex: int) -> None:
        pass

    @abstractmethod
    def remove_edge(self, vertex1: int, vertex2: int) -> None:
        pass

    @abstractmethod
    def has_edge(self, vertex1: int, vertex2: int) -> bool:
        pass

    @abstractmethod
    def DFS_rec(self, src: int | str = 0) -> List[int]:
        pass

    @abstractmethod
    def BFS_ite(self, src : int | str = 0) -> List[int]:
        pass

    @abstractmethod
    def print(self) -> int:
        pass
