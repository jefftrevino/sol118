from plotter import Drawing
from shapely.geometry import LineString, Point, GeometryCollection
from shapely.affinity import scale, rotate, translate
from shapely.ops import cascaded_union
from random import uniform, seed as set_seed
from math import floor


def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]


def interpolate_along_line(numPoints, the_line):
    print("the line before:", len(the_line.xy[0]))
    '''
    Returns a new LineString that interpolates n points along the line.
    '''
    points = []
    for x in range(0, numPoints + 1):
        newPoint = the_line.interpolate(float(x)/numPoints, normalized=True)
        points.append(newPoint)
    coords = points_to_coord_tuples(points)
    output_line = LineString(coords)
    print("the line after:", len(output_line.xy[0]))
    return LineString(coords)


def run(seed_int):
    set_seed(seed_int)
    drawing = Drawing()
    x_offset = -11.5
    y_offset = -8.5
    horizontal_margin = 2
    vertical_margin = 2
    point_x_min = horizontal_margin
    point_x_max = 24 - horizontal_margin
    point_y_min = vertical_margin
    point_y_max = 18 - vertical_margin
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
                line = interpolate_along_line(10, line)
                drawing.add(line)
    # line = LineString([(0, 0), (drawing.width, drawing.height)])
    drawing.add(line)
    drawing.preview(filepath='previews/preview-seed-' + str(seed_int) + '.svg')
    # drawing.plot()
    return drawing

if __name__ == '__main__':
    for seed_int in range(3):
        drawing = run(seed_int)
