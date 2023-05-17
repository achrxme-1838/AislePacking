import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Circle

import random

CAVE_WIDTH = 20
CAVE_DEPTH = 40

CURRENT_MAX_WIDTH = 5
CURRENT_MAX_HEIGHT = 5

CURRENT_MIN_WIDTH = 2
CURRENT_MIN_HEIGHT = 2

# TODO : 좁은 틈 (CURRENT MIN HEIGHT)을 알면 potential point 만들 때 좁은 틈에 있는 2개 지우고, 좀 더 밖에 1개로 대체 가능

class Object:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

        self.covered_obj = None

    def __str__(self):
        return f"Object {self.name} : ({self.width}, {self.height})"


def sum_accumulated_width(surface_obj):
    accumulated_width = 0
    current_obj = surface_obj
    if current_obj is not None:
        while current_obj.covered_obj is not None:
            accumulated_width += current_obj.width
            current_obj = current_obj.covered_obj

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
    def __init__(self, surface_object, lower_bound, upper_bound):
        self.surface_object = surface_object
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        print(self.lower_bound, self.upper_bound)




class GlobalPlanner:
    def __init__(self):

        self.state_representor = StateRepresentor(CAVE_WIDTH, CAVE_DEPTH)

        self.left_wall = Object('LEFT_WALL', 0, CAVE_DEPTH)
        self.right_wall = Object('RIGHT_WALL', 0, CAVE_DEPTH)
        self.base_line = Object('BASE_LINE', CAVE_WIDTH, 0)

        # self.left_surface_list = [(self.left_wall, 0, CAVE_DEPTH)]
        # self.right_surface_list = [(self.right_wall, 0, CAVE_DEPTH)]
        self.left_surface_list = [Surface(self.left_wall, 0, CAVE_DEPTH)]
        self.right_surface_list = [Surface(self.right_wall, 0, CAVE_DEPTH)]

        self.potential_points = []

        self.generate_potential_points()

    # Update surface list when placing target_obj at the target_point
    def update_surface_list(self, target_obj, target_point):

        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            surface_list = self.left_surface_list[:]
        else:
            surface_list = self.right_surface_list[:]

        if target_point.lower_or_higher == 'LOWER':
            # Add new surface
            surface_list.append(Surface(target_obj, target_point.y, target_point.y + target_obj.height))
            for surface in surface_list:
                # change the lower bound of surface covered by target object
                if surface.surface_object == target_point.covered_obj:
                    surface.lower_bound = target_point.y + target_obj.height
        elif target_point.lower_or_higher == 'HIGHER':
            # Add new surface
            surface_list.append(Surface(target_obj, target_point.y - target_obj.height, target_point.y))
            for surface in surface_list:
                # change the upper bound of surface covered by target object
                if surface.surface_object == target_point.covered_obj:
                    surface.upper_bound = target_point.y - target_obj.height


        surface_list.sort(key=lambda x_: x_.lower_bound)

        if left_or_right_judge(target_obj) == 'LEFT_WALL':
            self.left_surface_list = surface_list[:]
        else:
            self.right_surface_list = surface_list[:]

    def object_generator(self, name, max_width, max_height):
        return Object(name, random.randint(CURRENT_MIN_WIDTH, max_width),
                      random.randint(CURRENT_MIN_HEIGHT, max_height))

    # TODO
    # for i, fruit in enumerate(my_list): ???
    def generate_potential_points(self):

        left_potential_points = []
        right_potential_points = []

        # generate left potential points
        for idx in range(len(self.left_surface_list)):
            x = sum_accumulated_width(self.left_surface_list[idx].surface_object)
            lower_y = self.left_surface_list[idx].lower_bound
            higher_y = self.left_surface_list[idx].upper_bound

            left_potential_points.append(
                PotentialPoint(x, lower_y, self.left_surface_list[idx].surface_object, 'LOWER'))
            left_potential_points.append(
                PotentialPoint(x, higher_y, self.left_surface_list[idx].surface_object, 'HIGHER'))

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
            x = CAVE_WIDTH - sum_accumulated_width(self.right_surface_list[idx].surface_object)
            lower_y = self.right_surface_list[idx].lower_bound
            higher_y = self.right_surface_list[idx].upper_bound

            right_potential_points.append(
                PotentialPoint(x, lower_y, self.right_surface_list[idx].surface_object, 'LOWER'))
            right_potential_points.append(
                PotentialPoint(x, higher_y, self.right_surface_list[idx].surface_object, 'HIGHER'))

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
        merged_potential_points = left_potential_points[:] + right_potential_points[:]

        # delete duplicate points
        for point in merged_potential_points:
            for compare in merged_potential_points:
                if (point.x == compare.x and point.y == compare.y) and (point != compare):
                    merged_potential_points.remove(point)
                    merged_potential_points.remove(compare)

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

        distance_left_list = []  # (PotentialPoint, width_left, height_left)

        for point in self.potential_points:
            width_left, height_left = point.distance_left_calculator(
                target_obj, self.left_surface_list, self.right_surface_list)
            distance_left_list.append((point, width_left, height_left))

        copied_distance_list = distance_left_list[:]
        distance_left_list.clear()
        for distance_left in copied_distance_list:
            if distance_left[1] > 0 and distance_left[2] > 0 and distance_left[1] - CURRENT_MAX_WIDTH > 0:
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
    def __init__(self, x, y, covered_obj, lower_or_higher):
        self.x = x
        self.y = y
        self.covered_obj = covered_obj
        self.lower_or_higher = lower_or_higher

        self.width_left = 0
        self.height_left = 0

        self.counter_obj = []

    # calculate left_distance after we place target at that specific point
    def distance_left_calculator(self, target_obj, left_surface_list, right_surface_list):

        free_width = 0
        free_height = 0

        y_level = self.y

        if left_or_right_judge(self.covered_obj) == 'LEFT_WALL':
            # calculate free_width for self(potential point)

            # find counter
            for idx in range(len(right_surface_list)):
                if (y_level > right_surface_list[idx].lower_bound) and (y_level < right_surface_list[idx].upper_bound):
                    self.counter_obj.append(right_surface_list[idx].surface_object)
                elif y_level == right_surface_list[idx].lower_bound:
                    self.counter_obj.append(right_surface_list[idx].surface_object)
                    self.counter_obj.append(right_surface_list[idx - 1].surface_object)
                elif y_level == right_surface_list[idx].upper_bound:
                    self.counter_obj.append(right_surface_list[idx].surface_object)
                    self.counter_obj.append(right_surface_list[idx + 1].surface_object)

                elif self.lower_or_higher == 'LOWER':
                    if (y_level + CURRENT_MAX_HEIGHT >= right_surface_list[idx].lower_bound) \
                            and (right_surface_list[idx].lower_bound >= y_level):
                        self.counter_obj.append(right_surface_list[idx].surface_object)
                elif self.lower_or_higher == 'HIGHER':
                    if (y_level - CURRENT_MAX_HEIGHT <= right_surface_list[idx].upper_bound) \
                            and (right_surface_list[idx].upper_bound <= y_level):
                        self.counter_obj.append(right_surface_list[idx].surface_object)

            current_max_width = sum_accumulated_width(self.counter_obj[0])
            for comparison in self.counter_obj:
                comparison_value = sum_accumulated_width(comparison)
                if comparison_value > current_max_width:
                    current_max_width = comparison_value

            free_width = CAVE_WIDTH - self.x - current_max_width

            # calculate free_height for self(potential point)
            for surface in left_surface_list:
                if self.covered_obj == surface.surface_object:
                    free_height = surface.upper_bound - surface.lower_bound

        elif left_or_right_judge(self.covered_obj) == 'RIGHT_WALL':

            for idx in range(len(left_surface_list)):
                if (y_level > left_surface_list[idx].lower_bound) and (y_level < left_surface_list[idx].upper_bound):
                    self.counter_obj.append(left_surface_list[idx].surface_object)
                elif y_level == left_surface_list[idx].lower_bound:
                    self.counter_obj.append(left_surface_list[idx].surface_object)
                    self.counter_obj.append(left_surface_list[idx - 1].surface_object)
                elif y_level == left_surface_list[idx].upper_bound:
                    self.counter_obj.append(left_surface_list[idx].surface_object)
                    self.counter_obj.append(left_surface_list[idx + 1].surface_object)

                elif self.lower_or_higher == 'LOWER':
                    if (y_level + CURRENT_MAX_HEIGHT >= left_surface_list[idx].lower_bound) \
                            and (left_surface_list[idx].lower_bound >= y_level):
                        self.counter_obj.append(left_surface_list[idx].surface_object)
                elif self.lower_or_higher == 'HIGHER':
                    if (y_level - CURRENT_MAX_HEIGHT <= left_surface_list[idx].upper_bound) \
                            and (left_surface_list[idx].upper_bound <= y_level):
                        self.counter_obj.append(left_surface_list[idx].surface_object)

            current_max_width = sum_accumulated_width(self.counter_obj[0])
            for comparison in self.counter_obj:
                comparison_value = sum_accumulated_width(comparison)
                if comparison_value > current_max_width:
                    current_max_width = comparison_value

            free_width = self.x - current_max_width

            for surface in right_surface_list:
                if self.covered_obj == surface.surface_object:
                    free_height = surface.upper_bound - surface.lower_bound

        self.width_left = free_width - target_obj.width
        self.height_left = free_height - target_obj.height

        return self.width_left, self.height_left

    def __str__(self):
        return f"Point ({self.x}, {self.y})"


