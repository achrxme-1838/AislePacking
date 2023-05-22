import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Circle

import random

AISLE_WIDTH = 20
AISLE_DEPTH = 40

CURRENT_MAX_WIDTH = 5
CURRENT_MAX_HEIGHT = 5

CURRENT_MIN_WIDTH = 2
CURRENT_MIN_HEIGHT = 2


class Object:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

        self.covered_obj = None

    def __str__(self):
        return f"Object {self.name} size=({self.width}, {self.height})"


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
        self.ax.set_title('AISLE')

        self.object_counter = 0

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


class Surface:
    def __init__(self, surface_object, lower_bound, upper_bound, x):
        self.surface_object = surface_object
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.x = x

    def __str__(self):
        return f"Surface {self.surface_object} : bounds({self.lower_bound}, {self.upper_bound}), x({self.x})"


class GlobalPlanner:
    def __init__(self):

        self.state_representor = StateRepresentor(AISLE_WIDTH, AISLE_DEPTH)

        self.left_wall = Object('LEFT_WALL', 0, AISLE_DEPTH)
        self.right_wall = Object('RIGHT_WALL', 0, AISLE_DEPTH)
        self.base_line = Object('BASE_LINE', AISLE_WIDTH, 0)

        self.left_surface_list = [Surface(self.left_wall, 0, AISLE_DEPTH, 0)]
        self.right_surface_list = [Surface(self.right_wall, 0, AISLE_DEPTH, AISLE_WIDTH)]

        self.potential_points = []

        self.generate_potential_points()

    # Update surface list when placing target_obj at the target_point
    def update_surface_list(self, target_obj, target_point):

        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            surface_list = self.left_surface_list[:]
            surface_x = target_point.x + target_obj.width
        else:
            surface_list = self.right_surface_list[:]
            surface_x = target_point.x - target_obj.width

        if target_point.lower_or_higher == 'LOWER':
            surface_list.append(Surface(target_obj, target_point.y, target_point.y + target_obj.height, surface_x))
            for surface in surface_list:
                # change the lower bound of surface covered by target object
                if surface.surface_object == target_point.covered_obj:
                    surface.lower_bound = target_point.y + target_obj.height

        elif target_point.lower_or_higher == 'HIGHER':
            surface_list.append(Surface(target_obj, target_point.y - target_obj.height, target_point.y, surface_x))
            for surface in surface_list:
                # change the upper bound of surface covered by target object
                if surface.surface_object == target_point.covered_obj:
                    surface.upper_bound = target_point.y - target_obj.height

        self.delete_fully_covered_surface(surface_list)

        surface_list.sort(key=lambda x_: x_.lower_bound)

        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            self.left_surface_list = surface_list[:]
        else:
            self.right_surface_list = surface_list[:]

    def delete_fully_covered_surface(self, surface_list):
        copied_surface_list = surface_list[:]
        surface_list.clear()
        for surface in copied_surface_list:
            if surface.lower_bound != surface.upper_bound:
                surface_list.append(surface)

    def object_generator(self, name, max_width, max_height):
        return Object(name, random.randint(CURRENT_MIN_WIDTH, max_width),
                      random.randint(CURRENT_MIN_HEIGHT, max_height))

    def generate_potential_points(self):

        left_potential_points = []
        right_potential_points = []

        # generate potential points
        for surface in self.left_surface_list:
            x = surface.x
            left_potential_points.append(
                PotentialPoint(x, surface.lower_bound, surface.surface_object, 'LOWER', surface))
            left_potential_points.append(
                PotentialPoint(x, surface.upper_bound, surface.surface_object, 'HIGHER', surface))

        for surface in self.right_surface_list:
            x = surface.x
            right_potential_points.append(
                PotentialPoint(x, surface.lower_bound, surface.surface_object, 'LOWER', surface))
            right_potential_points.append(
                PotentialPoint(x, surface.upper_bound, surface.surface_object, 'HIGHER', surface))

        # delete invalid potential points
        copied_left_potential_points = left_potential_points[:]
        left_potential_points.clear()
        for i, point in enumerate(copied_left_potential_points):
            exist_same_y = False
            for compare_point in copied_left_potential_points[:i] + copied_left_potential_points[i + 1:]:
                if point.y == compare_point.y:
                    exist_same_y = True
                    if point.x < compare_point.x:
                        if point not in left_potential_points:
                            left_potential_points.append(point)
                    elif point.x > compare_point.x:
                        if compare_point not in left_potential_points:
                            left_potential_points.append(compare_point)
            if (not exist_same_y) and point.y != AISLE_DEPTH:
                if point not in left_potential_points:
                    left_potential_points.append(point)

        copied_right_potential_points = right_potential_points[:]
        right_potential_points.clear()
        for i, point in enumerate(copied_right_potential_points):
            exist_same_y = False
            for compare_point in copied_right_potential_points[:i] + copied_right_potential_points[i + 1:]:
                if point.y == compare_point.y:
                    exist_same_y = True
                    if point.x > compare_point.x:
                        if point not in right_potential_points:
                            right_potential_points.append(point)
                    elif point.x < compare_point.x:
                        if compare_point not in right_potential_points:
                            right_potential_points.append(compare_point)
            if (not exist_same_y) and point.y != AISLE_DEPTH:
                if point not in right_potential_points:
                    right_potential_points.append(point)

        # merge potential points which have close y_distance
        for idx, point in enumerate(left_potential_points):
            if idx - 1 > 0 and idx < len(left_potential_points):
                lower_compare_point = left_potential_points[idx - 1]
                if point.x == lower_compare_point.x and point.y - lower_compare_point.y < CURRENT_MIN_HEIGHT:
                    for surface_idx, base_surface in enumerate(self.left_surface_list):
                        if base_surface == point.parent_surface:
                            upper_surface = self.left_surface_list[surface_idx + 1]
                            lower_surface = self.left_surface_list[surface_idx - 1]
                            if upper_surface.x < lower_surface.x:
                                upper_surface.lower_bound = base_surface.lower_bound
                                base_surface.upper_bound = base_surface.lower_bound
                            elif upper_surface.x > lower_surface.x:
                                lower_surface.upper_bound = base_surface.upper_bound
                                base_surface.lower_bound = base_surface.upper_bound
                            elif upper_surface.x == lower_surface.x:
                                lower_surface.upper_bound = base_surface.upper_bound
                                base_surface.lower_bound = base_surface.upper_bound

        for idx, point in enumerate(right_potential_points):
            if idx - 1 > 0 and idx < len(right_potential_points):
                lower_compare_point = right_potential_points[idx - 1]
                if point.x == lower_compare_point.x and point.y - lower_compare_point.y < CURRENT_MIN_HEIGHT:
                    for surface_idx, base_surface in enumerate(self.right_surface_list):
                        if base_surface == point.parent_surface:
                            upper_surface = self.right_surface_list[surface_idx + 1]
                            lower_surface = self.right_surface_list[surface_idx - 1]
                            if upper_surface.x > lower_surface.x:
                                upper_surface.lower_bound = base_surface.lower_bound
                                base_surface.upper_bound = base_surface.lower_bound
                            elif upper_surface.x < lower_surface.x:
                                lower_surface.upper_bound = base_surface.upper_bound
                                base_surface.lower_bound = base_surface.upper_bound
                            elif upper_surface.x == lower_surface.x:
                                lower_surface.upper_bound = base_surface.upper_bound
                                base_surface.lower_bound = base_surface.upper_bound

        self.delete_fully_covered_surface(self.left_surface_list)
        self.delete_fully_covered_surface(self.right_surface_list)

        merged_potential_points = left_potential_points[:] + right_potential_points[:]

        self.potential_points = merged_potential_points[:]

    def placing(self, target_obj, target_point):

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

        distance_left_list = []

        for point in self.potential_points:
            width_left, height_left = point.distance_left_calculator(
                target_obj, self.left_surface_list, self.right_surface_list)
            distance_left_list.append((point, width_left, height_left))

        copied_distance_list = distance_left_list[:]
        distance_left_list.clear()
        for distance_left in copied_distance_list:
            if distance_left[1] > 0 and distance_left[2] >= 0 and distance_left[1] - CURRENT_MAX_WIDTH > 0:
                distance_left_list.append(distance_left)

        if distance_left_list:
            current_nearest = distance_left_list[0][0]
            for compare in distance_left_list:
                if compare[0].y < current_nearest.y:
                    current_nearest = compare[0]

            target_obj.covered_obj = current_nearest.covered_obj
        else:
            current_nearest = None
            print("There is no point which can be packed")

        return current_nearest

    def packing_algorithm(self, target_obj):

        target_point = self.selecting_point(target_obj)

        if target_point is None:
            return 'Fail'

        # Placing the object(drawing)
        self.placing(target_obj, target_point)
        # Update the surface list if we place the target_obj at the target_point
        self.update_surface_list(target_obj, target_point)
        # Generate potential point using updated surface list
        self.generate_potential_points()

        return 'Success'


