import random

import yaml

import Object
import DistanceMargin
import PotentialPoint
import StateRepresentor
import Surface

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

AISLE_WIDTH = config['AISLE_WIDTH']
AISLE_DEPTH = config['AISLE_DEPTH']

CURRENT_MAX_WIDTH = config['CURRENT_MAX_WIDTH']
CURRENT_MAX_HEIGHT = config['CURRENT_MAX_HEIGHT']

CURRENT_MIN_WIDTH = config['CURRENT_MIN_WIDTH']
CURRENT_MIN_HEIGHT = config['CURRENT_MIN_WIDTH']


def object_generator(mode, name, max_width, max_height):
    if mode == 'INT':
        return Object.Object(name, random.randint(CURRENT_MIN_WIDTH, max_width),
                             random.randint(CURRENT_MIN_HEIGHT, max_height))
    elif mode == 'FLOAT':
        return Object.Object(name, round(random.uniform(CURRENT_MIN_WIDTH, max_width), 1),
                             round(random.uniform(CURRENT_MIN_HEIGHT, max_height), 1))
    # elif mode == 'STRIP':
    #     return Object.Object(name, random.randint(CURRENT_MIN_WIDTH, 5),
    #                          random.randint(CURRENT_MIN_HEIGHT, 5))
    else:
        print('[ERROR] in object generation')


