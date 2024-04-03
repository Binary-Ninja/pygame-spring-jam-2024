from enum import Enum, auto

import pygame as pg

import images
import weapons
from weapons import WeaponID, weapon_reload, Bullet, explosion
from colors import *


class MobID(Enum):
    PLAYER = auto()
    MINIGUN = auto()
    SHOTGUN = auto()
    CANNON = auto()
    FLAME = auto()
    ROCKET = auto()
    BOMB = auto()
    RICOCHET = auto()
    CRATE = auto()
    BARREL = auto()
    MINIGUN_T = auto()
    SHOTGUN_T = auto()
    CANNON_T = auto()
    FLAME_T = auto()
    ROCKET_T = auto()
    BOMB_T = auto()
    RICOCHET_T = auto()


char_to_mob_id = {
    "@": MobID.PLAYER,
    "m": MobID.MINIGUN,
    "s": MobID.SHOTGUN,
    "c": MobID.CANNON,
    "f": MobID.FLAME,
    "r": MobID.ROCKET,
    "i": MobID.RICOCHET,
    "b": MobID.BOMB,
    "M": MobID.MINIGUN_T,
    "S": MobID.SHOTGUN_T,
    "C": MobID.CANNON_T,
    "F": MobID.FLAME_T,
    "R": MobID.ROCKET_T,
    "I": MobID.RICOCHET_T,
    "B": MobID.BOMB_T,
    "%": MobID.CRATE,
    "^": MobID.BARREL,
}

mob_health = {
    MobID.PLAYER: 100,
    MobID.MINIGUN: 50,
    MobID.SHOTGUN: 50,
    MobID.CANNON: 75,
    MobID.FLAME: 30,
    MobID.ROCKET: 75,
    MobID.RICOCHET: 60,
    MobID.BOMB: 75,
    MobID.CRATE: 25,
    MobID.BARREL: 25,

    MobID.MINIGUN_T: 100,
    MobID.SHOTGUN_T: 100,
    MobID.CANNON_T: 125,
    MobID.FLAME_T: 100,
    MobID.ROCKET_T: 125,
    MobID.RICOCHET_T: 100,
    MobID.BOMB_T: 100,
}

mob_speed = {
    MobID.MINIGUN: 50,
    MobID.PLAYER: 80,
    MobID.SHOTGUN: 60,
    MobID.CANNON: 60,
    MobID.FLAME: 40,
    MobID.ROCKET: 60,
    MobID.BOMB: 90,
    MobID.RICOCHET: 60,
}

mob_images = {
    MobID.PLAYER: images.ImageID.PLAYER,
    MobID.MINIGUN: images.ImageID.MINIGUN,
    MobID.SHOTGUN: images.ImageID.SHOTGUN,
    MobID.CANNON: images.ImageID.CANNON,
    MobID.FLAME: images.ImageID.FLAME,
    MobID.ROCKET: images.ImageID.ROCKET,
    MobID.BOMB: images.ImageID.BOMB,
    MobID.CRATE: images.ImageID.CRATE,
    MobID.BARREL: images.ImageID.BARREL,
    MobID.RICOCHET: images.ImageID.RICOCHET,
    MobID.RICOCHET_T: images.ImageID.RICOCHET_T,
    MobID.MINIGUN_T: images.ImageID.MINIGUN_T,
    MobID.SHOTGUN_T: images.ImageID.SHOTGUN_T,
    MobID.CANNON_T: images.ImageID.CANNON_T,
    MobID.FLAME_T: images.ImageID.FLAME_T,
    MobID.ROCKET_T: images.ImageID.ROCKET_T,
    MobID.BOMB_T: images.ImageID.BOMB_T,
}