class PotentialPoint:
    def __init__(self, x, y, covered_obj, lower_or_higher, parent_surface):
        self.x = x
        self.y = y
        self.covered_obj = covered_obj
        # self.next_to_obj = next_to_obj
        self.lower_or_higher = lower_or_higher

        self.width_left = 0
        self.height_left = 0

        self.counter_surface_set = []

        self.parent_surface = parent_surface

    def counter_finder(self, counter_surface_list: list[Surface]):

        if self.lower_or_higher == 'LOWER':
            upper_range = self.y + CURRENT_MAX_HEIGHT
            lower_range = self.y
        elif self.lower_or_higher == 'HIGHER':
            upper_range = self.y
            lower_range = self.y - CURRENT_MAX_HEIGHT
        else:
            upper_range = None
            lower_range = None

        self.counter_surface_set.clear()

        for counter_surface in counter_surface_list:
            if lower_range <= counter_surface.upper_bound <= upper_range \
                    or lower_range <= counter_surface.lower_bound <= upper_range \
                    or counter_surface.lower_bound <= lower_range <= counter_surface.upper_bound \
                    or counter_surface.lower_bound <= upper_range <= counter_surface.upper_bound:

                if counter_surface.surface_object not in self.counter_surface_set:
                    self.counter_surface_set.append(counter_surface)

    # calculate left_distance after we place target at that specific point
    def distance_left_calculator(self, target_obj, left_surface_list, right_surface_list):

        free_width = 0
        if left_or_right_judge(self.covered_obj) == 'LEFT_WALL':
            self.counter_finder(right_surface_list)
            current_most_inner = min(self.counter_surface_set, key=lambda counter: counter.x).x
            free_width = current_most_inner - self.x

        elif left_or_right_judge(self.covered_obj) == 'RIGHT_WALL':
            self.counter_finder(left_surface_list)
            current_most_inner = max(self.counter_surface_set, key=lambda counter: counter.x).x
            free_width = self.x - current_most_inner

        free_height = self.parent_surface.upper_bound - self.parent_surface.lower_bound

        self.width_left = free_width - target_obj.width
        self.height_left = free_height - target_obj.height

        return self.width_left, self.height_left

    def __str__(self):
        return f"Point ({self.x}, {self.y})"


