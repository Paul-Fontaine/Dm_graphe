from typing import Tuple

from lib_graph.vertex import Vertex


class Tile(Vertex):
    def __init__(self, coord: Tuple[int, int], ground: str, altitude: int, city: bool = False, name: str = "not named tile"):
        Vertex.__init__(self, name)
        self.ground = ground
        self.altitude = altitude
        self.coord = coord
        self.city = city
