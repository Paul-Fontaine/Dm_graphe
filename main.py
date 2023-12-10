from hexgrid import HexGrid, transfert_ensemble_proportionnel
from tile import Tile
from viewer import HexGridViewer

ground_type_color = {
    "plain": "green",
    "water": "blue",
    "mountain": "grey",
    "snow": "white",
    "field": "yellow",
    "town": "brown"
}
ground_color_type = {v: k for k, v in ground_type_color.items()}


def altitude_2_alpha(model: HexGrid, altitude: int, alpha_min: float = 0.2, ) -> float:
    """
    @param model:
    @param alpha_min:
    @param altitude: ∈ ⟦0, 100⟧
    @return: alpha ∈ [alpha_min, 1]
    """
    return transfert_ensemble_proportionnel((0, model.get_altitude_max()), (alpha_min, 1), altitude)


def model_2_viewer(model: HexGrid, viewer_: HexGridViewer, show_edges: bool = False):
    for tile in model.vertices:
        viewer_.add_color(
            *tile.coord,
            color=ground_type_color[tile.ground],
            alpha=altitude_2_alpha(model, tile.altitude)
        )
    if show_edges:
        for edge in model.edges:
            thick = edge.weight//5
            viewer_.add_link(
                coord1=model.i_2_coord(edge.u),
                coord2=model.i_2_coord(edge.v),
                color="yellow" if thick <= 2 else "orange" if thick <= 3 else "red" if thick <= 4 else "purple",
                thick=thick
            )


def run(n: int = 1, scale: int = 4, show_edges: bool = False, debug_coords: bool = False, debug_altitude: bool = False):
    GRID_WIDTH = 6 * scale
    GRID_HEIGHT = 5 * scale

    for i in range(n):
        hex_grid = HexGrid(GRID_WIDTH, GRID_HEIGHT)
        viewer = HexGridViewer(GRID_WIDTH, GRID_HEIGHT)

        model_2_viewer(hex_grid, viewer, show_edges)

        viewer.show(alias=ground_color_type,
                    debug_coords=debug_coords,
                    debug_altitude=debug_altitude,
                    altitudes=[tile.altitude for tile in hex_grid.vertices]
                    )


run(
    n=10,
    scale=6,
    debug_altitude=False,
)
