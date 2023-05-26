import yaml

# CURRENT_MAX_WIDTH = 5
# CURRENT_MAX_HEIGHT = 5

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

CURRENT_MAX_WIDTH = config['CURRENT_MAX_WIDTH']
CURRENT_MAX_HEIGHT = config['CURRENT_MAX_HEIGHT']


class PotentialPoint:
    def __init__(self, x, y, base_obj, lower_or_upper, parent_surface):
        self.x = x
        self.y = y
        self.base_obj = base_obj
        self.lower_or_upper = lower_or_upper

        self.width_left = 0
        self.height_left = 0

        self.counter_surface_set = []

        self.parent_surface = parent_surface

    def counter_finder(self, target_obj, counter_surface_list):  # O(n)

        if self.lower_or_upper == 'LOWER':
            upper_range = self.y + CURRENT_MAX_HEIGHT + target_obj.height
            lower_range = self.y - CURRENT_MAX_HEIGHT
        elif self.lower_or_upper == 'UPPER':
            upper_range = self.y + CURRENT_MAX_HEIGHT
            lower_range = self.y - CURRENT_MAX_HEIGHT - target_obj.height
        else:
            upper_range = None
            lower_range = None

        self.counter_surface_set.clear()  # O(n)

        for counter_surface in counter_surface_list:  # O(n)
            if lower_range <= counter_surface.upper_bound <= upper_range \
                    or lower_range <= counter_surface.lower_bound <= upper_range \
                    or counter_surface.lower_bound <= lower_range <= counter_surface.upper_bound \
                    or counter_surface.lower_bound <= upper_range <= counter_surface.upper_bound:

                if counter_surface.surface_object not in self.counter_surface_set:
                    self.counter_surface_set.append(counter_surface)

    # calculate left_distance after we place target at that specific point
    def free_distance_calculator(self, target_obj, left_surface_list, right_surface_list):  # O(n)

        free_width = 0
        free_height = self.parent_surface.upper_bound - self.parent_surface.lower_bound

        if self.base_obj.left_or_right == 'LEFT':
            self.counter_finder(target_obj, right_surface_list)  # O(n)
            current_most_inner = min(self.counter_surface_set, key=lambda counter: counter.x).x  # O(n)
            free_width = current_most_inner - self.x

        elif self.base_obj.left_or_right == 'RIGHT':
            self.counter_finder(target_obj, left_surface_list)
            current_most_inner = max(self.counter_surface_set, key=lambda counter: counter.x).x
            free_width = self.x - current_most_inner

        self.width_left = free_width - target_obj.width
        self.height_left = free_height - target_obj.height

        return self.width_left, self.height_left

    def urgent_free_distance_calculator(self, target_obj, left_surface_list, right_surface_list):

        free_width = 0
        free_height = 0

        if self.base_obj.left_or_right == 'LEFT':
            self.counter_finder(target_obj, right_surface_list)
            current_most_inner = min(self.counter_surface_set, key=lambda counter: counter.x).x
            free_width = current_most_inner - self.x

            vertical_line = self.x
            surface_index = left_surface_list.index(self.parent_surface)
            while left_surface_list[surface_index].x <= vertical_line:
                free_height += left_surface_list[surface_index].upper_bound \
                               - left_surface_list[surface_index].lower_bound
                if self.lower_or_upper == 'LOWER':
                    surface_index += 1
                elif self.lower_or_upper == 'UPPER':
                    surface_index -= 1

                if surface_index >= len(left_surface_list) or surface_index < 0:
                    break

        elif self.base_obj.left_or_right == 'RIGHT':
            self.counter_finder(target_obj, left_surface_list)
            current_most_inner = max(self.counter_surface_set, key=lambda counter: counter.x).x
            free_width = self.x - current_most_inner

            vertical_line = self.x
            surface_index = right_surface_list.index(self.parent_surface)
            while right_surface_list[surface_index].x >= vertical_line:
                free_height += right_surface_list[surface_index].upper_bound \
                               - right_surface_list[surface_index].lower_bound
                if self.lower_or_upper == 'LOWER':
                    surface_index += 1
                elif self.lower_or_upper == 'UPPER':
                    surface_index -= 1

                if surface_index >= len(right_surface_list) or surface_index < 0:
                    break

        self.width_left = free_width - target_obj.width
        self.height_left = free_height - target_obj.height

        return self.width_left, self.height_left

    def __str__(self):
        return f"Point ({self.x}, {self.y})"
