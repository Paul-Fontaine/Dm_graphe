import math
import queue
import random
import time
from typing import Tuple, List, Dict

from model.lib_graph.edge import Edge
from model.lib_graph.graphlist import GraphList
from model.lib_graph.vertex import Vertex
from model.tile import Tile

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


ground_type_color = {
    "plain": "green",
    "water": "blue",
    "mountain": "dimgray",
    "snow": "white",
    "field": "yellow",
    "volcano": "black",
    "lava": "orangered"
}
ground_color_type = {v: k for k, v in ground_type_color.items()}

MOVING_COST = {
    "plain": 2,
    "water": 20,
    "mountain": 5,
    "snow": 8,
    "field": 3,
    "volcano": 6,
    "lava": 100000
}


class HexGrid(GraphList):
    def __init__(self, width, height, nb_towns: int = -1):
        random.seed(time.time())
        self.width = width
        self.height = height
        self.towns: List[Coords] = []

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
                index_i_j = self.coord_2_i((i, j))
                for neighbor in self.get_neighbours_special_edges_(i, j):
                    index_neighbor = self.coord_2_i(neighbor)
                    self.add_edge(Edge(index_i_j, index_neighbor))

        d = math.floor((height * width) ** (1 / 3))  # cubic root of the nb of tiles

        # add some fields. random number, random coords, random size
        nb_fields = random.randint(1, d)
        for i in range(nb_fields):
            # fields are only in the lower part of the map
            field_coord = (
                random.randint(  # x
                    0,
                    max(height // 2 - 3, 0)
                ),
                random.randint(  # y
                    0,
                    width - 1
                )
            )
            field_size = random.randint(2, 3)
            self.make_field(field_coord, field_size)

        # add some mountains. random number, random coords, random size
        # nb_mountains = random.randint(1, d)
        nb_mountains = 2 * d - nb_fields
        for i in range(nb_mountains):
            # mountains are only in the upper part of the map
            mountain_coord = (
                random.randint(  # x
                    min(max(height // 2 + 3, 0), height - 1),  # clamp to avoid errors with low dimensions
                    height - 1
                ),
                random.randint(  # y
                    0,
                    width - 1
                )
            )
            mountain_size = random.randint(2, 4)
            self.make_mountain(mountain_coord, mountain_size)

        # add some volcanos. random number, random coords, random size
        nb_volcanos = random.randint(1, d // 3)
        for i in range(nb_volcanos):
            # volcanos can be everywhere on the map
            volcano_coord = (
                random.randint(  # x
                    0,
                    height - 1
                ),
                random.randint(  # y
                    0,
                    width - 1
                )
            )
            volcano_size = random.randint(2, 3)
            self.make_volcano(volcano_coord, volcano_size)

        # add some rivers
        nb_sources = random.randint(d // 3, d // 2) + 1
        candidates_sources = [
            tile.coord
            for tile in self.vertices
            if tile.altitude > 40
               and tile.ground not in ["volcano", "lava"]
        ]
        sources = random.choices(candidates_sources, k=min(nb_sources, len(candidates_sources)))
        for source in sources:
            self.make_river(source)

        # add some towns
        if nb_towns == -1:  # nb of town not specified by user : choose a random number of towns
            nb_towns = random.randint(
                (d - 1) // 2,
                (d + 2) // 2
            )
        for i in range(nb_towns):
            # choose a random place to put the town, but a town can't be in water, in a field or on a volcano
            town_coord = (
                random.randint(  # x
                    0,
                    height - 1
                ),
                random.randint(  # y
                    0,
                    width - 1
                )
            )
            while self.get_Tile(town_coord).ground in ["water", "field", "volcano", "lava"]:
                town_coord = (
                    random.randint(  # x
                        0,
                        height - 1
                    ),
                    random.randint(  # y
                        0,
                        width - 1
                    )
                )
            self.towns.append(town_coord)
            self.get_Tile(town_coord).town = True

        # update edges wheights depending on the type of ground and the altitude difference
        for edge in self.edges:
            tile1: Tile = self.vertices[edge.u]
            tile2: Tile = self.vertices[edge.v]
            edge.weight = MOVING_COST[tile1.ground] + MOVING_COST[tile2.ground]
            alt_diff = abs(tile1.altitude - tile2.altitude)
            if alt_diff > 5:
                edge.weight += alt_diff // 3
            elif alt_diff > 10:
                edge.weight += alt_diff // 2

    def i_2_coord(self, i: int) -> Coords:
        row = i // self.width
        col = i % self.width
        return row, col

    def coord_2_i(self, coord: Coords) -> int:
        row, col = coord
        return row * self.width + col

    def get_Tile(self, coord: Coords) -> Tile:
        return self.vertices[self.coord_2_i(coord)]

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
        Return the list of neighbors coords but only the 3 on top, top right and bottom right
        It divides by 2 the time needed to create edges
        """
        if y % 2 == 0:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1), (-1, 1))]
        else:
            res = [(x + dx, y + dy) for dx, dy in ((1, 0), (1, 1), (0, 1))]
        return [(dx, dy) for dx, dy in res if 0 <= dx < self.height and 0 <= dy < self.width]

    def pseudo_random_altitude(self, row: int, random_: int = 4, bonus: int = 40) -> int:
        """
        Generate a pseudo random altitude for __init__(). It creates a gradient from top to bottom
        @param row:
        @param random_: adjust the variation on each row
        @param bonus: altitude max added
        """
        altitude_init = random.randint(
            0,
            random_
        )
        # no randomness for altitude bonus it only depends on the row
        altitude_bonus = math.floor(transfert_ensemble_proportionnel((0, self.height), (0, bonus), row))
        return altitude_init + altitude_bonus

    def area(self, center: Coords, radius: int = 3, return_layer: bool = False):
        """
        return the tiles around center, it's a hexagon shape
        @param center:
        @param radius:
        @param return_layer: True -> return the distance from center
        @return:
        """
        marquage = [0] * self.order
        file = queue.Queue()
        file.put((self.coord_2_i(center), 1))
        area = []

        while not file.empty():
            u, layer = file.get()
            if layer > radius:
                break
            area.append((self.i_2_coord(u), layer) if return_layer else self.i_2_coord(u))
            for v in self.successors(u):
                if marquage[v] == 0:
                    file.put((v, layer + 1))
                    marquage[v] = 1
            marquage[u] = 2

        return area

    def make_field(self, center: Coords, size: int):
        field_coords = self.area(center, size)
        for coord in field_coords:
            tile = self.get_Tile(coord)
            tile.ground = "field"

    def make_mountain(self, center: Coords, size: int):
        mountain_coords = self.area(center, size, return_layer=True)
        for coord, layer in mountain_coords:
            tile = self.get_Tile(coord)
            tile.altitude += (size - layer + 1) * 8 + random.randint(-5, 10)
            if tile.altitude > 100:
                tile.altitude = 100

            if tile.altitude > 75:
                tile.ground = "snow"
            else:
                tile.ground = "mountain"

    def make_volcano(self, center: Coords, size: int):
        volcano_coords = self.area(center, size, return_layer=True)
        for coord, layer in volcano_coords:
            tile = self.get_Tile(coord)
            tile.ground = "volcano"
            tile.altitude += (size - layer + 1) * 8 + random.randint(-5, 10)
            if tile.altitude > 100:
                tile.altitude = 100
            if layer == 1 or random.random() < 1 / 20:
                tile.ground = "lava"

    def get_altitude_max(self):
        return max(self.vertices, key=lambda tile: tile.altitude).altitude

    def longest_river(self, src: Coords) -> List[Coords]:
        # init step
        src = self.coord_2_i(src)
        pred: List[Coords] = [None] * self.order
        visited = [False] * self.order
        pile = queue.LifoQueue()
        deepest_node = src
        max_depth = 0

        visited[src] = True
        pile.put((src, 0))

        while not pile.empty():
            u, depth = pile.get()

            if depth > max_depth:
                max_depth = depth
                deepest_node = u

            for v in self.successors(u):
                if not visited[v] \
                        and self.vertices[v].altitude <= self.vertices[u].altitude \
                        and self.vertices[v].ground not in {"volcano", "lava"}:
                    pile.put((v, depth + 1))
                    pred[v] = u
                    visited[v] = True

        path: List[int] = self.path(pred, src, deepest_node)
        path: List[Coords] = [self.i_2_coord(tile) for tile in path]
        l = len(path)

        # if the river is long enough
        if l > math.sqrt(self.order) / 2:
            # add a lake in the second half of its path
            lake_center: Coords = random.choice(path[l//2::])
            lake_radius: int = random.randint(2, 3)
            lake_coords: List[Coords] = self.area(lake_center, lake_radius)
            coord_alt_min: Coords = min(lake_coords, key=lambda c: self.get_Tile(c).altitude)
            alt_min: int = self.get_Tile(coord_alt_min).altitude
            for coord in lake_coords:
                self.get_Tile(coord).altitude = alt_min
            path += lake_coords

        return path

    def make_river(self, src: Coords):
        river_coords = self.longest_river(src)
        for coord in river_coords:
            tile: Tile = self.get_Tile(coord)
            tile.ground = "water"

    # end of methods for __init__

    # network methods

    def network(self) -> List[List[int]]:
        """
        use a BFS to get the network between all towns, but it doesn't care about terrain and altitude
        @return: List[Path]
        """
        network: List[List[int]] = []
        for i, town in enumerate(self.towns):
            pred = self.BFS(self.coord_2_i(town))
            for other_town in self.towns[i + 1::]:
                if town != other_town:
                    town_i = self.coord_2_i(town)
                    other_town_i = self.coord_2_i(other_town)
                    path = self.path(pred, town_i, other_town_i)
                    network.append(path)
        return network

    def shortest_network(self) -> List[List[int]]:
        """
        use the dijkstra algorithm to get the network between all towns and this time it cares about terrain and altitude
        NB : we calculate dijkstra for each pair of towns instead of each town,
        but as our dijkstra algorithm stop when it reaches the other town
        we still gain time because we don't have to reach all vertices
        @return: List[Path]
        """
        network: List[List[int]] = []
        for i, town in enumerate(self.towns):
            # self.dijkstra() could be here
            for other_town in self.towns[i + 1::]:
                if town != other_town:
                    path, path_cost = self.dijkstra(self.coord_2_i(town), self.coord_2_i(other_town))
                    network.append(path)
        return network

    def minimal_network(self):
        """
        use the Kruskal algorithm (with union-find) to get the costless network that connects all towns
        @return:
        """
        network: Dict[Tuple[Coords, Coords]: List[int]] = {}
        towns_graph = GraphList("towns graph", [Vertex(str(town_coord)) for town_coord in self.towns])

        def town_coord_2_index(town_coord: Coords):
            for j, vertex in enumerate(towns_graph.vertices):
                if vertex.name == str(town_coord):
                    return j

        for i, town in enumerate(self.towns):
            for other_town in self.towns[i + 1::]:
                if town != other_town:
                    path, path_cost = self.dijkstra(self.coord_2_i(town), self.coord_2_i(other_town))
                    network[(town, other_town)] = path

                    towns_graph.add_edge(Edge(
                        u=town_coord_2_index(town),
                        v=town_coord_2_index(other_town),
                        weight=path_cost))

        arpm = GraphList.arpm(towns_graph)

        minimal_network = []
        for edge in arpm.edges:
            town1_coord = eval(arpm.vertices[edge.u].name)  # "(2, 5)" -> (2, 5) string to tuple
            town2_coord = eval(arpm.vertices[edge.v].name)
            minimal_network.append(network[(town1_coord, town2_coord)])

        return minimal_network
