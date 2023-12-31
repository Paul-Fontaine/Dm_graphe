from typing import Tuple

from model.lib_graph.vertex import Vertex


class Tile(Vertex):
    def __init__(self, coord: Tuple[int, int], ground: str, altitude: int, town: bool = False, name: str = "not named tile"):
        Vertex.__init__(self, name)
        self.ground = ground
        self.altitude = altitude
        self.coord = coord
        self.town = town
