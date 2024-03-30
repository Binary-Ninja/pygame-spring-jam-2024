from enum import Enum, auto

import pygame as pg

from colors import *


TILE_SIZE = (32, 32)
TANK_SIZE = (24, 24)


class ImageID(Enum):
    WALL = auto()
    PLAYER = auto()


def make_wall_tile(color: pg.Color) -> pg.Surface:
    image = pg.Surface(TILE_SIZE).convert()
    pg.draw.rect(image, color, pg.Rect(0, 0, *TILE_SIZE), 3)
    # Draw horizontal lines.
    pg.draw.line(image, color, (0, 7), (TILE_SIZE[0], 7), 1)
    pg.draw.line(image, color, (0, 15), (TILE_SIZE[0], 15), 1)
    pg.draw.line(image, color, (0, 23), (TILE_SIZE[0], 23), 1)
    # Draw vertical lines.
    pg.draw.line(image, color, (TILE_SIZE[0] // 2, 0), (TILE_SIZE[0] // 2, 7), 1)
    pg.draw.line(image, color, (TILE_SIZE[0] // 2, 15), (TILE_SIZE[0] // 2, 23), 1)
    pg.draw.line(image, color, (TILE_SIZE[0] // 4, 7), (TILE_SIZE[0] // 4, 15), 1)
    pg.draw.line(image, color, (3*TILE_SIZE[0] // 4, 7), (3*TILE_SIZE[0] // 4, 15), 1)
    pg.draw.line(image, color, (TILE_SIZE[0] // 4, 23), (TILE_SIZE[0] // 4, TILE_SIZE[1]), 1)
    pg.draw.line(image, color, (3*TILE_SIZE[0] // 4, 23), (3*TILE_SIZE[0] // 4, TILE_SIZE[1]), 1)
    return image


def make_player_tile(color: pg.Color) -> pg.Surface:
    image = pg.Surface(TANK_SIZE).convert()
    pg.draw.rect(image, color, pg.Rect(0, 0, *TANK_SIZE), 3)
    pg.draw.circle(image, color, (TANK_SIZE[0] // 2, TANK_SIZE[1] // 2), 7, 3)
    return image


image_dict = {}


def make_images():
    global image_dict
    image_dict = {
        ImageID.WALL: make_wall_tile(MED_GRAY),
        ImageID.PLAYER: make_player_tile(WHITE),
    }