def main():
    plt.ion()
    global_planner = GlobalPlanner()
    stop_animation = False

    def on_key(event):
        global stop_animation
        if event.key == 'q':
            stop_animation = True

    plt.connect('key_press_event', on_key)

    idx = 1

    while not stop_animation:
        obj = global_planner.object_generator(idx, CURRENT_MAX_WIDTH, CURRENT_MAX_HEIGHT)
        result = global_planner.packing_algorithm(obj)

        if result == 'Fail':
            global_planner.state_representor.draw_potential_points(global_planner.potential_points)
            print('Successfully packed ', idx-1, ' objects')
            print('Cannot packing', obj)
            print('Cave searching will be operated')
            break

        idx += 1

        plt.draw()
        plt.pause(0.4)

    plt.ioff()
    plt.show()

    # global_planner = GlobalPlanner()
    # ob1 = Object(1, 5, 5)
    # ob2 = Object(2, 2, 4)
    # ob3 = Object(3, 3, 10)
    # global_planner.packing_algorithm(ob1)
    # global_planner.packing_algorithm(ob2)
    # global_planner.packing_algorithm(ob3)
    #
    # global_planner.state_representor.draw_potential_points(global_planner.potential_points)
    #
    # plt.show()

if __name__ == "__main__":
    main()
