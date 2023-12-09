from hexgrid import HexGrid, transfert_ensemble_proportionnel
from tile import Tile
from viewer import HexGridViewer

SCALE = 3
GRID_WIDTH  = 6 * SCALE
GRID_HEIGHT = 5 * SCALE

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


def altitude_2_alpha(altitude: int, alpha_min: float = 0.1, model: HexGrid = hex_grid) -> float:
    """
    @param alpha_min:
    @param altitude: ∈ ⟦0, 100⟧
    @return: alpha ∈ [alpha_min, 1]
    """
    return transfert_ensemble_proportionnel((0, model.get_altitude_max()), (alpha_min, 1), altitude)


def model_2_viewer(show_edges: bool = False, model: HexGrid = hex_grid, viewer_: HexGridViewer = viewer):
    for tile in model.vertices:
        viewer_.add_color(
            *tile.coord,
            color=ground_type_color[tile.ground],
            alpha=altitude_2_alpha(tile.altitude)
        )
    if show_edges:
        for edge in model.edges:
            thick = edge.weight//5
            viewer_.add_link(
                coord1=hex_grid.i_2_coord(edge.u),
                coord2=hex_grid.i_2_coord(edge.v),
                color="yellow" if thick <= 2 else "orange" if thick <= 3 else "red" if thick <= 4 else "purple",
                thick=thick
            )


for i in range(10):
    hex_grid = HexGrid(GRID_WIDTH, GRID_HEIGHT)
    viewer = HexGridViewer(GRID_WIDTH, GRID_HEIGHT)

    model_2_viewer(show_edges=True, model=hex_grid, viewer_=viewer)

    viewer.show(alias=ground_color_type,
                debug_coords=False,
                debug_altitude=True,
                altitudes=[tile.altitude for tile in hex_grid.vertices]
                )
