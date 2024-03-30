from enum import Enum, auto

import pygame as pg

import images


class TileID(Enum):
    WALL = auto()


char_to_tile_id = {
    "#": TileID.WALL,
}


tile_health = {
    TileID.WALL: 100,
}


tile_images = {
    TileID.WALL: images.ImageID.WALL,
}


class Tile(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], tile_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pos
        self.id = char_to_tile_id[tile_id]
        self.health = tile_health.get(self.id, 100)
        self.image = images.image_dict[tile_images[self.id]]
        self.rect = pg.Rect(pos, images.TILE_SIZE)
