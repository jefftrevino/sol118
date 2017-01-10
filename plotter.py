import svgwrite
import uuid
from shapely.geometry import Polygon, Point, box
from shapely.affinity import scale, translate
from chiplotle import (
    hpgl,
    instantiate_plotters
    )


def position_and_size_of_geom(geom):
    """Returns xmin, ymin, width, and height of a geometry
    based on its shapely `.bounds`
    """
    bounds = geom.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    return bounds[0], bounds[1], width, height


def px(*args):
    return [str(item) + "px" for item in args]


PLOTTER_UNITS_PER_INCH = 1018.39880656


class Drawing:
    """Assumes that everything is in inches

    Before plotting or making previews, all geometry is
    translated into plotter units.
    """

    def __init__(self, default_scale=PLOTTER_UNITS_PER_INCH):
        self.geoms = []
        self.get_bounds()
        self.default_preview_filepath = "previews/preview.svg"
        self.plotter = None
        self.scalar = default_scale
        self.paper = None
        self.paper_origin = Point(-11.7850105901, -8.765625)
        self.add_paper(24, 18)

    def get_bounds(self):
        self.bounds_poly = Polygon([
            (-11640, -8640),
            (-11640, 8640),
            (10720, 8640),
            (10720, -8640),
            (-11640, -8640),
            ])
        self.bounds = self.bounds_poly.bounds
        self.width = 11640 + 10720
        self.height = 8640 * 2

    def plot(self):
        if not self.plotter:
            plotters = instantiate_plotters()
            self.plotter = plotters[0]
        for geom in self.geoms:
            self.plot_geom(geom)

    def add(self, geom):
        self.geoms.append(self.scale_to_plotter_units(geom))

    def add_paper(self, width, height):
        """paper width and height are assumed to be in scalar units
            (inches by default)
        """
        geom = box(
            minx=0, miny=0,
            maxx=width, maxy=height
            )
        self.paper = translate(
            geom,
            xoff=self.paper_origin.x,
            yoff=self.paper_origin.y
            )
        self.paper_center = self.paper.centroid
        return self.paper

    def scale_to_plotter_units(self, geom):
        return scale(geom, self.scalar, self.scalar, origin=Point(0, 0))

    def clip_to_plotter_bounds(self):
        """Clips all geometries to the boundaries of the plotter
        """
        self.geoms = [
            self.bounds_poly.intersection(geom)
            for geom in self.geoms
        ]

    def plot_geom(self, geom):
        if hasattr(geom, 'coords'):
            # assume it is a linear ring or linestring
            self.plot_coords([coord for coord in geom.coords])
        elif hasattr(geom, 'exterior'):
            # assume it has a Polygon-like interface
            self.plot_geom(geom.exterior)
            for ring in geom.interiors:
                self.plot_geom(ring)
        elif hasattr(geom, 'geoms'):
            # assume this is a collection of objects
            for geom in geom.geoms:
                self.plot_geom(geom)
        else:
            raise NotImplementedError(
                "I don't know how to plot {}".format(type(geom)))

    def start_svg(self):
        preview_margin = 100
        screen_height = 600
        plotter_paper = self.scale_to_plotter_units(self.paper)
        paper_x, paper_y, paper_width, paper_height = \
            position_and_size_of_geom(plotter_paper)
        paper_top = paper_y + paper_height
        svg_width = paper_width + (preview_margin * 2)
        svg_height = paper_height + (preview_margin * 2)
        screen_width = (svg_width / float(svg_height)) * screen_height
        self.svg = svgwrite.Drawing(
            filename=self.default_preview_filepath,
            size=px(screen_width, screen_height),
            style="background-color: #ccc"
            )
        self.svg.viewbox(
            minx=paper_x - preview_margin,
            miny=(paper_top * -1) - preview_margin,
            width=svg_width,
            height=svg_height,
            )
        self.plotter_geom_group = self.svg.g(
            transform="scale(1, -1)"
            )
        # draw paper
        self.plotter_geom_group.add(self.svg.rect(
            insert=(paper_x, paper_y),
            size=(paper_width, paper_height),
            fill="white",
            ))

    def preview(self, filepath=None):
        self.start_svg()
        for geom in self.geoms:
            self.preview_geom(geom)
        self.svg.add(self.plotter_geom_group)
        self.add_bounds_preview()
        if not filepath:
            self.svg.save()
        else:
            self.svg.saveas(filepath)

    def preview_geom(self, geom, **kwargs):
        if hasattr(geom, 'xy'):
            # assume it is a linear ring or linestring
            self.plotter_geom_group.add(self.svg.polyline(
                points=geom.coords,
                stroke_width="1",
                fill="none",
                stroke="black",)
            )
        elif hasattr(geom, 'exterior'):
            # assume it has a Polygon-like interface
            self.preview_geom(geom.exterior, **kwargs)
            for ring in geom.interiors:
                self.preview_geom(ring, **kwargs)
        elif hasattr(geom, 'geoms'):
            # assume this is a collection of objects
            for geom in geom.geoms:
                self.preview_geom(geom, **kwargs)
        else:
            raise NotImplementedError(
                "I don't know how to preview {}".format(type(geom)))

    def add_bounds_preview(self):
        self.svg.add(self.svg.rect(
            insert=(self.bounds[0], self.bounds[1]),
            size=(self.width, self.height),
            stroke_width=25,
            stroke_dasharray=100,
            stroke="black",
            fill="none"
            ))

    def plot_coords(self, coords):
        start = hpgl.PU([coords[0]])
        self.plotter.write(start)
        threshold = 300
        while len(coords) > threshold:
            command = hpgl.PD(coords[:threshold])
            self.plotter.write(command)
            coords = coords[threshold:]
        command = hpgl.PD(coords)
        self.plotter.write(command)
        end = hpgl.PU([coords[-1]])
        self.plotter.write(end)

    def scale_to_fit(self, geom):
        return scale(
            geom,
            xfact=self.scale_ratio,
            yfact=self.scale_ratio,
            origin=(0.0, 0.0),
            )
