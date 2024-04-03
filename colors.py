BLACK = (0, 0, 0)
MED_GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SOFT_RED = (128, 32, 32)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
SOFT_CYAN = (0, 128, 128)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
SOFT_ORANGE = (128, 64, 0)
BROWN = (190, 150, 100)
SOFT_BROWN = (95, 75, 50)
PURPLE = (128, 0, 255)


def distance_within(a, b, dist: int | float) -> bool:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 <= dist ** 2


def distance_within_any(a, b, dist: int | float) -> bool:
    for p in b:
        if distance_within(a, p, dist):
            return True
    return False
