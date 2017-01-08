from plotter import Drawing
from shapely.geometry import LineString, Point, GeometryCollection
from shapely.affinity import scale, rotate, translate
from shapely.ops import cascaded_union
from random import uniform, seed as set_seed
from math import floor


def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]


def run(seed_int):
    set_seed(seed_int)
    drawing = Drawing()
    x_offset = -11.5
    y_offset = -8.5
    horizontal_margin = .5
    vertical_margin = .5
    point_x_min = horizontal_margin
    point_x_max = 5-horizontal_margin
    point_y_min = vertical_margin
    point_y_max = 3-vertical_margin
    points = [
        Point(
            uniform(point_x_min, point_x_max) + x_offset,
            uniform(point_y_min, point_y_max) + y_offset)
        for x in range(50)
        ]
    coord_tuples = points_to_coord_tuples(points)
    for e,coord_tuple in enumerate(coord_tuples):
        for i in range(50):
            if e != i:
                line = LineString([coord_tuple, coord_tuples[i]])
                drawing.add(line)
    # line = LineString([(0, 0), (drawing.width, drawing.height)])
    drawing.add(line)
    drawing.preview(filepath='previews/preview-seed-' + str(seed_int) + '.svg')
    # drawing.plot()
    return drawing

if __name__ == '__main__':
    for seed_int in range(20, 40):
        drawing = run(seed_int)
