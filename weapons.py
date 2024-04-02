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


def destroy_cascade(tile_objs: pg.sprite.Group, first: pg.sprite.Sprite):
    to_kill: set[pg.sprite.Sprite] = set()
    to_collide: set[tuple[float, float]] = {first.rect.center}
    done = False
    while done is False:
        done = True
        for t in tile_objs:
            if t.id == first.id and distance_within_any(t.rect.center, to_collide, 36):
                to_kill.add(t)
                to_collide.add(t.rect.center)
                done = False
        # Kill the cascading tiles before next iteration to prevent infinite loops.
        for t in to_kill:
            tile_objs.remove(t)


def explosion(tile_objs: pg.sprite.Group, mob_objs: pg.sprite.Group, pos: tuple[float, float], dist: int, dmg: int):
    for t in tile_objs.copy():
        if distance_within(t.rect.center, pos, dist):
            if not t.immortal and tile_objs.has(t):  # Check if in original group because it could have been cascaded.
                t.health -= dmg
                t.last_hit = pg.time.get_ticks()
                if t.health <= 0:
                    tile_objs.remove(t)
                    if t.cascading:
                        destroy_cascade(tile_objs, t)

    for m in mob_objs.copy():
        if distance_within(m.rect.center, pos, dist):
            m.heat += dmg
            if not m.is_player:
                m.last_hit = pg.time.get_ticks()
                if m.heat >= m.max_heat:
                    mob_objs.remove(m)
                    if m.is_barrel:
                        explosion(tile_objs, mob_objs, m.rect.center, 32 * 2, 10)


class Bullet(pg.sprite.Sprite):
    def __init__(self, start: pg.Vector2 | tuple[int, int] | tuple[float, float],
                 target: pg.Vector2 | tuple[float, float], weapon_id: WeaponID, p: bool = False):
        pg.sprite.Sprite.__init__(self)
        self.id = weapon_id
        self.pos = pg.Vector2(start)
        self.vel = pg.Vector2(target).normalize() * weapon_speed[self.id]
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        self.p = p

    def update(self, dt: float, tile_objs: pg.sprite.Group, mob_objs: pg.sprite.Group):
        self.pos += self.vel * dt
        # Do collisions.
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        if hit := pg.sprite.spritecollideany(self, tile_objs):
            if not hit.immortal:
                hit.health -= weapon_damage[self.id]
                hit.last_hit = pg.time.get_ticks()
                if hit.health <= 0:
                    tile_objs.remove(hit)
                    if hit.cascading:
                        destroy_cascade(tile_objs, hit)
            self.kill()
        if hit := pg.sprite.spritecollideany(self, mob_objs):
            if hit.is_player:
                if not self.p:
                    hit.heat += weapon_damage[self.id]
                    if hit.heat > hit.max_heat:
                        hit.heat = hit.max_heat
                    self.kill()
            else:
                if self.p:
                    hit.heat += weapon_damage[self.id]
                    hit.last_hit = pg.time.get_ticks()
                    if hit.heat >= hit.max_heat:
                        mob_objs.remove(hit)
                        if hit.is_barrel:
                            explosion(tile_objs, mob_objs, hit.rect.center, 32 * 3, 10)
                    self.kill()
