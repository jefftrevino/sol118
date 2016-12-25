from matplotlib import pyplot
from shapely.geometry.polygon import Polygon
from shapely.affinity import scale, rotate
from chiplotle import (
    hpgl,
    instantiate_plotters
    )


class Plotter:

    def __init__(self, plot=False):
        self.plot = plot
        self.get_bounds()
        self.fig = pyplot.figure(1, figsize=(5, 5), dpi=300)
        pyplot.axis([-11640, 10720, -11640, 10720])
        self.subplot = self.fig.add_subplot(111)
        self.subplot.set_title('PlotterPreview')
        self.default_style = dict(
            color='#000000', alpha=0.6,
            linewidth=0.7, solid_capstyle='round')
        self.add_bounds_preview()
        if self.plot:
            plotters = instantiate_plotters()
            self.plotter = plotters[0]

    def get_bounds(self):
        self.bounds_poly = Polygon([
            (-11640, -8640),
            (-11640, 8640),
            (10720, 8640),
            (10720, -8640),
            (-11640, -8640),
            ])
        self.width = 11640 + 10720
        self.height = 8640 * 2
        self.scale_ratio = self.height / 1000

    def add_bounds_preview(self):
        self.preview_polygon(self.bounds_poly, color="#CCCCCC")

    def preview_polygon(self, poly, **kwargs):
        x, y = poly.exterior.xy
        style = self.default_style.copy()
        style.update(kwargs)
        self.subplot.plot(x, y, **style)

    def plot_polygon(self, poly, **kwargs):
        coords = [coord for coord in poly.exterior.coords]
        start = hpgl.PU([coords[0]])
        command = hpgl.PD(coords[1:])
        self.plotter.write(start)
        self.plotter.write(command)

    def add_polygon(self, poly, **kwargs):
        poly = scale(
            poly,
            xfact=self.scale_ratio,
            yfact=self.scale_ratio,
            origin=(0.0, 0.0))
        self.preview_polygon(poly, **kwargs)
        if self.plot:
            self.plot_polygon(poly, **kwargs)

    def save_preview(self):
        pyplot.savefig('plot.png', dpi=300)


def run():
    preview = Plotter(plot=False)
    poly = Polygon([
        (0, 0), (0, 200), (100, 100),
        (200, 200), (200, 0), (100, 80), (0, 0)])
    poly2 = rotate(poly, 45)

    preview.add_polygon(poly)
    preview.add_polygon(poly2, color='#FF0000')
    preview.save_preview()


if __name__ == '__main__':
    run()
