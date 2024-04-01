from enum import Enum, auto

import pygame as pg

from colors import *


class WeaponID(Enum):
    MINIGUN = auto()


weapon_names = {
    WeaponID.MINIGUN: "MINIGUN",
}

weapon_reload = {
    WeaponID.MINIGUN: 100,
}

weapon_damage = {
    WeaponID.MINIGUN: 2,
}

weapon_speed = {
    WeaponID.MINIGUN: 500,
}

weapon_radius = {
    WeaponID.MINIGUN: 2,
}

weapon_color = {
    WeaponID.MINIGUN: ORANGE,
}


def calc_bullet_rect(pos: pg.Vector2, radius: int) -> pg.Rect:
    return pg.Rect(int(pos[0]) - radius, int(pos[1]) - radius, radius * 2, radius * 2)


class Bullet(pg.sprite.Sprite):
    def __init__(self, start: pg.Vector2 | tuple[int, int], target: pg.Vector2, weapon_id: WeaponID, p: bool = False):
        pg.sprite.Sprite.__init__(self)
        self.id = weapon_id
        self.pos = pg.Vector2(start)
        self.vel = target.normalize() * weapon_speed[self.id]
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        self.p = p

    def update(self, dt: float, tile_objs: pg.sprite.Group, mob_objs: pg.sprite.Group):
        self.pos += self.vel * dt
        # Do collisions.
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        if hit := pg.sprite.spritecollideany(self, tile_objs):
            if not hit.immortal:
                hit.health -= weapon_damage[self.id]
                if hit.health <= 0:
                    tile_objs.remove(hit)
                hit.last_hit = pg.time.get_ticks()
            self.kill()
        if hit := pg.sprite.spritecollideany(self, mob_objs):
            if hit.is_player:
                if not self.p:
                    hit.heat += weapon_damage[self.id]
                    if hit.heat >= hit.max_heat:
                        mob_objs.remove(hit)
                    hit.last_hit = pg.time.get_ticks()
                    self.kill()
            else:
                if self.p:
                    hit.heat += weapon_damage[self.id]
                    if hit.heat >= hit.max_heat:
                        mob_objs.remove(hit)
                    hit.last_hit = pg.time.get_ticks()
                    self.kill()
