import math

from matplotlib.patches import RegularPolygon
from vedo import *
import matplotlib.colors
from typing import List, Tuple

from model.hexgrid import HexGrid, ground_type_color


class Viewer3d:
    def __init__(self, hex_grid: HexGrid, z_scale: float = 0.1):
        self.hex_grid = hex_grid
        self.z_scale = z_scale

    def create_3d_hexagon(self, tile: 'Tile') -> Tuple['hexagon_3d', 'label']:
        color = ground_type_color[tile.ground]
        color_rgb = matplotlib.colors.to_rgb(color)

        row, col = tile.coord
        x = col * 1.5
        y = row * 1.5
        if col % 2:
            y += math.sqrt(3) / 2

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

        return hexagon_3d, label

    def create_3d_hexagons(self) -> List:
        hexagons = []
        for tile in self.hex_grid.vertices:
            hexagons.append(self.create_3d_hexagon(tile))

        return hexagons

    def display(self):
        hexagons = [self.create_3d_hexagons()]
        show(hexagons)
