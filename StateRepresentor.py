import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle
from matplotlib.patches import Circle

class StateRepresentor:
    def __init__(self, x_range, y_range):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, x_range)
        self.ax.set_ylim(0, y_range)

        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        self.ax.set_title('AISLE')

    def draw_rectangle(self, name, x, y, width, height, mode=None):
        if mode == 'WALL':
            rectangle = Rectangle((x, y), width, height, edgecolor='black', facecolor='black')
        else:
            rectangle = Rectangle((x, y), width, height, edgecolor='black', facecolor='none')
        self.ax.add_patch(rectangle)

        # text_x = x + width / 2
        # text_y = y + height / 2
        # number = name
        # self.ax.text(text_x, text_y, str(number), ha='center', va='center')

    def draw_potential_points(self, potential_points):
        for point in potential_points:
            x = point.x
            y = point.y
            circle = Circle((x, y), 0.5, facecolor='red')
            self.ax.add_patch(circle)