class GlobalPlanner:
    def __init__(self, wall_mode=None):

        self.state_representor = StateRepresentor.StateRepresentor(AISLE_WIDTH, AISLE_DEPTH)

        self.left_wall = Object.Object('LEFT_WALL', 0, AISLE_DEPTH)
        self.left_wall.left_or_right = 'LEFT'
        self.right_wall = Object.Object('RIGHT_WALL', 0, AISLE_DEPTH)
        self.right_wall.left_or_right = 'RIGHT'

        self.left_surface_list = [Surface.Surface(self.left_wall, 0, AISLE_DEPTH, 0)]
        self.right_surface_list = [Surface.Surface(self.right_wall, 0, AISLE_DEPTH, AISLE_WIDTH)]

        self.potential_points = []
        self.generate_potential_points()

        self.wall_area = 0

        if wall_mode == 'ROUGH_WALL':
            self.wall_generator('LEFT', wall_mode)
            self.wall_generator('RIGHT', wall_mode)
        elif wall_mode == 'REAL_WALL':
            self.wall_generator('LEFT', wall_mode)
            self.wall_generator('RIGHT', wall_mode)

    def wall_generator(self, left_or_right, wall_mode):

        default_width = 2

        while 1:
            if left_or_right == 'LEFT':
                left_points = [point for point in self.potential_points if
                               point.parent_surface.surface_object.left_or_right == 'LEFT']
                if left_points:
                    frontier_point = max(left_points, key=lambda point: point.y)
                else:
                    frontier_point = None
            elif left_or_right == 'RIGHT':
                right_points = [point for point in self.potential_points if
                                point.parent_surface.surface_object.left_or_right == 'RIGHT']
                if right_points:
                    frontier_point = max(right_points, key=lambda point: point.y)
                else:
                    frontier_point = None
            else:
                frontier_point = None

            if wall_mode == 'ROUGH_WALL':
                wall_obj = Object.Object(' ', random.randint(0, 7), random.randint(1, 10))
            elif wall_mode == 'REAL_WALL':
                increment = random.choice([-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
                default_width += increment
                if default_width <= 0:
                    default_width = 1
                if default_width >= AISLE_WIDTH / 2:
                    default_width = AISLE_WIDTH / 2
                wall_obj = Object.Object('', default_width, AISLE_DEPTH / 500)
            else:
                wall_obj = None

            if frontier_point.y + wall_obj.height >= AISLE_DEPTH:
                self.placing(wall_obj, frontier_point, 'WALL')
                self.wall_area += wall_obj.height * wall_obj.width
                self.update_surface_list(wall_obj, frontier_point)
                self.generate_potential_points()
                break

            else:
                self.placing(wall_obj, frontier_point, 'WALL')
                self.wall_area += wall_obj.height * wall_obj.width
                self.update_surface_list(wall_obj, frontier_point)
                self.generate_potential_points()

    # Update surface list when placing target_obj at the target_point
    def update_surface_list(self, target_obj, target_point):

        if target_obj.left_or_right == 'LEFT':
            surface_list = self.left_surface_list[:]
            surface_x = target_point.x + target_obj.width
        elif target_obj.left_or_right == 'RIGHT':
            surface_list = self.right_surface_list[:]
            surface_x = target_point.x - target_obj.width
        else:
            surface_list = None
            surface_x = None

        if target_point.lower_or_upper == 'LOWER':
            new_surface = Surface.Surface(target_obj, target_point.y, target_point.y + target_obj.height, surface_x)
            surface_list.append(new_surface)
            for surface in surface_list:
                # change the lower bound of surface covered by target object
                if surface.surface_object == target_point.base_obj:
                    surface.lower_bound = target_point.y + target_obj.height
                elif surface.lower_bound < target_point.y + target_obj.height and surface != new_surface \
                        and surface.upper_bound > target_point.y:
                    surface.lower_bound = target_point.y + target_obj.height

        elif target_point.lower_or_upper == 'UPPER':
            new_surface = Surface.Surface(target_obj, target_point.y - target_obj.height, target_point.y, surface_x)
            surface_list.append(new_surface)
            for surface in surface_list:
                # change the upper bound of surface covered by target object
                if surface.surface_object == target_point.base_obj:
                    surface.upper_bound = target_point.y - target_obj.height
                elif surface.upper_bound > target_point.y - target_obj.height and surface != new_surface \
                        and surface.lower_bound < target_point.y:
                    surface.upper_bound = target_point.y - target_obj.height

        self.delete_fully_covered_surface(surface_list)

        surface_list.sort(key=lambda x_: x_.lower_bound)

        if target_obj.left_or_right == 'LEFT':
            self.left_surface_list = surface_list[:]
        elif target_obj.left_or_right == 'RIGHT':
            self.right_surface_list = surface_list[:]

    def delete_fully_covered_surface(self, surface_list):
        copied_surface_list = surface_list[:]
        surface_list.clear()
        for surface in copied_surface_list:
            if surface.lower_bound < surface.upper_bound:
                surface_list.append(surface)

    def generate_potential_points(self):

        left_potential_points = []
        right_potential_points = []

        # generate potential points
        for surface in self.left_surface_list:
            x = surface.x
            left_potential_points.append(
                PotentialPoint.PotentialPoint(x, surface.lower_bound, surface.surface_object, 'LOWER', surface))
            left_potential_points.append(
                PotentialPoint.PotentialPoint(x, surface.upper_bound, surface.surface_object, 'UPPER', surface))

        for surface in self.right_surface_list:
            x = surface.x
            right_potential_points.append(
                PotentialPoint.PotentialPoint(x, surface.lower_bound, surface.surface_object, 'LOWER', surface))
            right_potential_points.append(
                PotentialPoint.PotentialPoint(x, surface.upper_bound, surface.surface_object, 'UPPER', surface))

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
                        if base_surface == point.parent_surface and surface_idx + 1 < len(self.left_surface_list):
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
                        if base_surface == point.parent_surface and surface_idx + 1 < len(self.right_surface_list):
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

        merged_potential_points = left_potential_points[:] + right_potential_points[:]

        self.potential_points = merged_potential_points[:]

    def placing(self, target_obj, target_point, mode=None):

        if target_point.parent_surface.surface_object.left_or_right == 'LEFT':
            target_obj.left_or_right = 'LEFT'
        elif target_point.parent_surface.surface_object.left_or_right == 'RIGHT':
            target_obj.left_or_right = 'RIGHT'

        if target_obj.left_or_right == 'LEFT':
            if target_point.lower_or_upper == 'LOWER':
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, target_obj.width, target_obj.height, mode)
            else:
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, target_obj.width, -target_obj.height, mode)

        elif target_obj.left_or_right == 'RIGHT':
            if target_point.lower_or_upper == 'LOWER':
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, -target_obj.width, target_obj.height, mode)
            else:
                self.state_representor.draw_rectangle(
                    target_obj.name, target_point.x, target_point.y, -target_obj.width, -target_obj.height, mode)

    def selecting_point(self, target_obj, mode: str, filtering_mode=None) -> PotentialPoint.PotentialPoint:

        filtered_point_list = self.filtering_point(target_obj, filtering_mode)
        if filtered_point_list == 'Fail':
            return 'Fail'

        else:
            if mode == 'NEAREST':
                selected_point = min(filtered_point_list,
                                     key=lambda criteria: criteria.potential_point.y).potential_point

            elif mode == 'MIN_HEIGHT':
                selected_point = min(filtered_point_list,
                                     key=lambda criteria: criteria.potential_point.height_left).potential_point
            elif mode == 'MIN_HEIGHT_WIDTH':
                selected_point = min(filtered_point_list, key=lambda criteria:
                criteria.potential_point.height_left * criteria.potential_point.width_left) \
                    .potential_point
            elif mode == 'RANDOM':
                selected_point = random.choice(filtered_point_list).potential_point
            else:
                selected_point = None
                print('[ERROR] mode error')

            return selected_point

    def filtering_point(self, target_obj, mode=None) -> list[DistanceMargin.DistanceMargin]:

        distance_margin_list = []  # O(1)

        # O(n^2)
        for point in self.potential_points:  # O(n)
            width_margin, height_margin = point.distance_margin_calculator(  # O(n)
                target_obj, self.left_surface_list, self.right_surface_list)
            distance_margin_list.append(DistanceMargin.DistanceMargin(point, width_margin, height_margin))

        copied_distance_margin_list = distance_margin_list[:]  # O(n)
        distance_margin_list.clear()  # O(n)
        for distance_margin in copied_distance_margin_list:  # O(n)

            if mode == 'STRIP_PACKING':
                if distance_margin.height_margin >= 0 and distance_margin.width_margin > 0:
                    distance_margin_list.append(distance_margin)
            else:
                if distance_margin.height_margin >= 0 and distance_margin.width_margin - CURRENT_MAX_WIDTH > 0:
                    distance_margin_list.append(distance_margin)

        if distance_margin_list:
            return distance_margin_list

        else:
            # When there is no point can be packed
            print("try urgent placing, called with", target_obj)
            for point in self.potential_points:  # O(n)
                urgent_width_margin, urgent_height_margin = point.urgent_distance_margin_calculator(  # O(n)
                    target_obj, self.left_surface_list, self.right_surface_list)
                distance_margin_list.append(
                    DistanceMargin.DistanceMargin(point, urgent_width_margin, urgent_height_margin))

            copied_distance_margin_list = distance_margin_list[:]
            distance_margin_list.clear()
            for distance_margin in copied_distance_margin_list:

                if mode == 'STRIP_PACKING':
                    if distance_margin.height_margin >= 0 and distance_margin.width_margin> 0:
                        distance_margin_list.append(distance_margin)
                else:
                    if distance_margin.height_margin >= 0 and distance_margin.width_margin - CURRENT_MAX_WIDTH > 0:
                        distance_margin_list.append(distance_margin)

            if distance_margin_list:
                return distance_margin_list
            else:
                print("There is no point which can be packed")
                return 'Fail'

    def packing_algorithm(self, target_obj, selecting_mode, filtering_mode=None):  # target_obj = N

        target_point = self.selecting_point(target_obj, selecting_mode, filtering_mode)  # O(n^2)

        if target_point == 'Fail':
            return 'Fail'

        # Placing the object(drawing)
        self.placing(target_obj, target_point)
        # Update the surface list if we place the target_obj at the target_point
        self.update_surface_list(target_obj, target_point)
        # Generate potential point using updated surface list
        self.generate_potential_points()

        return 'Success'
