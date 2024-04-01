from enum import Enum, auto

import pygame as pg

from colors import *


class WeaponID(Enum):
    MINIGUN = auto()


weapon_names = {
    WeaponID.MINIGUN: "MINIGUN",
}

weapon_damage = {
    WeaponID.MINIGUN: 2,
}

weapon_speed = {
    WeaponID.MINIGUN: 160,
}

weapon_radius = {
    WeaponID.MINIGUN: 2,
}

weapon_color = {
    WeaponID.MINIGUN: ORANGE,
}


class Bullet(pg.sprite.Sprite):
    def __init__(self, start: pg.Vector2, target: pg.Vector2, weapon_id: WeaponID):
        pg.sprite.Sprite.__init__(self)
        self.id = weapon_id
        self.pos = pg.Vector2(start)
        self.vel = (pg.Vector2(target) - self.pos).normalize() * weapon_speed[self.id]

    def update(self, dt: float):
        self.pos += self.vel * dt
