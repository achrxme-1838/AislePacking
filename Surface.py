class Surface:
    def __init__(self, surface_object, lower_bound, upper_bound, x):
        self.surface_object = surface_object
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.x = x

    def __str__(self):
        return f"Surface {self.surface_object} : bounds({self.lower_bound}, {self.upper_bound}), x({self.x})"
