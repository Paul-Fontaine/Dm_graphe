import time
import pandas as pd
from model.hexgrid import HexGrid


def fill_excel_file(file_path: str, min_towns: int, max_towns: int, min_scale: int, max_scale: int, precision: int):
    """
    fill an Excel file with the time needed to get the shortest network with dijkstra algorithm
    depending on the number of tiles and the number of cities
    @param file_path:
    @param min_towns:
    @param max_towns:
    @param min_scale: grid_width = grid_height = scale * 10
    @param max_scale:
    @param precision: number of iterations to make the average time
    """
    start = time.time()
    columns = []
    for i in range(min_scale, max_scale+1):
        column = []
        for j in range(min_towns, max_towns+1):
            durations = []
            for _ in range(precision):
                hex_grid = HexGrid(i*10, i*10, nb_towns=j)
                start_time = time.time()

                hex_grid.shortest_network()

                end_time = time.time()
                duration = end_time - start_time
                durations.append(duration)

            avg = sum(durations)/len(durations)
            column.append(avg)
            print("(scale: {}, nb_towns: {})  {:.4f} s".format(i, j, time.time()-start))

        columns.append(column)

    df = pd.DataFrame(
        data=columns,
        columns=[j for j in range(min_towns, max_towns+1)],
        index=[i*i*10*10 for i in range(min_scale, max_scale+1)]
    )
    df.to_excel(file_path, index=True)


fill_excel_file(
    file_path="dijkstra.xlsx",
    min_towns=2, max_towns=7,
    min_scale=2, max_scale=7,
    precision=3
)
