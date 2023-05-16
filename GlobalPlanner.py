import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Circle

import random

CAVE_WIDTH = 20
CAVE_DEPTH = 40

CURRENT_MAX_WIDTH = 10


# TODO : delete next_to


class Object:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

        self.covered_obj = None

    def __str__(self):
        return f"Object {self.name} : ({self.width}, {self.height})"


def object_generator(name, max_width, max_height):
    return Object(name, random.randint(1, max_width), random.randint(1, max_height))


def sum_accumulated_width(surface):
    accumulated_width = 0
    current = surface
    if current is not None:
        while current.covered_obj is not None:
            accumulated_width += current.width
            current = current.covered_obj

    return accumulated_width


def left_or_right_judge(target_obj):
    current = target_obj
    if current is not None:
        while current.covered_obj is not None:
            current = current.covered_obj

    return current.name


class StateRepresentor:
    def __init__(self, x_range, y_range):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, x_range)
        self.ax.set_ylim(0, y_range)

        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        self.ax.set_title('Cave')

    def draw_rectangle(self, name, x, y, width, height):
        rectangle = Rectangle((x, y), width, height, edgecolor='black', facecolor='none')
        self.ax.add_patch(rectangle)

        text_x = x + width / 2
        text_y = y + height / 2
        number = name
        self.ax.text(text_x, text_y, str(number), ha='center', va='center')

    def draw_potential_points(self, potential_points):
        for point in potential_points:
            x = point.x
            y = point.y
            circle = Circle((x, y), 0.5, facecolor='red')
            self.ax.add_patch(circle)


class GlobalPlanner:
    def __init__(self):

        self.state_representor = StateRepresentor(CAVE_WIDTH, CAVE_DEPTH)

        self.left_wall = Object('LEFT_WALL', 0, CAVE_DEPTH)
        self.right_wall = Object('RIGHT_WALL', 0, CAVE_DEPTH)
        self.base_line = Object('BASE_LINE', CAVE_WIDTH, 0)

        self.left_surface_list = [(self.left_wall, 0, CAVE_DEPTH)]
        self.right_surface_list = [(self.right_wall, 0, CAVE_DEPTH)]

        self.potential_points = []

        self.generate_potential_points()

    def generate_potential_points(self):

        left_potential_points = []
        right_potential_points = []

        # generate left potential points
        for idx in range(len(self.left_surface_list)):

            x = sum_accumulated_width(self.left_surface_list[idx][0])
            lower_y = self.left_surface_list[idx][1]
            higher_y = self.left_surface_list[idx][2]
            if idx - 1 >= 0:
                lower_next_to = self.left_surface_list[idx - 1][0]
            else:
                lower_next_to = self.base_line

            if idx < len(self.left_surface_list) - 1:
                higher_next_to = self.left_surface_list[idx + 1][0]
            else:
                higher_next_to = None

            left_potential_points.append(
                PotentialPoint(x, lower_y, self.left_surface_list[idx][0], lower_next_to, 'LOWER'))
            left_potential_points.append(
                PotentialPoint(x, higher_y, self.left_surface_list[idx][0], higher_next_to, 'HIGHER'))

        for point in left_potential_points:
            value_for_removing = point.y
            for compare in left_potential_points:
                if compare.y == value_for_removing:
                    if compare.x > point.x:
                        left_potential_points.remove(compare)
                    elif compare.x < point.x:
                        if point in left_potential_points:
                            left_potential_points.remove(point)

        left_potential_points.pop()

        # generate right potential points

        for idx in range(len(self.right_surface_list)):

            x = CAVE_WIDTH - sum_accumulated_width(self.right_surface_list[idx][0])
            lower_y = self.right_surface_list[idx][1]
            higher_y = self.right_surface_list[idx][2]
            if idx - 1 >= 0:
                lower_next_to = self.right_surface_list[idx - 1][0]
            else:
                lower_next_to = self.base_line

            if idx < len(self.right_surface_list) - 1:
                higher_next_to = self.right_surface_list[idx + 1][0]
            else:
                higher_next_to = None

            right_potential_points.append(
                PotentialPoint(x, lower_y, self.right_surface_list[idx][0], lower_next_to, 'LOWER'))
            right_potential_points.append(
                PotentialPoint(x, higher_y, self.right_surface_list[idx][0], higher_next_to, 'HIGHER'))

        for point in right_potential_points:
            value_for_removing = point.y
            for compare in right_potential_points:
                if compare.y == value_for_removing:
                    if compare.x < point.x:
                        right_potential_points.remove(compare)
                    elif compare.x > point.x:
                        if point in right_potential_points:
                            right_potential_points.remove(point)

        right_potential_points.pop()

        # merge left and right
        merged_potential_points = left_potential_points + right_potential_points

        # delete duplicate points
        for point in merged_potential_points:
            for compare in merged_potential_points:
                if (point.x == compare.x and point.y == compare.y) and (point != compare):
                    merged_potential_points.remove(point)
                    merged_potential_points.remove(compare)

        self.potential_points = merged_potential_points[:]

    def update_surface_list(self, target_obj, target_point):

        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            surface_list = self.left_surface_list
        else:
            surface_list = self.right_surface_list

        if target_point.lower_or_higher == 'LOWER':
            surface_list.append((target_obj, target_point.y, target_point.y + target_obj.height))

            for surface in surface_list:
                if surface[0].name == target_obj.covered_obj.name:
                    surface_list.remove(surface)
                    if (target_point.y + target_obj.height) != surface[2]:
                        surface_list.append(
                            (surface[0], target_point.y + target_obj.height, surface[2]))

        elif target_point.lower_or_higher == 'HIGHER':
            surface_list.append((target_obj, target_point.y - target_obj.height, target_point.y))

            for surface in surface_list:
                if surface[0].name == target_obj.covered_obj.name:
                    surface_list.remove(surface)
                    if surface[1] != (target_point.y - target_obj.height):
                        surface_list.append(
                            (surface[0], surface[1], target_point.y - target_obj.height))

        self.left_surface_list.sort(key=lambda x_: x_[1])
        self.right_surface_list.sort(key=lambda x_: x_[1])

    def placing(self, target_obj, target_point):
        # TODO : it should be replaced to order for agent
        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            if target_point.lower_or_higher == 'LOWER':
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, target_obj.width, target_obj.height)
            else:
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, target_obj.width, -target_obj.height)
        elif left_or_right_judge(target_obj) == 'RIGHT_WALL':
            if target_point.lower_or_higher == 'LOWER':
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, -target_obj.width, target_obj.height)
            else:
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, -target_obj.width, -target_obj.height)

    def selecting_point(self, target_obj):

        distance_left_list = []  # (PotentialPoint, width_left, height_left)

        for point in self.potential_points:
            width_left, height_left = point.distance_left_calculator(
                target_obj, self.left_surface_list, self.right_surface_list)
            distance_left_list.append((point, width_left, height_left))

        copied_distance_list = distance_left_list[:]
        distance_left_list.clear()
        for distance_left in copied_distance_list:
            if not (distance_left[1] < 0 or distance_left[2] < 0 or distance_left[1] - CURRENT_MAX_WIDTH < 0):
                distance_left_list.append(distance_left)

        if distance_left_list:
            current_nearest = distance_left_list[0][0]
            # print(current_nearest)
            for compare in distance_left_list:
                if compare[0].y < current_nearest.y:
                    current_nearest = compare[0]
        else:
            current_nearest = None
            print("There is no point which can be packed")

        return current_nearest

    def packing_algorithm(self, target_obj):

        target_point = self.selecting_point(target_obj)
        # print('target_point', target_point.x, target_point.y)

        # target_obj : Object
        # target_point :PotentialPoint
        # potential_points : list of potential points

        target_obj.covered_obj = target_point.covered_obj
        self.placing(target_obj, target_point)
        self.update_surface_list(target_obj, target_point)
        self.generate_potential_points()


