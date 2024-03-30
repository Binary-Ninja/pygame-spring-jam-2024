from enum import Enum, auto

import pygame as pg


import images


class MobID(Enum):
    PLAYER = auto()


char_to_mob_id = {
    "@": MobID.PLAYER,
}


mob_health = {
    MobID.PLAYER: 100,
}


mob_images = {
    MobID.PLAYER: images.ImageID.PLAYER,
}


class Mob(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], mob_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos)
        self.id = char_to_mob_id[mob_id]
        self.health = mob_health.get(self.id, 100)
        self.image = images.image_dict[mob_images[self.id]]
        self.rect = pg.Rect(pos, images.TANK_SIZE)

    def update(self):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

