import math
import random
from typing import Tuple

from hexgrid import HexGrid, transfert_ensemble_proportionnel
from viewer import HexGridViewer, Circle, Rect

GRID_WIDTH =  40
GRID_HEIGHT = 30

ground_type_color = {
    "plain": "green",
    "water": "blue",
    "mountain": "grey",
    "snow": "white",
    "field": "yellow"
}
ground_color_type = {v: k for k, v in ground_type_color.items()}

hex_grid = HexGrid(GRID_WIDTH, GRID_HEIGHT)
viewer = HexGridViewer(GRID_WIDTH, GRID_HEIGHT)


def altitude_2_alpha(altitude: int, alpha_min: float = 0.1) -> float:
    """
    @param alpha_min:
    @param altitude: ∈ ⟦0, 100⟧
    @return: alpha ∈ [alpha_min, 1]
    """
    return transfert_ensemble_proportionnel((0, hex_grid.get_altitude_max()), (alpha_min, 1), altitude)


def model_2_viewer():
    for tile in hex_grid.vertices:
        viewer.add_color(*tile.coord, ground_type_color[tile.ground], altitude_2_alpha(tile.altitude))



model_2_viewer()

viewer.show(alias=ground_color_type,
            debug_coords=False,
            debug_altitude=True,
            altitudes=[tile.altitude for tile in hex_grid.vertices]
            )
