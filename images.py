from enum import Enum, auto

import pygame as pg

from colors import *


TILE_SIZE = (32, 32)
TANK_SIZE = (24, 24)


class ImageID(Enum):
    WALL = auto()
    BRICKS = auto()
    DOOR = auto()
    COOLER = auto()

    PLAYER = auto()
    MINIGUN = auto()
    CRATE = auto()
    BARREL = auto()


def make_wall_tile(color: pg.Color, bgcolor: pg.Color | None = None) -> pg.Surface:
    image = pg.Surface(TILE_SIZE).convert()
    if bgcolor:
        image.fill(bgcolor)
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


def make_door_tile(color: pg.Color, bgcolor: pg.Color | None = None) -> pg.Surface:
    image = pg.Surface(TILE_SIZE).convert()
    if bgcolor:
        image.fill(bgcolor)
    pg.draw.rect(image, color, pg.Rect(0, 0, *TILE_SIZE), 3)
    pg.draw.rect(image, color, pg.Rect(8, 8, 16, 16), 1)
    # Draw diagonal lines.
    pg.draw.line(image, color, (0, 0), (8, 8), 1)
    pg.draw.line(image, color, (0, TILE_SIZE[1]), (8, TILE_SIZE[1] - 8), 1)
    pg.draw.line(image, color, (TILE_SIZE[0], 0), (TILE_SIZE[0] - 8, 8), 1)
    pg.draw.line(image, color, TILE_SIZE, (TILE_SIZE[0] - 8, TILE_SIZE[1] - 8), 1)
    return image


def make_cooler_tile(color: pg.Color, bgcolor: pg.Color | None = None) -> pg.Surface:
    image = pg.Surface(TILE_SIZE).convert()
    if bgcolor:
        image.fill(bgcolor)
    pg.draw.rect(image, color, pg.Rect(0, 0, *TILE_SIZE), 3)
    # Draw diagonal lines.
    pg.draw.line(image, color, (0, 0), TILE_SIZE, 3)
    pg.draw.line(image, color, (0, TILE_SIZE[1]), (TILE_SIZE[0], 0), 3)
    return image


def make_player_tile(color: pg.Color) -> pg.Surface:
    image = pg.Surface(TANK_SIZE).convert()
    pg.draw.rect(image, color, pg.Rect(0, 0, *TANK_SIZE), 3)
    pg.draw.circle(image, color, (TANK_SIZE[0] // 2, TANK_SIZE[1] // 2), 7, 3)
    return image


def make_crate_tile(color: pg.Color, bgcolor: pg.Color | None = None) -> pg.Surface:
    image = pg.Surface(TANK_SIZE).convert()
    if bgcolor:
        image.fill(bgcolor)
    pg.draw.rect(image, color, pg.Rect(0, 0, *TANK_SIZE), 3)
    pg.draw.line(image, color, (8, 0), (8, 24), 1)
    pg.draw.line(image, color, (16, 0), (16, 24), 1)
    pg.draw.line(image, color, (0, 8), (24, 8), 1)
    pg.draw.line(image, color, (0, 16), (24, 16), 1)
    return image


def make_barrel_tile(color: pg.Color, bgcolor: pg.Color | None = None) -> pg.Surface:
    image = pg.Surface(TANK_SIZE).convert()
    if bgcolor:
        image.fill(bgcolor)
    pg.draw.rect(image, color, pg.Rect(0, 0, *TANK_SIZE), 3)
    pg.draw.line(image, color, (0, 0), (24, 24), 3)
    pg.draw.line(image, color, (24, 0), (0, 24), 3)
    return image


image_dict = {}


def make_images():
    global image_dict
    image_dict = {
        ImageID.WALL: make_wall_tile(MED_GRAY),
        ImageID.BRICKS: make_wall_tile(RED, SOFT_RED),
        ImageID.DOOR: make_door_tile(ORANGE, SOFT_ORANGE),
        ImageID.COOLER: make_cooler_tile(CYAN, SOFT_CYAN),

        ImageID.PLAYER: make_player_tile(WHITE),
        ImageID.MINIGUN: make_player_tile(ORANGE),
        ImageID.CRATE: make_crate_tile(BROWN, SOFT_BROWN),
        ImageID.BARREL: make_barrel_tile(RED, SOFT_RED),
    }
