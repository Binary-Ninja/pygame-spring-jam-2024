from enum import Enum, auto
import random
import math

import pygame as pg

from colors import *


class WeaponID(Enum):
    MINIGUN = auto()
    SHOTGUN = auto()
    RICOCHET = auto()
    CANNON = auto()
    FLAME = auto()
    ROCKET = auto()


weapon_names = {
    WeaponID.MINIGUN: "MINIGUN",
    WeaponID.SHOTGUN: "SHOTGUN",
    WeaponID.RICOCHET: "RICOCHET",
    WeaponID.CANNON: "CANNON",
    WeaponID.FLAME: "FLAME",
    WeaponID.ROCKET: "ROCKET",
}

weapon_reload = {
    WeaponID.MINIGUN: 100,
    WeaponID.SHOTGUN: 1000,
    WeaponID.RICOCHET: 500,
    WeaponID.CANNON: 1000,
    WeaponID.FLAME: 100,
    WeaponID.ROCKET: 2000,
}

weapon_damage = {
    WeaponID.MINIGUN: 2,
    WeaponID.SHOTGUN: 2,
    WeaponID.RICOCHET: 10,
    WeaponID.CANNON: 25,
    WeaponID.FLAME: 5,
    WeaponID.ROCKET: 25,
}

weapon_speed = {
    WeaponID.MINIGUN: 500,
    WeaponID.SHOTGUN: 250,
    WeaponID.RICOCHET: 300,
    WeaponID.CANNON: 400,
    WeaponID.FLAME: 200,
    WeaponID.ROCKET: 150,
}

weapon_radius = {
    WeaponID.MINIGUN: 2,
    WeaponID.SHOTGUN: 2,
    WeaponID.RICOCHET: 4,
    WeaponID.CANNON: 6,
    WeaponID.FLAME: 10,
    WeaponID.ROCKET: 5,
}

weapon_spread = {
    WeaponID.MINIGUN: 4,
    WeaponID.SHOTGUN: 20,
    WeaponID.RICOCHET: 30,
    WeaponID.CANNON: 0,
    WeaponID.FLAME: 20,
    WeaponID.ROCKET: 0,
}

weapon_color = {
    WeaponID.MINIGUN: ORANGE,
    WeaponID.SHOTGUN: PURPLE,
    WeaponID.RICOCHET: CYAN,
    WeaponID.CANNON: DARK_GREEN,
    WeaponID.FLAME: YELLOW,
    WeaponID.ROCKET: RED,
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
        spread = pg.Vector2(random.randint(-weapon_spread[self.id], weapon_spread[self.id]))
        if self.id is WeaponID.SHOTGUN:
            self.vel = (spread + target).normalize() * (weapon_speed[self.id] + random.randint(-20, 20))
        else:
            self.vel = (spread + target).normalize() * weapon_speed[self.id]
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        self.p = p
        self.lifetime = pg.time.get_ticks()

    def update(self, dt: float, tile_objs: pg.sprite.Group, mob_objs: pg.sprite.Group, mpos: tuple[int, int],
               p: pg.sprite.Sprite, cs: pg.Vector2):
        if self.id is WeaponID.ROCKET:
            if self.p:
                self.vel = (mpos - (cs + self.pos)).normalize() * weapon_speed[self.id]
            else:
                self.vel = (pg.Vector2(p.rect.center) - self.pos).normalize() * weapon_speed[self.id]
        self.pos += self.vel * dt
        # Do collisions.
        self.rect = calc_bullet_rect(self.pos, weapon_radius[self.id])
        if hit := pg.sprite.spritecollideany(self, tile_objs):
            if self.id in (WeaponID.CANNON, WeaponID.ROCKET):
                explosion(tile_objs, mob_objs, self.rect.center, 48, weapon_damage[self.id])
                self.kill()
                return
            if not hit.immortal:
                hit.health -= weapon_damage[self.id]
                hit.last_hit = pg.time.get_ticks()
                if hit.health <= 0:
                    tile_objs.remove(hit)
                    if hit.cascading:
                        destroy_cascade(tile_objs, hit)
            if self.id is WeaponID.RICOCHET:
                self.pos -= self.vel * dt
                x_diff = math.fabs(hit.rect.centerx - self.rect.centerx)
                y_diff = math.fabs(hit.rect.centery - self.rect.centery)
                if x_diff > y_diff:
                    self.vel.x *= -1
                elif y_diff > x_diff:
                    self.vel.y *= -1
                else:
                    self.vel *= -1
            if self.id is not WeaponID.RICOCHET:
                self.kill()
            elif pg.time.get_ticks() - self.lifetime >= 2000:
                self.kill()
            return
        if hit := pg.sprite.spritecollideany(self, mob_objs):
            if hit.is_player:
                if not self.p:
                    if self.id in (WeaponID.CANNON, WeaponID.ROCKET):
                        explosion(tile_objs, mob_objs, self.rect.center, 48, weapon_damage[self.id])
                        self.kill()
                        return
                    hit.heat += weapon_damage[self.id]
                    if hit.heat > hit.max_heat:
                        hit.heat = hit.max_heat
                    self.kill()
            else:
                if self.p:
                    if self.id in (WeaponID.CANNON, WeaponID.ROCKET):
                        explosion(tile_objs, mob_objs, self.rect.center, 48, weapon_damage[self.id])
                        self.kill()
                        return
                    hit.heat += weapon_damage[self.id]
                    hit.last_hit = pg.time.get_ticks()
                    if hit.heat >= hit.max_heat:
                        mob_objs.remove(hit)
                        if hit.is_barrel:
                            explosion(tile_objs, mob_objs, hit.rect.center, 32 * 3, 20)
                    self.kill()
