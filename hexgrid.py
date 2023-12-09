import math
import queue
import random
import time
from typing import Tuple, List

from lib_graph.edge import Edge
from lib_graph.graphlist import GraphList
from tile import Tile

Coords = Tuple[int, int]
Interval = Tuple[float, float]


def transfert_ensemble_proportionnel(D: Interval, A: Interval, x: float) -> float:
    """
    @param D: ensemble de départ
    @param A: ensemble d'arrivée
    @param x: valeur à transférer
    @return:
    """
    size_D = D[1] - D[0]
    size_A = A[1] - A[0]
    result = size_A / size_D * x + A[0]

    # clamp
    if result <= A[0]:
        result = A[0]
    if result >= A[1]:
        result = A[1]

    return result


MOVING_COST = {
    "plain": 2,
    "water": 10,
    "mountain": 5,
    "snow": 8,
    "field": 3
}


class HexGrid(GraphList):
    def __init__(self, width, height):
        random.seed(time.time())
        self.width = width
        self.height = height

        # init tiles with only plains
        tiles = [Tile(coord=(i, j),
                      ground="plain",
                      altitude=self.pseudo_random_altitude(i)
                      )
                 for i in range(height)
                 for j in range(width)
                 ]

        GraphList.__init__(self, "hex graph", tiles, directed=False)

        # init edges with a default weight = 1
        # mandatory to then make a BFS for the self.area() function
        for i in range(height):
            for j in range(width):
                for neighbor in self.get_neighbours_special_edges_(i, j):
                    index_i_j = self.coord_2_i((i, j))
                    index_neighbor = self.coord_2_i(neighbor)
                    self.add_edge(Edge(index_i_j, index_neighbor))

        # add some fields. random number, random coords, random size
        nb_fields = random.randint(1, math.floor((height*width)**(1/3))-1)  # cubic root of the nb of tiles
        for i in range(nb_fields):
            # fields are only in the lower part of the map
            field_coord = (
                random.randint(  # x
                    0,
                    max(height//2 - 3, 0)
                ),
                random.randint(  # y
                    0,
                    width-1
                )
            )
            field_size = random.randint(2, 3)
            self.make_field(field_coord, field_size)

        # add some mountains. random number, random coords, random size
        nb_mountains = random.randint(1, math.floor((height * width) ** (1 / 3)))
        for i in range(nb_mountains):
            # mountains are only in the upper part of the map
            mountain_coord = (
                random.randint(  # x
                    min(max(height//2 + 3, 0), height-1),  # clamp to avoid errors with low dimensions
                    height-1
                ),
                random.randint(  # y
                    0,
                    width-1
                )
            )
            mountain_size = random.randint(2, 4)
            self.make_mountains(mountain_coord, mountain_size)

        # todo add rivers

        # update edges wheights depending on the type of ground and the altitude difference
        for edge in self.edges:
            tile1: Tile = self.vertices[edge.u]
            tile2: Tile = self.vertices[edge.v]
            edge.weight = MOVING_COST[tile1.ground] + MOVING_COST[tile2.ground]
            alt_diff = abs(tile1.altitude - tile2.altitude)
            if alt_diff > 10:
                edge.weight += alt_diff // 2

    def i_2_coord(self, i: int) -> Coords:
        row = i // self.width
        col = i % self.width
        return row, col

    def coord_2_i(self, coord: Coords) -> int:
        row, col = coord
        return row * self.width + col

    def get_neighbours(self, x: int, y: int) -> List[Coords]:
        """
        Retourne la liste des coordonnées des hexagones voisins de l'hexagone en coordonnées (x,y).
        """
        if y % 2 == 0:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1))]
        else:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (1, 1), (0, 1), (-1, 0), (0, -1), (1, -1))]
        return [(dx, dy) for dx, dy in res if 0 <= dx < self.height and 0 <= dy < self.width]

    def get_neighbours_special_edges_(self, x: int, y: int) -> List[Coords]:
        """
        Return the list of neighbors coords but only the 3 on top, top right and top
        It divides by 2 the time needed to create edges
        """
        if y % 2 == 0:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1), (-1, 1))]
        else:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (1, 1), (0, 1))]
        return [(dx, dy) for dx, dy in res if 0 <= dx < self.height and 0 <= dy < self.width]

    def pseudo_random_altitude(self, row: int, random_: int = 10, bonus: int = 40) -> int:
        """
        Generate a pseudo random altitude for __init__(). It creates a gradient from top to bottom
        @param row:
        @param random_: control the variation on each row
        @param bonus: altitude max added
        """
        altitude_bonus = math.floor(transfert_ensemble_proportionnel((0, self.height), (0, bonus), row))
        altitude = random.randint(0, math.ceil(100/self.height)) + altitude_bonus
        return altitude

    def area(self, center: Coords, radius: int = 3):
        marquage = [0] * self.order
        file = queue.Queue()
        file.put((self.coord_2_i(center), 1))
        area = []

        while not file.empty():
            u, layer = file.get()
            if layer > radius:
                break
            area.append(self.i_2_coord(u))
            for v in self.successors(u):
                if marquage[v] == 0:
                    file.put((v, layer+1))
                    marquage[v] = 1
            marquage[u] = 2

        return area

    def make_field(self, center: Coords, size: int):
        field_coords = self.area(center, size)
        for coord in field_coords:
            tile = self.vertices[self.coord_2_i(coord)]
            tile.ground = "field"

    def make_mountains(self, center: Coords, size: int):
        for i in range(size):
            ring = {"coords": list(set(self.area(center, i+1)) - set(self.area(center, i))),
                    "layer": size-i+1}
            for coord in ring["coords"]:
                tile = self.vertices[self.coord_2_i(coord)]
                tile.altitude += ring["layer"]*8 + random.randint(-5, 10)
                if tile.altitude > 100:
                    tile.altitude = 100

                if tile.altitude > 75:
                    tile.ground = "snow"
                else:
                    tile.ground = "mountain"

    def get_altitude_max(self):
        return max(self.vertices, key=lambda tile: tile.altitude).altitude
