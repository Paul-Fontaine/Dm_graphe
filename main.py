from typing import List, Tuple

from model.hexgrid import HexGrid, transfert_ensemble_proportionnel, ground_type_color, ground_color_type
from viewer.viewer import HexGridViewer, Circle
from viewer.viewer_3d import Viewer3d


def altitude_2_alpha(model: HexGrid, altitude: int, alpha_min: float) -> float:
    """
    @param model:
    @param alpha_min:
    @param altitude: ∈ ⟦0, 100⟧
    @return: alpha ∈ [alpha_min, 1]
    """
    return transfert_ensemble_proportionnel((0, model.get_altitude_max()), (alpha_min, 1), altitude)


def model_2_viewer(
        model: HexGrid,
        viewer_: HexGridViewer,
        alpha_min: float,

        show_edges: bool = False,
        show_BFS_network: bool = False,
        show_dijkstra_network: bool = False,
        show_arpm_network: bool = False
):

    for tile in model.vertices:
        # add colors to viewer
        viewer_.add_color(
            *tile.coord,
            color=ground_type_color[tile.ground],
            alpha=altitude_2_alpha(model, tile.altitude, alpha_min) if tile.ground != "volcano"
            else altitude_2_alpha(model, tile.altitude, alpha_min=0.7)  # volcanos are black not gray !
        )
        # add towns to viewer
        if tile.town:
            viewer_.add_symbol(*tile.coord, Circle("purple"))

    def add_links(path , color: str, thick: int = 1):
        links: List[Tuple[int, int]] = [(path[i], path[i + 1]) for i in range(len(path) - 1)]  # [1,2,3, ...] -> [(1,2), (2,3) ...]
        for link in links:
            coord1 = model.i_2_coord(link[0])
            coord2 = model.i_2_coord(link[1])
            viewer_.add_link(coord1, coord2, color, thick)

    if show_BFS_network:
        for path in model.network():
            add_links(path, "grey", thick=1)

    if show_dijkstra_network:
        for path in model.shortest_network():
            add_links(path, "black", thick=1)

    if show_arpm_network:
        for path in model.minimal_network():
            add_links(path, "red", thick=2)

    if show_edges:
        for edge in model.edges:
            thick = edge.weight // 10
            if thick >= 5:
                thick = 5
            viewer_.add_link(
                coord1=model.i_2_coord(edge.u),
                coord2=model.i_2_coord(edge.v),
                color="yellow" if thick <= 2 else "orange" if thick <= 3 else "red" if thick <= 4 else "purple",
                thick=thick
            )


def run(
        n: int = 1, scale: int = 4,
        alpha_min: float = 0.2,
        nb_of_towns: int = -1,
        debug_coords: bool = False,
        debug_altitude: bool = False,
        show_edges: bool = False,
        show_BFS_network: bool = False,
        show_dijkstra_network: bool = False,
        show_arpm_network: bool = False,
        mode: str = "2d"
):
    """
    This function generate a model and display it, it repeats n times.
    @param n: number of map generated
    @param scale: set the size of the map, the dimensions of the map are 6*scale, 5*scale so the hexagonal map will look as a square
    @param alpha_min: set the minimum value for transaprency in the 2d model
    @param nb_of_towns: if it's not specified it will be random
    @param debug_coords: if True it will print the coordinates inside the tiles in the 2d model
    @param debug_altitude: if True it will print the altitudes in the 2d model
    @param show_edges: if True it will show the weight of edges
    @param show_BFS_network: if True it will calculate and display the network without the terrain and altitude constraints
    @param show_dijkstra_network: if True it will calculate and display the netwotk with the terrain and altitude constraints
    @param show_arpm_network: if True it will calculate and display the minimal network that connects all towns
    @param mode: can be "2d", "3d" or "both"
    """
    GRID_WIDTH = 6 * scale
    GRID_HEIGHT = 5 * scale
    hex_grid = HexGrid(GRID_WIDTH, GRID_HEIGHT, nb_of_towns)

    if mode in {"2d", "both"}:
        for i in range(n):
            hex_grid = HexGrid(GRID_WIDTH, GRID_HEIGHT, nb_of_towns)
            viewer = HexGridViewer(GRID_WIDTH, GRID_HEIGHT)

            model_2_viewer(
                hex_grid,
                viewer,
                alpha_min,
                show_edges,
                show_BFS_network,
                show_dijkstra_network,
                show_arpm_network
            )

            viewer.show(
                alias=ground_color_type,
                debug_coords=debug_coords,
                debug_altitude=debug_altitude,
                altitudes=[tile.altitude for tile in hex_grid.vertices]
            )

    if mode in {"3d", "both"}:
        viewer = Viewer3d(hex_grid, z_scale=0.15)
        viewer.display()

# the next 3 calls to run will show you the project steps
# you can simply run the main and then close the viewer window to go to the next step

# generate 3 basic maps, the number of city is random
run(
    n=3,
    scale=6,
    alpha_min=0.2,
    debug_altitude=True,
    mode="2d"
)

# generate 3 maps to see the networks
run(
    n=3,
    scale=6,
    alpha_min=0.4,
    nb_of_towns=8,
    show_BFS_network=True,
    show_dijkstra_network=True,
    show_arpm_network=True,
    mode="2d"
)

# generate a 3d map
run(
    n=1,
    scale=6,
    alpha_min=0.2,
    show_dijkstra_network=True,
    show_arpm_network=True,
    mode="both"
)
