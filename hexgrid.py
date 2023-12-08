import math
import queue
import random
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
    if result <= A[0]:
        result = A[0]
    if result >= A[1]:
        result = A[1]
    return result


ground_types = ["plain", "water", "mountain", "snow", "field"]
ground_probas = [0.4, 0.1, 0.2, 0.1, 0.2]


class HexGrid(GraphList):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # init tiles with only plains
        tiles = []
        for i in range(height):
            for j in range(width):
                # ground = random.choices(ground_types, ground_probas)[0]
                tile = Tile(coord=(i, j),
                            ground="plain",
                            altitude=self.pseudo_random_altitude(i)
                            )
                tiles.append(tile)
        GraphList.__init__(self, "hex graph", tiles)

        # init edges with a default weight = 1
        for i in range(height):
            for j in range(width):
                for neighbor in self.get_neighbours(i, j):
                    index_i_j = self.coord_2_i((i, j))
                    index_neighbor = self.coord_2_i(neighbor)
                    self.add_edge(Edge(index_i_j, index_neighbor))

        # add some fields
        nb_fields = random.randint(0, math.floor((height*width)**(1/3)))  # cubic root of the nb of tiles
        for i in range(nb_fields):
            field_coord = (random.randint(0, height//2), random.randint(0, width))
            field_size = random.randint(2, 4)
            self.make_field(field_coord, field_size)

    def i_2_coord(self, i: int) -> Coords:
        row = i // self.width
        col = i % self.width
        return row, col

    def coord_2_i(self, coord: Coords) -> int:
        row, col = coord
        return row * self.width + col

    def get_Tile(self, coord: Coords) -> Tile:
        for tile in self.vertices:
            if tile.coord == coord:
                return tile
        return False

    def set_ground(self, coord: Coords, ground: str):
        tile = self.get_Tile(coord)
        tile.ground = ground

    def get_neighbours(self, x: int, y: int) -> List[Coords]:
        """
        Retourne la liste des coordonnées des hexagones voisins de l'hexagone en coordonnées (x,y).
        """
        if y % 2 == 0:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1))]
        else:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (1, 1), (0, 1), (-1, 0), (0, -1), (1, -1))]
        return [(dx, dy) for dx, dy in res if 0 <= dx < self.height and 0 <= dy < self.width]

    def pseudo_random_altitude(self, row: int, random_: int = 10, bonus: int = 40) -> int:
        """
        Generate a pseudo random altitude for __init__(). It creates a gradient from top to bottom
        @param row:
        @param random_: control the variation on each row
        @param bonus: altitude max added
        """
        altitude_bonus = math.floor(transfert_ensemble_proportionnel((0, self.height), (0, bonus), row))
        altitude = random.randint(0, random_) + altitude_bonus
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

    def make_field(self, center: Coords, size: int = 3):
        field_coords = self.area(center, size)
        for coord in field_coords:
            self.set_ground(coord, "field")