mob_weapon = {
    MobID.PLAYER: WeaponID.MINIGUN,
    MobID.MINIGUN: WeaponID.MINIGUN,
    MobID.SHOTGUN: WeaponID.SHOTGUN,
    MobID.CANNON: WeaponID.CANNON,
    MobID.FLAME: WeaponID.FLAME,
    MobID.ROCKET: WeaponID.ROCKET,
    MobID.BOMB: WeaponID.MINIGUN,
    MobID.RICOCHET: WeaponID.RICOCHET,
    MobID.MINIGUN_T: WeaponID.MINIGUN,
    MobID.SHOTGUN_T: WeaponID.SHOTGUN,
    MobID.CANNON_T: WeaponID.CANNON,
    MobID.FLAME_T: WeaponID.FLAME,
    MobID.ROCKET_T: WeaponID.ROCKET,
    MobID.BOMB_T: WeaponID.MINIGUN,
    MobID.RICOCHET_T: WeaponID.RICOCHET,
}


class Mob(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], mob_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos[0] + 4, pos[1] + 4)
        self.id = char_to_mob_id[mob_id]
        self.is_player = self.id is MobID.PLAYER
        self.is_barrel = self.id is MobID.BARREL
        self.is_prop = self.id in (MobID.BARREL, MobID.CRATE)
        self.weapon = mob_weapon.get(self.id, None)
        self.max_heat = mob_health.get(self.id, 100)
        self.heat = 0
        self.image = images.image_dict[mob_images[self.id]]
        self.rect = pg.Rect(pos, images.TANK_SIZE)
        self.update_rect()
        self.last_hit = 0
        self.reload_timer = pg.time.get_ticks()
        self.is_turret = self.id in (MobID.MINIGUN_T, MobID.SHOTGUN_T, MobID.RICOCHET_T, MobID.CANNON_T, MobID.FLAME_T,
                                     MobID.ROCKET_T, MobID.BOMB_T)

    def update_rect(self):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

    def fire_weapon(self, target: tuple[float, float], bullets: pg.sprite.Group):
        if pg.time.get_ticks() - self.reload_timer >= weapon_reload[self.weapon]:
            self.reload_timer = pg.time.get_ticks()
            b = Bullet(self.rect.center, pg.Vector2(target) - self.rect.center, self.weapon)
            bullets.add(b)
            if self.weapon is weapons.WeaponID.SHOTGUN:
                for _ in range(9):
                    b = Bullet(self.rect.center, pg.Vector2(target) - self.rect.center, self.weapon)
                    bullets.add(b)

    def update(self, dt: float, tile_objs: pg.sprite.Group,
               mob_objs: pg.sprite.Group, player: pg.sprite.Sprite, bullets: pg.sprite.Group) -> bool:
        # Props have no AI, player is handled externally.
        if self.is_player or self.is_prop:
            return False
        # Only tick AI when within simulation distance.
        if not distance_within(self.rect.center, player.rect.center, 32 * 12.5):
            return False
        # Clip LOS.
        for t in tile_objs:
            if t.rect.clipline(self.rect.center, player.rect.center):
                return False
        # Fire at player.
        if distance_within(self.rect.center, player.rect.center, 32 * 2.5):
            if self.id in (MobID.BOMB, MobID.BOMB_T):
                explosion(tile_objs, mob_objs, self.rect.center, 32 * 3, 20)
                self.kill()
            else:
                self.fire_weapon(player.rect.center, bullets)
            return True  # Don't move, just shoot.
        # Chase and fire at player.
        if not self.is_turret:
            vel = (pg.Vector2(player.rect.center) - self.rect.center).normalize() * dt * mob_speed.get(self.id, 0)
            self.pos.x += vel.x
            self.update_rect()
            if pg.sprite.spritecollideany(self, tile_objs):
                self.pos.x -= vel.x
                self.update_rect()
            mob_objs.remove(self)
            if pg.sprite.spritecollideany(self, mob_objs):
                self.pos.x -= vel.x
                self.update_rect()
            mob_objs.add(self)
            self.pos.y += vel.y
            self.update_rect()
            if pg.sprite.spritecollideany(self, tile_objs):
                self.pos.y -= vel.y
                self.update_rect()
            mob_objs.remove(self)
            if pg.sprite.spritecollideany(self, mob_objs):
                self.pos.y -= vel.y
                self.update_rect()
            mob_objs.add(self)
        if self.id not in (MobID.BOMB, MobID.BOMB_T):
            self.fire_weapon(player.rect.center, bullets)
        return True

