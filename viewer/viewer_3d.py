import math

from matplotlib.patches import RegularPolygon
from vedo import *
import matplotlib.colors
from typing import List, Tuple

from model.hexgrid import HexGrid, ground_type_color, Coords


class Viewer3d:
    def __init__(self, hex_grid: HexGrid, z_scale: float = 0.1):
        self.hex_grid = hex_grid
        self.z_scale = z_scale

    def convert_2_hex_coords(self, coord: Coords):
        row, col = coord
        x = col * 1.5
        y = row * 1.5
        if col % 2:
            y += math.sqrt(3) / 2
        return x, y

    def create_3d_hexagon(self, tile: 'Tile') -> Tuple['hexagon_3d', 'label', 'town_shape']:
        color = ground_type_color[tile.ground]
        color_rgb = matplotlib.colors.to_rgb(color)

        x, y = self.convert_2_hex_coords(tile.coord)
        z = (tile.altitude + 0.1) * self.z_scale

        hexagon = Polygon(
            pos=(x, y, 0),
            r=1,
            nsides=6,
            c=color_rgb,
        )
        hexagon.rotate(angle=30, axis=(0, 0, 1), point=(x, y, 0))
        hexagon_3d = hexagon.extrude(z)

        label = Text3D(txt=tile.altitude, pos=(x, y, z), s=0.12, justify="center")

        town = None
        if tile.town:
            town = Cone(pos=(x, y, z+5*self.z_scale), r=0.6, height=10*self.z_scale, c='purple')

        return hexagon_3d, label, town

    def create_3d_hexagons(self) -> List:
        hexagons = []
        for tile in self.hex_grid.vertices:
            hexagons.append(self.create_3d_hexagon(tile))

        return hexagons

    def create_links(self, network, color: any = 'black', thick: int = 2):
        lines: List[Line] = []

        for path in network:
            path_3d = []
            for tile_i in path:
                x, y = self.convert_2_hex_coords(self.hex_grid.i_2_coord(tile_i))
                z = (self.hex_grid.vertices[tile_i].altitude + 2) * self.z_scale
                point = (x, y, z)
                path_3d.append(point)

            line = Line(path_3d, lw=thick, c=color)
            lines.append(line)

        return lines
        #
        #
        #     links: Tuple[int, int] = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        #
        #     for link in links:
        #         coord1 = self.hex_grid.i_2_coord(link[0])
        #         x1, y1 = self.convert_2_hex_coords(coord1)
        #         z1 = (self.hex_grid.vertices[link[0]].altitude - 8) * self.z_scale
        #
        #         coord2 = self.hex_grid.i_2_coord(link[1])
        #         x2, y2 = self.convert_2_hex_coords(coord2)
        #         z2 = (self.hex_grid.vertices[link[1]].altitude - 8) * self.z_scale
        #
        #         line = Line((x1, y1, z1+1), (x2, y2, z2+1), lw=5, c=color)
        #         lines.append(line)
        #
        # return lines


    def display(self):
        light_source_1 = Point(pos=(0, 0, 1000*self.z_scale), c='y')
        light_source_2 = Point(pos=(1.5*self.hex_grid.width, 0, 500 * self.z_scale), c='y')
        light_focal_point = Point(pos=(self.hex_grid.width, self.hex_grid.height, 50*self.z_scale), c='r')
        light1 = Light(
            pos=light_source_1,
            focal_point=light_focal_point,
            angle=360,
            c='w',
            intensity=1
        )
        light2 = Light(
            pos=light_source_2,
            focal_point=light_focal_point,
            angle=360,
            c='#fafadc',
            intensity=1
        )

        hexagons = [self.create_3d_hexagons()]
        dijkstra = self.create_links(self.hex_grid.shortest_network(), color='black')
        arpm = self.create_links(self.hex_grid.minimal_network(), color='red', thick=5)
        show(hexagons, dijkstra, arpm, light1, light2)
