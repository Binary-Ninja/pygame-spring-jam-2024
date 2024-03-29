from enum import Enum, auto

import pygame as pg

from colors import *


TILE_SIZE = (32, 32)


class ImageID(Enum):
    WALL = auto()


def make_wall_tile(color: pg.Color) -> pg.Surface:
    image = pg.Surface(TILE_SIZE).convert()
    pg.draw.rect(image, color, pg.Rect(0, 0, *TILE_SIZE), 3)
    pg.draw.line(image, color, (0, 7), (TILE_SIZE[0], 7), 1)
    pg.draw.line(image, color, (0, 15), (TILE_SIZE[0], 15), 1)
    pg.draw.line(image, color, (0, 23), (TILE_SIZE[0], 23), 1)
    return image


image_dict = {}


def make_images():
    global image_dict
    image_dict = {
        ImageID.WALL: make_wall_tile(MED_GRAY),
    }
