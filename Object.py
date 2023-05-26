class Object:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

        self.left_or_right = None

    def __str__(self):
        return f"Object {self.name} size=({self.width}, {self.height})"
