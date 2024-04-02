from enum import Enum, auto

import pygame as pg

import images
from weapons import WeaponID


class MobID(Enum):
    PLAYER = auto()
    MINIGUN = auto()
    CRATE = auto()
    BARREL = auto()


char_to_mob_id = {
    "@": MobID.PLAYER,
    "m": MobID.MINIGUN,
    "%": MobID.CRATE,
    "^": MobID.BARREL,
}


mob_health = {
    MobID.PLAYER: 100,
    MobID.MINIGUN: 50,
    MobID.CRATE: 20,
    MobID.BARREL: 20,
}


mob_images = {
    MobID.PLAYER: images.ImageID.PLAYER,
    MobID.MINIGUN: images.ImageID.MINIGUN,
    MobID.CRATE: images.ImageID.CRATE,
    MobID.BARREL: images.ImageID.BARREL,
}

mob_weapon = {
    MobID.PLAYER: WeaponID.MINIGUN,
    MobID.MINIGUN: WeaponID.MINIGUN,
}


class Mob(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], mob_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos[0] + 4, pos[1] + 4)
        self.id = char_to_mob_id[mob_id]
        self.is_player = self.id is MobID.PLAYER
        self.is_barrel = self.id is MobID.BARREL
        self.weapon = mob_weapon.get(self.id, None)
        self.max_heat = mob_health.get(self.id, 100)
        self.heat = 0
        self.image = images.image_dict[mob_images[self.id]]
        self.rect = pg.Rect(pos, images.TANK_SIZE)
        self.last_hit = 0

    def update(self):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

