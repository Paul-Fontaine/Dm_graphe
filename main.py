from graph.matrixgraph import MatrixGraph
from viewer import HexGridViewer, Coords
import random

GRID_WIDTH, GRID_HEIGHT = 10, 10
hex_grid = HexGridViewer(GRID_WIDTH, GRID_HEIGHT)

vertices_names = [f"({i}, {j})" for i in range(GRID_HEIGHT) for j in range(GRID_WIDTH)]
graph = MatrixGraph('map', vertices_names)

ground_types = ["water", "void", "mountain", "plains", "city"]
ground_types_probabilities = [0.15, 0, 0.25, 0.5, 0.1]
color_2_type = {"blue": "water", "white": "void", "grey": "mountain", "green":"plains", "red": "city"}
type_2_color = {value: key for key, value in color_2_type.items()}
tiles_ground_type = [random.choices(ground_types, ground_types_probabilities)[0] for _ in range(GRID_WIDTH*GRID_HEIGHT)]

tiles_altitude = [random.uniform(0, 100) for _ in range(GRID_WIDTH*GRID_HEIGHT)]


def coords_2_index(coords: Coords, grid_width: int = GRID_WIDTH, grid_height: int = GRID_HEIGHT) -> int:
    y, x = coords
    if not (0 <= x < grid_width) or not (0 <= y < grid_height):
        raise ValueError(f"Error: Coordinates {coords} out of range")
    return y * grid_width + x


def index_2_coords(i: int, grid_width: int = GRID_WIDTH, grid_height: int = GRID_HEIGHT) -> Coords:
    if not (0 <= i < GRID_WIDTH * GRID_HEIGHT):
        raise ValueError(f"Error: Index {i} out of range")
    return i // grid_width, i % grid_width


def coords_2_str(coords: Coords) -> str:
    return str(coords)


def link(tile1: Coords, tile2: Coords, g: MatrixGraph = graph) -> None:
    g.add_edge(coords_2_index(tile1), coords_2_index(tile2))


def apply_links_2_hex_grid(color: str = "purple") -> None:
    for i in range(GRID_HEIGHT*GRID_WIDTH):
        for j in range(GRID_WIDTH*GRID_WIDTH):
            if graph.matrix[i][j] >= 1:
                hex_grid.add_link(index_2_coords(i), index_2_coords(j), color)


def apply_ground_type_2_hex_grid() -> None:
    for i, ground_type in enumerate(tiles_ground_type):
        color = type_2_color[ground_type]
        coords = index_2_coords(i)
        hex_grid.add_color(*coords, color)


def main():
    link((0, 0), (0, 1))
    link((1, 1), (0, 1))

    apply_links_2_hex_grid()

    apply_ground_type_2_hex_grid()

    hex_grid.show(debug_coords=True, alias=color_2_type)


if __name__ == "__main__":
    main()




