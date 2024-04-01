from enum import Enum, auto

import pygame as pg


import images


class MobID(Enum):
    PLAYER = auto()
    MINIGUN = auto()
    CRATE = auto()


char_to_mob_id = {
    "@": MobID.PLAYER,
    "m": MobID.MINIGUN,
    "%": MobID.CRATE,
}


mob_health = {
    MobID.PLAYER: 100,
    MobID.MINIGUN: 20,
    MobID.CRATE: 10,
}


mob_images = {
    MobID.PLAYER: images.ImageID.PLAYER,
    MobID.MINIGUN: images.ImageID.MINIGUN,
    MobID.CRATE: images.ImageID.CRATE,
}


class Mob(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], mob_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos[0] + 4, pos[1] + 4)
        self.id = char_to_mob_id[mob_id]
        self.max_heat = mob_health.get(self.id, 100)
        self.heat = 0
        self.image = images.image_dict[mob_images[self.id]]
        self.rect = pg.Rect(pos, images.TANK_SIZE)

    def update(self):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

