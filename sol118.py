from plotterWsvgPreview import Drawing
from shapely.geometry import LineString, Point, GeometryCollection
from shapely.affinity import scale, rotate, translate
from shapely.ops import cascaded_union
from random import randint, seed as set_seed
from math import floor

set_seed(2)


def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]


def make_hexagon(center, radius):
    # center is a Shapely point
    coords = [Point(center.x + radius, center.y)]
    point = coords[0]
    for x in range(6):
        new_point = rotate(point, 60 * x, origin=center)
        coords.append(new_point)
    coord_tuples = points_to_coord_tuples(coords)
    hexagon = Polygon(coord_tuples)
    return hexagon


def make_hexagons(num_hexagons, xmin, xmax, ymin, ymax, rmin, rmax):
    hexagons = []
    for x in range(num_hexagons):
        center_x = randint(xmin, xmax)
        center_y = randint(ymin, ymax)
        radius = randint(rmin, rmax)
        hexagons.append(
            make_hexagon(
                Point(center_x, center_y),
                radius
            )
        )
    return hexagons


def make_shank(hexagons):
    union = cascaded_union(hexagons)
    union_reflection = scale(union, -1.0, 1.0, origin=Point(0, 0))
    return cascaded_union([union, union_reflection])


def twist_shank(shank, center):
    shankles = [shank]
    for x in range(1, 6):
        shanklet = rotate(shank, 60 * x, origin=center)
        shankles.append(shanklet)
    return cascaded_union(shankles)


def make_snowflake_layer(num_hexagons, r_min, r_max):
    hexagons = make_hexagons(num_hexagons, 0, 35, 0, 500, r_min, r_max)
    shank = make_shank(hexagons)
    full_snowflake = twist_shank(shank, Point(0, 0))
    return full_snowflake


def make_snowflake(seed, origin, rotation=0):
    """origin is assumed to be a shapely.geometry.Point
    rotation is in degrees
    """
    set_seed(seed)
    base_layer = make_snowflake_layer(5, 50, 150)
    top_layer = make_snowflake_layer(20, 5, 50)
    snowflake = GeometryCollection([base_layer, top_layer])
    return rotate(
        translate(snowflake, xoff=origin.x, yoff=origin.y),
        rotation, origin=origin)


def run():
    drawing = Drawing()
    x_offset = -10000
    y_offset = -8000
    horizontal_margin = 1200
    vertical_margin = 1400
    point_x_min = horizontal_margin
    point_x_max = drawing.width-horizontal_margin
    point_y_min = vertical_margin
    point_y_max = drawing.height-vertical_margin
    points = [
        Point(
            randint(point_x_min, point_x_max) + x_offset,
            randint(point_y_min, point_y_max) + y_offset)
        for x in range(50)
        ]
    coord_tuples = points_to_coord_tuples(points)
    for e,coord_tuple in enumerate(coord_tuples):
        for i in range(50):
            if e != i:
                line = LineString([coord_tuple, coord_tuples[i]])
                drawing.add(line)
    # line = LineString([(0, 0), (drawing.width, drawing.height)])
    # drawing.add(line)
    drawing.preview()
    # drawing.plot()

if __name__ == '__main__':
    run()
