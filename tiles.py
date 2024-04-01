from enum import Enum, auto

import pygame as pg

import images


class TileID(Enum):
    WALL = auto()
    BRICKS = auto()
    DOOR = auto()
    COOLER = auto()


char_to_tile_id = {
    "#": TileID.WALL,
    "+": TileID.DOOR,
    "=": TileID.BRICKS,
    "~": TileID.COOLER,
}


tile_health = {
    TileID.WALL: 1000,
    TileID.DOOR: 100,
    TileID.BRICKS: 50,
    TileID.COOLER: 200,
}


tile_images = {
    TileID.WALL: images.ImageID.WALL,
    TileID.DOOR: images.ImageID.DOOR,
    TileID.BRICKS: images.ImageID.BRICKS,
    TileID.COOLER: images.ImageID.COOLER,
}


class Tile(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], tile_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pos
        self.id = char_to_tile_id[tile_id]
        self.immortal = self.id is TileID.WALL
        self.max_health = tile_health.get(self.id, 100)
        self.health = self.max_health
        self.image = images.image_dict[tile_images[self.id]]
        self.rect = pg.Rect(pos, images.TILE_SIZE)
        self.last_hit = 0
