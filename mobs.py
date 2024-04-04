from enum import Enum, auto
import random

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
    PROTOTYPE = auto()

    MINIGUN_T = auto()
    SHOTGUN_T = auto()
    CANNON_T = auto()
    FLAME_T = auto()
    ROCKET_T = auto()
    BOMB_T = auto()
    RICOCHET_T = auto()

    CRATE = auto()
    BARREL = auto()
    AMMO_CRATE = auto()
    SPEED_CRATE = auto()
    COOL_CRATE = auto()
    MAX_HEAT_CRATE = auto()
    MINIGUN_C = auto()
    SHOTGUN_C = auto()
    RICOCHET_C = auto()
    CANNON_C = auto()
    FLAME_C = auto()
    ROCKET_C = auto()


char_to_mob_id = {
    "@": MobID.PLAYER,
    "P": MobID.PROTOTYPE,
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
    "!": MobID.AMMO_CRATE,
    ">": MobID.SPEED_CRATE,
    "*": MobID.COOL_CRATE,
    "$": MobID.MAX_HEAT_CRATE,
    "1": MobID.MINIGUN_C,
    "2": MobID.SHOTGUN_C,
    "3": MobID.RICOCHET_C,
    "4": MobID.CANNON_C,
    "5": MobID.FLAME_C,
    "6": MobID.ROCKET_C,
}

mob_health = {  # Crates and barrels have default health 20.
    MobID.PLAYER: 100,
    MobID.PROTOTYPE: 300,
    MobID.MINIGUN: 50,
    MobID.SHOTGUN: 50,
    MobID.CANNON: 75,
    MobID.FLAME: 50,
    MobID.ROCKET: 75,
    MobID.RICOCHET: 60,
    MobID.BOMB: 75,

    MobID.MINIGUN_C: 50,
    MobID.SHOTGUN_C: 50,
    MobID.CANNON_C: 50,
    MobID.FLAME_C: 50,
    MobID.ROCKET_C: 50,
    MobID.RICOCHET_C: 50,

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
    MobID.CANNON: 50,
    MobID.FLAME: 40,
    MobID.ROCKET: 50,
    MobID.BOMB: 120,
    MobID.PROTOTYPE: 95,
    MobID.RICOCHET: 60,
}

mob_images = {
    MobID.PLAYER: images.ImageID.PLAYER,
    MobID.PROTOTYPE: images.ImageID.PLAYER,
    MobID.MINIGUN: images.ImageID.MINIGUN,
    MobID.SHOTGUN: images.ImageID.SHOTGUN,
    MobID.CANNON: images.ImageID.CANNON,
    MobID.FLAME: images.ImageID.FLAME,
    MobID.ROCKET: images.ImageID.ROCKET,
    MobID.BOMB: images.ImageID.BOMB,
    MobID.CRATE: images.ImageID.CRATE,
    MobID.AMMO_CRATE: images.ImageID.CRATE,
    MobID.SPEED_CRATE: images.ImageID.CRATE,
    MobID.COOL_CRATE: images.ImageID.CRATE,
    MobID.MAX_HEAT_CRATE: images.ImageID.CRATE,
    MobID.BARREL: images.ImageID.BARREL,
    MobID.RICOCHET: images.ImageID.RICOCHET,
    MobID.RICOCHET_T: images.ImageID.RICOCHET_T,
    MobID.MINIGUN_T: images.ImageID.MINIGUN_T,
    MobID.SHOTGUN_T: images.ImageID.SHOTGUN_T,
    MobID.CANNON_T: images.ImageID.CANNON_T,
    MobID.FLAME_T: images.ImageID.FLAME_T,
    MobID.ROCKET_T: images.ImageID.ROCKET_T,
    MobID.BOMB_T: images.ImageID.BOMB_T,
    MobID.RICOCHET_C: images.ImageID.WEAPON_CRATE,
    MobID.MINIGUN_C: images.ImageID.WEAPON_CRATE,
    MobID.SHOTGUN_C: images.ImageID.WEAPON_CRATE,
    MobID.CANNON_C: images.ImageID.WEAPON_CRATE,
    MobID.FLAME_C: images.ImageID.WEAPON_CRATE,
    MobID.ROCKET_C: images.ImageID.WEAPON_CRATE,
}