class PotentialPoint:
    def __init__(self, x, y, covered_obj, next_to, lower_or_higher):
        self.x = x
        self.y = y
        self.covered_obj = covered_obj
        self.next_to = next_to,
        self.lower_or_higher = lower_or_higher

        self.width_left = 0
        self.height_left = 0
        self.counter_obj = None

    # TODO
    # calculate left_distance if we placing target at that specific point
    def distance_left_calculator(self, target_obj, left_surface_list, right_surface_list):

        free_width = 0
        free_height = 0

        y_level = self.y

        if left_or_right_judge(self.covered_obj) == 'LEFT_WALL':
            # calculate free_width for self(potential point)
            # find counter
            for surface in right_surface_list:
                if (y_level >= surface[1]) and (y_level <= surface[2]):
                    self.counter_obj = surface[0]
            free_width = CAVE_WIDTH - self.x - sum_accumulated_width(self.counter_obj)

            # calculate free_height for self(potential point)

            for surface in left_surface_list:
                if self.covered_obj == surface[0]:
                    free_height = surface[2] - surface[1]

        elif left_or_right_judge(self.covered_obj) == 'RIGHT_WALL':

            for surface in left_surface_list:
                if (y_level >= surface[1]) and (y_level <= surface[2]):
                    self.counter_obj = surface[0]
            free_width = self.x - sum_accumulated_width(self.counter_obj)

            for surface in right_surface_list:
                if self.covered_obj == surface[0]:
                    free_height = surface[2] - surface[1]

        self.width_left = free_width - target_obj.width
        self.height_left = free_height - target_obj.height

        return self.width_left, self.height_left

    def __str__(self):
        return f"Point ({self.x}, {self.y})"


def main():
    global_panner = GlobalPlanner()

    for idx in range(1, 10):
        obj = object_generator(idx, CURRENT_MAX_WIDTH - 2, CURRENT_MAX_WIDTH - 2)
        global_panner.packing_algorithm(obj)

    global_panner.state_representor.draw_potential_points(global_panner.potential_points)

    plt.show()


if __name__ == "__main__":
    main()