def main():
    global_planner = GlobalPlanner()
    for idx in range(1, 100):
        obj = global_planner.object_generator(idx, CURRENT_MAX_WIDTH, CURRENT_MAX_HEIGHT)
        print("=========================")
        result = global_planner.packing_algorithm(obj)

        if result == 'Fail':
            global_planner.state_representor.draw_potential_points(global_planner.potential_points)
            print('Successfully packed ', idx - 1, ' objects')
            print('Cannot packing', obj)
            print('AISLE searching will be operated')
            break
        plt.draw()
        # plt.pause(0.01)
        plt.pause(0.01)
    plt.show()

    # global_planner = GlobalPlanner()
    # ob1 = Object(1, 3, 5)
    # ob2 = Object(2, 4, 6)
    # ob3 = Object(3, 2, 3)
    # ob4 = Object(4, 5, 5)
    # ob5 = Object(5, 2, 3)
    #
    # global_planner.packing_algorithm(ob1)
    # global_planner.packing_algorithm(ob2)
    # global_planner.packing_algorithm(ob3)
    # global_planner.packing_algorithm(ob4)
    # print("=========================")
    # global_planner.packing_algorithm(ob5)
    #
    # global_planner.state_representor.draw_potential_points(global_planner.potential_points)
    # plt.show()



if __name__ == "__main__":
    main()