mob_names = {
    MobID.PLAYER: "PROTOTYPE",
    MobID.PROTOTYPE: "PROTOTYPE",
    MobID.MINIGUN: "MINIGUN TANK",
    MobID.SHOTGUN: "SHOTGUN TANK",
    MobID.RICOCHET: "RICOCHET TANK",
    MobID.CANNON: "CANNON TANK",
    MobID.FLAME: "FLAME TANK",
    MobID.ROCKET: "ROCKET TANK",
    MobID.BOMB: "MOBILE BOMB",
    MobID.CRATE: "CRATE",
    MobID.AMMO_CRATE: "CRATE",
    MobID.SPEED_CRATE: "CRATE",
    MobID.COOL_CRATE: "CRATE",
    MobID.MAX_HEAT_CRATE: "CRATE",
    MobID.BARREL: "TNT",
    MobID.MINIGUN_T: "MINIGUN TURRET",
    MobID.SHOTGUN_T: "SHOTGUN TURRET",
    MobID.RICOCHET_T: "RICOCHET TURRET",
    MobID.CANNON_T: "CANNON TURRET",
    MobID.FLAME_T: "FLAME TURRET",
    MobID.ROCKET_T: "ROCKET TURRET",
    MobID.BOMB_T: "PROXIMITY MINE",
    MobID.RICOCHET_C: "WEAPON CRATE",
    MobID.MINIGUN_C: "WEAPON CRATE",
    MobID.SHOTGUN_C: "WEAPON CRATE",
    MobID.CANNON_C: "WEAPON CRATE",
    MobID.FLAME_C: "WEAPON CRATE",
    MobID.ROCKET_C: "WEAPON CRATE",
}

mob_weapon = {
    MobID.PLAYER: WeaponID.MINIGUN,
    MobID.MINIGUN: WeaponID.MINIGUN,
    MobID.SHOTGUN: WeaponID.SHOTGUN,
    MobID.RICOCHET: WeaponID.RICOCHET,
    MobID.CANNON: WeaponID.CANNON,
    MobID.FLAME: WeaponID.FLAME,
    MobID.ROCKET: WeaponID.ROCKET,
    MobID.MINIGUN_T: WeaponID.MINIGUN,
    MobID.SHOTGUN_T: WeaponID.SHOTGUN,
    MobID.RICOCHET_T: WeaponID.RICOCHET,
    MobID.CANNON_T: WeaponID.CANNON,
    MobID.FLAME_T: WeaponID.FLAME,
    MobID.ROCKET_T: WeaponID.ROCKET,
    MobID.MINIGUN_C: WeaponID.MINIGUN,
    MobID.SHOTGUN_C: WeaponID.SHOTGUN,
    MobID.RICOCHET_C: WeaponID.RICOCHET,
    MobID.CANNON_C: WeaponID.CANNON,
    MobID.FLAME_C: WeaponID.FLAME,
    MobID.ROCKET_C: WeaponID.ROCKET,
}


class Mob(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], mob_id: str):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos[0] + 4, pos[1] + 4)
        self.id = char_to_mob_id[mob_id]
        self.is_player = self.id is MobID.PLAYER
        self.is_barrel = self.id is MobID.BARREL
        self.is_prop = self.id in (MobID.BARREL, MobID.CRATE, MobID.AMMO_CRATE, MobID.COOL_CRATE,
                                   MobID.SPEED_CRATE, MobID.MAX_HEAT_CRATE, MobID.MINIGUN_C, MobID.SHOTGUN_C,
                                   MobID.RICOCHET_C, MobID.CANNON_C, MobID.FLAME_C, MobID.ROCKET_C)
        self.is_w_crate = self.id in (MobID.MINIGUN_C, MobID.SHOTGUN_C, MobID.RICOCHET_C, MobID.CANNON_C,
                                      MobID.FLAME_C, MobID.ROCKET_C)
        self.is_ammo = self.id is MobID.AMMO_CRATE
        self.is_speed = self.id is MobID.SPEED_CRATE
        self.is_cool = self.id is MobID.COOL_CRATE
        self.is_heat = self.id is MobID.MAX_HEAT_CRATE
        self.weapon = mob_weapon.get(self.id, None)
        self.max_heat = mob_health.get(self.id, 20)
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
               mob_objs: pg.sprite.Group, player: pg.sprite.Sprite, bullets: pg.sprite.Group,
               pgp: pg.sprite.Group | None = None) -> bool:
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
        # Choose random weapon.
        if self.id is MobID.PROTOTYPE:
            self.weapon = random.choice(tuple(weapons.WeaponID))
        # Fire at player.
        if distance_within(self.rect.center, player.rect.center, 32 * 2.5):
            if self.id in (MobID.BOMB, MobID.BOMB_T):
                explosion(tile_objs, mob_objs, self.rect.center, 32 * 3, 20, pgp)
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

